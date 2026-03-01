"""
Database service for BharatPrice AI.
Uses real data from data.gov.in API when available, falls back to seed data.
"""

import logging
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

import boto3
from botocore.exceptions import ClientError

from app.data.seed_data import (
    generate_price_record,
    generate_mandi_rates,
    find_product_id,
    PRODUCTS,
    REGIONS,
    get_product_list,
)
from app.models.schemas import PriceData, MandiRate, PriceTrend, UserProfile
from app.services.price_fetcher import get_real_price, get_real_mandi_rates
from app.data.product_mapping import is_mandi_product

logger = logging.getLogger(__name__)


# ─── DynamoDB Configuration ──────────────────────────────────────

DYNAMODB_AVAILABLE = True
try:
    dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'ap-south-1'))
    users_table = dynamodb.Table('BharatPriceUsers')
    market_table = dynamodb.Table('BharatPriceMarketData')
except Exception as e:
    logger.error(f"Failed to initialize DynamoDB: {e}")
    DYNAMODB_AVAILABLE = False


# ─── User Operations ──────────────────────────────────────────────

def create_user(user_id: str, profile: dict) -> UserProfile | None:
    """Create a new user profile in DynamoDB."""
    if not DYNAMODB_AVAILABLE:
        logger.error("DynamoDB not available.")
        return None

    item = {**profile, "user_id": user_id}
    try:
        users_table.put_item(Item=item)
        return UserProfile(**item)
    except ClientError as e:
        logger.error(f"Error creating user in DynamoDB: {e}")
        return None

def get_user(user_id: str) -> UserProfile | None:
    """Get user profile by ID from DynamoDB."""
    if not DYNAMODB_AVAILABLE:
        return None

    try:
        response = users_table.get_item(Key={'user_id': user_id})
        item = response.get('Item')
        if item:
            return UserProfile(**item)
        return None
    except ClientError as e:
        logger.error(f"Error getting user from DynamoDB: {e}")
        return None

def update_user(user_id: str, updates: dict) -> UserProfile | None:
    """Update user profile in DynamoDB."""
    if not DYNAMODB_AVAILABLE:
        return None

    try:
        # Construct update expression
        update_expr = "set "
        expr_attr_values = {}
        expr_attr_names = {}
        
        for k, v in updates.items():
            update_expr += f"#{k} = :{k}, "
            expr_attr_values[f":{k}"] = v
            expr_attr_names[f"#{k}"] = k
            
        update_expr = update_expr.rstrip(", ")

        response = users_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_attr_values,
            ExpressionAttributeNames=expr_attr_names,
            ReturnValues="ALL_NEW"
        )
        return UserProfile(**response.get('Attributes', {}))
    except ClientError as e:
        logger.error(f"Error updating user in DynamoDB: {e}")
        return None


# ─── Price Queries (with real data) ────────────────────────────────

