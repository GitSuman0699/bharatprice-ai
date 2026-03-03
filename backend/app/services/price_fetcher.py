"""
Real Price Fetcher for BharatPrice AI.
Fetches actual commodity prices from:
  1. data.gov.in AGMARKNET API — real daily mandi (wholesale) prices
  2. BigBasket — scraped retail prices
  3. JioMart — scraped retail prices
Falls back to estimated retail prices from wholesale data when scraping fails.
"""

import logging
import os
import time
from datetime import datetime
from typing import Optional

import httpx

from app.data.product_mapping import (
    resolve_product_id,
    get_commodity_name,
    get_retail_markup,
    get_online_markup,
    PRODUCT_TO_COMMODITY,
)
logger = logging.getLogger(__name__)

# ─── Configuration ─────────────────────────────────────────────────

DATA_GOV_API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
# Public demo API key — works for prototype; replace with registered key for production
DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY")

BIGBASKET_SEARCH_URL = "https://www.bigbasket.com/listing-svc/v2/products"


# ─── In-memory Cache ───────────────────────────────────────────────

_price_cache: dict[str, dict] = {}
CACHE_TTL = 3600  # 1 hour


def _cache_key(commodity: str, state: str, district: str = "") -> str:
    return f"{commodity}:{state}:{district}".lower()


def _get_cached(key: str) -> dict | None:
    if key in _price_cache:
        entry = _price_cache[key]
        if time.time() - entry["timestamp"] < CACHE_TTL:
            return entry["data"]
        del _price_cache[key]
    return None


def _set_cache(key: str, data: dict):
    _price_cache[key] = {"data": data, "timestamp": time.time()}


# ─── data.gov.in API ──────────────────────────────────────────────

