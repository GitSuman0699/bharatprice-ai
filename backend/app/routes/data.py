"""Data query API routes."""

from fastapi import APIRouter, Query
from app.services.database import (
    get_current_price,
    get_competitor_prices,
    get_mandi_rates,
    get_price_trend,
    get_all_products,
    get_available_regions,
    search_products,
)

router = APIRouter(prefix="/api", tags=["data"])


@router.get("/prices/{product}")
async def get_price(product: str, region: str = Query(default="delhi")):
    """Get current price for a product."""
    price = get_current_price(product, region)
    if not price:
        return {"error": f"Product '{product}' not found"}
    return price


@router.get("/compare/{product}")
async def compare_prices(product: str, region: str = Query(default="delhi")):
    """Get competitor price comparison."""
    comparison = get_competitor_prices(product, region)
    if not comparison:
        return {"error": f"Product '{product}' not found"}
    return comparison


@router.get("/mandi/{product}")
async def mandi_rates(product: str, region: str = Query(default="delhi")):
    """Get mandi wholesale rates."""
    rates = get_mandi_rates(product, region)
    if not rates:
        return {"error": f"Product '{product}' not found"}
    return rates


@router.get("/trends/{product}")
async def price_trends(
    product: str,
    region: str = Query(default="delhi"),
    days: int = Query(default=30, ge=7, le=90),
):
    """Get price trend analysis."""
    trend = get_price_trend(product, region, days)
    if not trend:
        return {"error": f"Product '{product}' not found"}
    return trend


@router.get("/products")
async def list_products():
    """List all available products."""
    return {"products": get_all_products()}


@router.get("/products/search")
async def search(q: str = Query(...)):
    """Search products by name."""
    return {"results": search_products(q)}


@router.get("/regions")
async def list_regions():
    """List available regions."""
    return {"regions": get_available_regions()}