def get_current_price(product_query: str, region: str = "delhi", pincode: str | None = None, state: str | None = None, district: str | None = None) -> PriceData | None:
    """
    Get today's price for a product.
    Implemented with Cache-Aside Pattern using DynamoDB TTL.
    """
    product_id = find_product_id(product_query)
    if not product_id:
        return None

    # Determine region key — use the custom city name sent from frontend (e.g. "Siliguri")
    cache_region = region
    
    # 1. Check DynamoDB Cache
    if DYNAMODB_AVAILABLE:
        try:
            response = market_table.get_item(Key={'product_id': product_id, 'region': cache_region})
            item = response.get('Item')
            
            # Cache Hit: Ensure it hasn't expired (DynamoDB TTL deletion is inexact)
            if item and int(item.get('expiration_time', 0)) > int(datetime.now().timestamp()):
                logger.info(f"CACHE HIT: Returning {product_id} in {cache_region} from DynamoDB.")
                # We pop internal keys to match schema
                item.pop('expiration_time', None)
                item.pop('product_id', None)
                item.pop('region', None)
                
                return PriceData(
                    product_id=product_id,
                    region=cache_region,
                    **item
                )
        except ClientError as e:
            logger.error(f"DynamoDB cache read failed: {e}")

    # 2. Cache Miss: Fetch Real Data
    logger.info(f"CACHE MISS: Fetching fresh data for {product_id} in {cache_region}...")
    logger.info(f"GPS PARAMS: state={state}, district={district}, pincode={pincode}, region={region}")
    final_data = None
    
    if state and district:
        real_data = get_real_price(product_query, pincode or "110001", state=state, district=district, city=district)
        if real_data:
            final_data = {
                "product_name": real_data["product_name"],
                "date": real_data.get("arrival_date", datetime.now().strftime("%d/%m/%Y")),
                "mandi_price": real_data["mandi_price"],
                "bigbasket_price": real_data["bigbasket_price"],
                "jiomart_price": real_data["jiomart_price"],
                "local_avg": real_data["local_avg"],
                "recommended_retail": real_data["recommended_retail"],
                "demand_trend": real_data["demand_trend"],
                "unit": real_data["unit"],
            }

    # Fallback to seed if real data failed or pincode missing
    if not final_data:
        if region not in REGIONS:
            region = "delhi"
        record = generate_price_record(product_id, region, datetime.now())
        final_data = {
            "product_name": record["product_name"],
            "date": record["date"],
            "mandi_price": float(record["mandi_price"]),
            "bigbasket_price": float(record["bigbasket_price"]),
            "jiomart_price": float(record["jiomart_price"]),
            "local_avg": float(record["local_avg"]),
            "recommended_retail": float(record["recommended_retail"]),
            "demand_trend": record["demand_trend"],
            "unit": record["unit"],
        }

    # 3. Write back to Cache (TTL exactly 24 hours from now)
    if DYNAMODB_AVAILABLE and final_data:
        try:
            expiration_epoch = int((datetime.now() + timedelta(hours=24)).timestamp())
            
            # Serialize floats to Decimals for DynamoDB
            import decimal
            dynamo_item = json.loads(json.dumps(final_data), parse_float=decimal.Decimal)
            
            market_table.put_item(Item={
                'product_id': product_id,
                'region': cache_region,
                'expiration_time': expiration_epoch,
                **dynamo_item
            })
            logger.info(f"CACHE WRITE: Saved {product_id} in {cache_region} to DynamoDB (TTL 24h).")
        except Exception as e:
            logger.error(f"DynamoDB cache write failed: {e}")

    # Return structured Pydantic object
    return PriceData(
        product_id=product_id,
        region=cache_region,
        **final_data
    )


def get_competitor_prices(product_query: str, region: str = "delhi", pincode: str | None = None, state: str | None = None, district: str | None = None) -> dict | None:
    """Get competitor price comparison. Leverages the cached get_current_price architecture."""
    # This automatically handles DynamoDB TTL caching and data.gov.in fetching
    price_data = get_current_price(product_query, region, pincode, state=state, district=district)
    
    if not price_data:
        return None

    prices = []

    # Only include mandi price for products actually traded in mandis
    product_id = find_product_id(product_query)
    if product_id and is_mandi_product(product_id) and price_data.mandi_price > 0:
        prices.append({
            "source": "🏪 Mandi (Wholesale)",
            "price": price_data.mandi_price,
            "is_real": True,
        })

    prices.extend([
        {
            "source": "🛒 BigBasket",
            "price": price_data.bigbasket_price,
            "is_real": True,
        },
        {
            "source": "🛍️ JioMart",
            "price": price_data.jiomart_price,
            "is_real": True,
        },
        {
            "source": "📊 Local Avg",
            "price": price_data.local_avg,
            "is_real": True,
        },
        {
            "source": "✅ Recommended",
            "price": price_data.recommended_retail,
            "is_real": True,
        },
    ])

    return {
        "product_name": price_data.product_name,
        "region": price_data.region,
        "unit": price_data.unit,
        "prices": prices,
        "demand_trend": price_data.demand_trend,
        "data_source": "DynamoDB Cache / data.gov.in",
        "is_real_data": True,
    }