def fetch_mandi_prices(
    commodity: str,
    state: str = "",
    district: str = "",
    limit: int = 1,
) -> list[dict]:
    """
    Fetch real daily mandi prices from data.gov.in AGMARKNET API.

    Args:
        commodity: Commodity name (e.g., "Tomato", "Onion")
        state: State filter (e.g., "Maharashtra", "Delhi")
        district: District filter (e.g., "Pune", "New Delhi")
        limit: Max records to return

    Returns:
        List of price records with fields:
            state, district, market, commodity, variety, grade,
            arrival_date, min_price, max_price, modal_price (all in ₹/quintal)
    """
    cache_key = _cache_key(commodity, state, district)
    cached = _get_cached(cache_key)
    if cached:
        logger.info(f"Cache hit for {cache_key}")
        return cached

    params = {
        "api-key": DATA_GOV_API_KEY,
        "format": "json",
        "limit": str(limit),
        "filters[commodity]": commodity,
    }

    if state:
        params["filters[state]"] = state
    if district:
        params["filters[district]"] = district

    try:
        with httpx.Client(timeout=25) as client:
            response = client.get(DATA_GOV_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            records = data.get("records", [])
            if records:
                _set_cache(cache_key, records)
                logger.info(
                    f"Fetched {len(records)} mandi prices for {commodity} "
                    f"in {state or 'all states'}"
                )
            else:
                logger.warning(f"No mandi data for {commodity} in {state}/{district}")

            return records

    except httpx.HTTPStatusError as e:
        logger.error(f"data.gov.in API error: {e.response.status_code}")
        return []
    except Exception as e:
        logger.error(f"data.gov.in API failed: {e}")
        return []


def _quintal_to_kg(price_per_quintal: float) -> float:
    """Convert ₹/quintal to ₹/kg (1 quintal = 100 kg)."""
    return round(price_per_quintal / 100, 2)


# ─── BigBasket Scraper (via scraper.py) ────────────────────────────

def scrape_bigbasket_price(product_id: str) -> dict | None:
    """
    Get real BigBasket prices using the in-house scraper.
    Returns: {source, price, mrp, unit, is_scraped} or None
    """
    try:
        from app.services.scraper import scrape_product_price

        result = scrape_product_price(product_id)
        if result and result.bigbasket_price:
            return {
                "source": "BigBasket",
                "price": result.bigbasket_price,
                "mrp": result.bigbasket_mrp or result.bigbasket_price,
                "unit": "per kg",
                "weight": result.bigbasket_weight,
                "discount": result.bigbasket_discount,
                "is_scraped": True,
                "jiomart_est": result.jiomart_price,
                "local_est": result.local_market_price,
            }
    except Exception as e:
        logger.warning(f"BigBasket scraper failed for {product_id}: {type(e).__name__}: {e}")

    return None



# ─── Main Price Fetcher ────────────────────────────────────────────

def get_real_price(
    query: str,
    pincode: str = "110001",
    state: str | None = None,
    district: str | None = None,
    city: str | None = None,
) -> dict | None:
    """
    Get real prices for a product using GPS-provided state/district.
    Combines data.gov.in mandi prices with scraped retail prices.

    Returns:
        {
            product_name, commodity, pincode, city, state, district,
            mandi_price, mandi_min, mandi_max,     (₹/kg, from data.gov.in)
            bigbasket_price,                         (₹/kg, scraped or estimated)
            jiomart_price,                           (₹/kg, scraped or estimated)
            local_avg,                               (₹/kg, estimated retail)
            recommended_retail,                      (₹/kg, our recommendation)
            unit, arrival_date, market,
            data_source, is_real_data
        }
    """
    # Step 1: Resolve product query → product ID → commodity name
    product_id = resolve_product_id(query)
    if not product_id:
        logger.warning(f"Could not resolve product: {query}")
        return None

    commodity = get_commodity_name(product_id)
    if not commodity:
        logger.warning(f"No commodity mapping for: {product_id}")
        return None

    # Step 2: Use GPS-provided state, district, city (from frontend Nominatim)
    state = state or "Delhi"
    district = district or "New Delhi"
    city = city or district

    # Step 3: Fetch real mandi prices from data.gov.in
    mandi_records = fetch_mandi_prices(commodity, state=state)

    # If no data for this state, try without state filter (nationwide)
    if not mandi_records:
        mandi_records = fetch_mandi_prices(commodity, limit=50)

    mandi_price_per_kg = None
    mandi_min_per_kg = None
    mandi_max_per_kg = None
    arrival_date = None
    market_name = None
    data_source = "data.gov.in (AGMARKNET)"
    is_real = False

    if mandi_records:
        is_real = True

        # Try to find the closest market (same district first)
        best_record = None
        for record in mandi_records:
            if record.get("district", "").lower() == district.lower():
                best_record = record
                break

        # If no district match, use first record (closest state match)
        if not best_record:
            best_record = mandi_records[0]

        # Convert ₹/quintal → ₹/kg
        mandi_price_per_kg = _quintal_to_kg(best_record.get("modal_price", 0))
        mandi_min_per_kg = _quintal_to_kg(best_record.get("min_price", 0))
        mandi_max_per_kg = _quintal_to_kg(best_record.get("max_price", 0))
        arrival_date = best_record.get("arrival_date", "")
        market_name = best_record.get("market", "")
        data_source = f"data.gov.in — {best_record.get('market', 'Mandi')}"

    # Step 4: Try scraping BigBasket for real retail prices
    # The scraper returns BigBasket price + JioMart/local estimates
    bb_data = scrape_bigbasket_price(product_id)

    # Step 5: Calculate prices
    if mandi_price_per_kg and mandi_price_per_kg > 0:
        base_mandi = mandi_price_per_kg
    else:
        # Fallback: use a reasonable default (will be overridden by seed data in caller)
        return None

    markup = get_retail_markup(product_id)
    online_markup = get_online_markup(product_id)

    # Use scraped prices if available, otherwise estimate from mandi
    if bb_data:
        bigbasket_price = bb_data["price"]
        jiomart_price = bb_data.get("jiomart_est") or round(bigbasket_price * 0.95, 2)
        local_avg = bb_data.get("local_est") or round(bigbasket_price * 0.90, 2)
        data_source += " + BigBasket (scraped)"
    else:
        bigbasket_price = round(base_mandi * online_markup["bigbasket"], 2)
        jiomart_price = round(base_mandi * online_markup["jiomart"], 2)
        local_avg = round(base_mandi * markup, 2)

    # Sanity check: Retail prices cannot physically be lower than Mandi wholesale
    # (This happens when scrapers accidentally pull a 250g pack price)
    if bigbasket_price <= base_mandi:
        bigbasket_price = round(base_mandi * online_markup["bigbasket"], 2)
        jiomart_price = round(base_mandi * online_markup["jiomart"], 2)
        local_avg = round(base_mandi * markup, 2)
        data_source = data_source.replace(" + BigBasket (scraped)", " + Overridden Scatter")

    # Recommended retail: slightly above mandi, competitive with online
    recommended_retail = round(
        min(local_avg, bigbasket_price, jiomart_price) * 0.97, 2
    )

    # Final safety clamp: Must guarantee a positive profit margin over wholesale
    if recommended_retail <= base_mandi:
        recommended_retail = round(base_mandi * 1.15, 2)

    # Determine demand trend from price range
    if mandi_max_per_kg and mandi_min_per_kg:
        spread = (mandi_max_per_kg - mandi_min_per_kg) / mandi_min_per_kg if mandi_min_per_kg > 0 else 0
        if spread > 0.3:
            demand_trend = "rising"
        elif spread < 0.1:
            demand_trend = "stable"
        else:
            demand_trend = "moderate"
    else:
        demand_trend = "stable"

    return {
        "product_id": product_id,
        "product_name": commodity,
        "commodity": commodity,
        "pincode": pincode,
        "city": city,
        "state": state,
        "district": district,
        "mandi_price": base_mandi,
        "mandi_min": mandi_min_per_kg,
        "mandi_max": mandi_max_per_kg,
        "bigbasket_price": bigbasket_price,
        "jiomart_price": jiomart_price,
        "local_avg": local_avg,
        "recommended_retail": recommended_retail,
        "unit": "/kg",
        "arrival_date": arrival_date,
        "market": market_name,
        "demand_trend": demand_trend,
        "data_source": data_source,
        "is_real_data": is_real,
        "bigbasket_scraped": bb_data is not None,
    }


def get_real_mandi_rates(
    query: str,
    pincode: str = "110001",
    limit: int = 10,
    state: str | None = None,
    district: str | None = None,
) -> list[dict]:
    """
    Get real mandi rates from multiple markets using GPS params.

    Returns list of:
        {mandi_name, state, district, min_price, max_price, modal_price, arrival_date, unit}
    """
    product_id = resolve_product_id(query)
    if not product_id:
        return []

    commodity = get_commodity_name(product_id)
    if not commodity:
        return []

    records = fetch_mandi_prices(commodity, state=state, limit=limit)

    # If too few results in state, add nationwide
    if len(records) < 3:
        nationwide = fetch_mandi_prices(commodity, limit=limit)
        # Deduplicate
        seen = {r.get("market", "") for r in records}
        for r in nationwide:
            if r.get("market", "") not in seen:
                records.append(r)
                seen.add(r.get("market", ""))
            if len(records) >= limit:
                break

    return [
        {
            "mandi_name": r.get("market", "Unknown"),
            "state": r.get("state", ""),
            "district": r.get("district", ""),
            "min_price": _quintal_to_kg(r.get("min_price", 0)),
            "max_price": _quintal_to_kg(r.get("max_price", 0)),
            "modal_price": _quintal_to_kg(r.get("modal_price", 0)),
            "arrival_date": r.get("arrival_date", ""),
            "commodity": r.get("commodity", commodity),
            "variety": r.get("variety", ""),
            "unit": "/kg",
        }
        for r in records
    ]


