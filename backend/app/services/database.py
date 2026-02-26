"""
Database service for BharatPrice AI.
Uses real data from data.gov.in API when available, falls back to seed data.
"""

import logging
from datetime import datetime, timedelta

from app.data.seed_data import (
    generate_price_record,
    generate_mandi_rates,
    find_product_id,
    PRODUCTS,
    REGIONS,
    get_product_list,
)
from app.data.pincode_data import lookup_pincode, get_city_name
from app.models.schemas import PriceData, MandiRate, PriceTrend, UserProfile
from app.services.price_fetcher import get_real_price, get_real_mandi_rates

logger = logging.getLogger(__name__)


# ─── In-memory user store (prototype) ─────────────────────────────

_users: dict[str, dict] = {}


# ─── User Operations ──────────────────────────────────────────────

def create_user(user_id: str, profile: dict) -> UserProfile:
    """Create a new user profile."""
    _users[user_id] = {**profile, "user_id": user_id}
    return UserProfile(**_users[user_id])


def get_user(user_id: str) -> UserProfile | None:
    """Get user profile by ID."""
    if user_id in _users:
        return UserProfile(**_users[user_id])
    return None


def update_user(user_id: str, updates: dict) -> UserProfile | None:
    """Update user profile."""
    if user_id in _users:
        _users[user_id].update(updates)
        return UserProfile(**_users[user_id])
    return None


# ─── Price Queries (with real data) ────────────────────────────────

def get_current_price(product_query: str, region: str = "delhi", pincode: str | None = None) -> PriceData | None:
    """
    Get today's price for a product.
    Uses real data.gov.in API when pincode is provided, falls back to seed data.
    """
    # Try real data first if pincode is available
    if pincode:
        real_data = get_real_price(product_query, pincode)
        if real_data:
            location = lookup_pincode(pincode)
            logger.info(
                f"Real price for {product_query} in {location['city']}: "
                f"₹{real_data['mandi_price']}/kg (mandi), "
                f"₹{real_data['local_avg']}/kg (retail)"
            )
            return PriceData(
                product_id=real_data["product_id"],
                product_name=real_data["product_name"],
                date=real_data.get("arrival_date", datetime.now().strftime("%d/%m/%Y")),
                region=real_data["city"],
                mandi_price=real_data["mandi_price"],
                bigbasket_price=real_data["bigbasket_price"],
                jiomart_price=real_data["jiomart_price"],
                local_avg=real_data["local_avg"],
                recommended_retail=real_data["recommended_retail"],
                demand_trend=real_data["demand_trend"],
                unit=real_data["unit"],
            )

    # Fallback to seed data
    product_id = find_product_id(product_query)
    if not product_id:
        return None

    if region not in REGIONS:
        region = "delhi"

    record = generate_price_record(product_id, region, datetime.now())
    return PriceData(
        product_id=record["product_id"],
        product_name=record["product_name"],
        date=record["date"],
        region=record["region"],
        mandi_price=record["mandi_price"],
        bigbasket_price=record["bigbasket_price"],
        jiomart_price=record["jiomart_price"],
        local_avg=record["local_avg"],
        recommended_retail=record["recommended_retail"],
        demand_trend=record["demand_trend"],
        unit=record["unit"],
    )


def get_competitor_prices(product_query: str, region: str = "delhi", pincode: str | None = None) -> dict | None:
    """Get competitor price comparison. Uses real data when available."""
    # Try real data first
    if pincode:
        real_data = get_real_price(product_query, pincode)
        if real_data:
            city = real_data["city"]
            prices = [
                {
                    "source": f"🏪 Mandi ({real_data.get('market', 'Wholesale')})",
                    "price": real_data["mandi_price"],
                    "is_real": True,
                },
                {
                    "source": "🛒 BigBasket",
                    "price": real_data["bigbasket_price"],
                    "is_real": real_data.get("bigbasket_scraped", False),
                },
                {
                    "source": "🛍️ JioMart",
                    "price": real_data["jiomart_price"],
                    "is_real": real_data.get("jiomart_scraped", False),
                },
                {
                    "source": "📊 Local Avg",
                    "price": real_data["local_avg"],
                    "is_real": False,
                },
                {
                    "source": "✅ Recommended",
                    "price": real_data["recommended_retail"],
                    "is_real": False,
                },
            ]
            return {
                "product_name": real_data["product_name"],
                "region": city,
                "unit": real_data["unit"],
                "prices": prices,
                "demand_trend": real_data["demand_trend"],
                "data_source": real_data.get("data_source", "data.gov.in"),
                "is_real_data": True,
            }

    # Fallback to seed data
    product_id = find_product_id(product_query)
    if not product_id:
        return None

    if region not in REGIONS:
        region = "delhi"

    record = generate_price_record(product_id, region, datetime.now())
    return {
        "product_name": record["product_name"],
        "region": REGIONS[region]["city"],
        "unit": record["unit"],
        "prices": [
            {"source": "Mandi (Wholesale)", "price": record["mandi_price"]},
            {"source": "BigBasket", "price": record["bigbasket_price"]},
            {"source": "JioMart", "price": record["jiomart_price"]},
            {"source": "Local Average", "price": record["local_avg"]},
            {"source": "✅ Recommended Retail", "price": record["recommended_retail"]},
        ],
        "demand_trend": record["demand_trend"],
        "is_real_data": False,
    }


def get_mandi_rates(product_query: str, region: str = "delhi", pincode: str | None = None) -> list[MandiRate]:
    """Get mandi rates. Uses real data.gov.in API when pincode is available."""
    # Try real data first
    if pincode:
        real_rates = get_real_mandi_rates(product_query, pincode)
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
