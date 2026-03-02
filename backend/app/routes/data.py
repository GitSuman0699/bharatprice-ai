"""Data query API routes."""

from fastapi import APIRouter, Query, Request
from app.services.database import (
    get_current_price,
    get_competitor_prices,
    get_mandi_rates,
    get_price_trend,
    get_all_products,
    get_available_regions,
    search_products,
)
from app.middleware.rate_limiter import limiter, DATA_LIMIT

router = APIRouter(prefix="/api", tags=["data"])


@router.get("/prices/{product}")
@limiter.limit(DATA_LIMIT)
async def get_price(request: Request, product: str, region: str = Query(default="delhi")):
    """Get current price for a product."""
    price = get_current_price(product, region)
    if not price:
        return {"error": f"Product '{product}' not found"}
    return price


@router.get("/compare/{product}")
@limiter.limit(DATA_LIMIT)
async def compare_prices(request: Request, product: str, region: str = Query(default="delhi")):
    """Get competitor price comparison."""
    comparison = get_competitor_prices(product, region)
    if not comparison:
        return {"error": f"Product '{product}' not found"}
    return comparison


@router.get("/mandi/{product}")
@limiter.limit(DATA_LIMIT)
async def mandi_rates(request: Request, product: str, region: str = Query(default="delhi")):
    """Get mandi wholesale rates."""
    rates = get_mandi_rates(product, region)
    if not rates:
        return {"error": f"Product '{product}' not found"}
    return rates


@router.get("/trends/{product}")
@limiter.limit(DATA_LIMIT)
async def price_trends(
    request: Request,
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
@limiter.limit(DATA_LIMIT)
async def list_products(request: Request):
    """List all available products."""
    return {"products": get_all_products()}


@router.get("/products/search")
@limiter.limit(DATA_LIMIT)
async def search(request: Request, q: str = Query(...)):
    """Search products by name."""
    return {"results": search_products(q)}


@router.get("/regions")
@limiter.limit(DATA_LIMIT)
async def list_regions(request: Request):
    """List available regions."""
    return {"regions": get_available_regions()}