def get_mandi_rates(product_query: str, region: str = "delhi", pincode: str | None = None, state: str | None = None, district: str | None = None) -> list[MandiRate]:
    """Get mandi rates. Uses real data.gov.in API when location is available."""
    # Non-mandi products (dairy, eggs/meat, FMCG) are not traded in mandis
    product_id = find_product_id(product_query)
    if product_id and not is_mandi_product(product_id):
        logger.info(f"Skipping mandi rates for non-mandi product: {product_id}")
        return []

    # Try real data first
    if state and district:
        real_rates = get_real_mandi_rates(product_query, pincode=pincode, state=state, district=district)
        if real_rates:
            logger.info(f"Got {len(real_rates)} real mandi rates for {product_query}")
            return [
                MandiRate(
                    mandi_name=r["mandi_name"],
                    location=f"{r['district']}, {r['state']}",
                    price=r["modal_price"],
                    unit="/kg",
                    date=r.get("arrival_date", ""),
                )
                for r in real_rates
            ]

    # Fallback to seed data
    product_id = find_product_id(product_query)
    if not product_id:
        return []

    if region not in REGIONS:
        region = "delhi"

    rates = generate_mandi_rates(product_id, region, datetime.now())
    return [MandiRate(**r) for r in rates]


def get_price_trend(product_query: str, region: str = "delhi", days: int = 30) -> PriceTrend | None:
    """Get price trend for a product over N days. Uses seed data (historical trends)."""
    product_id = find_product_id(product_query)
    if not product_id:
        return None

    if region not in REGIONS:
        region = "delhi"

    today = datetime.now()
    data_points = []
    prices = []

    for i in range(days):
        date = today - timedelta(days=i)
        record = generate_price_record(product_id, region, date)
        data_points.append({
            "date": record["date"],
            "price": record["local_avg"],
        })
        prices.append(record["local_avg"])

    current = prices[0]
    oldest = prices[-1]
    change_pct = round(((current - oldest) / oldest) * 100, 1)

    if change_pct > 3:
        trend = "rising"
    elif change_pct < -3:
        trend = "falling"
    else:
        trend = "stable"

    product_name = PRODUCTS[product_id]["name"]
    summary = f"{product_name} is currently ₹{current:.0f} {PRODUCTS[product_id]['unit']} in {REGIONS[region]['city']}. "
    if trend == "rising":
        summary += f"Price has risen {abs(change_pct)}% over the last {days} days. Consider stocking up before further increases."
    elif trend == "falling":
        summary += f"Price has dropped {abs(change_pct)}% over the last {days} days. Good time to wait for further drops before bulk buying."
    else:
        summary += f"Price has been stable (±{abs(change_pct)}%) over the last {days} days."

    return PriceTrend(
        product_name=product_name,
        region=region,
        period_days=days,
        current_price=current,
        price_change_pct=change_pct,
        trend=trend,
        data_points=list(reversed(data_points)),
        summary=summary,
    )


def search_products(query: str) -> list[dict]:
    """Search for products matching a query."""
    query_lower = query.lower()
    results = []
    for pid, product in PRODUCTS.items():
        if (query_lower in product["name"].lower() or
                query_lower in pid.lower() or
                query_lower in product["category"].lower()):
            results.append({"id": pid, "name": product["name"], "category": product["category"]})
    return results[:10]


def get_all_products() -> list[dict]:
    """Return full product catalog."""
    return get_product_list()


def get_available_regions() -> list[dict]:
    """Return available regions."""
    return [
        {"id": rid, "city": r["city"], "mandis": r["mandis"]}
        for rid, r in REGIONS.items()
    ]
