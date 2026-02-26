"""
In-house price scraper for BharatPrice AI.
Fetches real retail prices from BigBasket using their internal listing API.
"""
import httpx
import time
import re
import logging
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ─── Data models ────────────────────────────────────────────────────

@dataclass
class ScrapedProduct:
    """A single product with pricing data from a retailer."""
    name: str
    brand: str
    sp: float            # selling price
    mrp: float           # maximum retail price
    weight: str          # e.g. "1 kg"
    weight_grams: int    # normalized weight in grams
    unit: str            # "g" or "ml"
    price_per_kg: float  # normalized price per kg
    discount: str        # e.g. "28% OFF"
    category: str        # top-level category
    source: str          # "bigbasket"
    url: str             # product URL


@dataclass
class PriceResult:
    """Aggregated price result for a product."""
    product_name: str
    bigbasket_price: Optional[float] = None
    bigbasket_mrp: Optional[float] = None
    bigbasket_weight: str = ""
    bigbasket_discount: str = ""
    jiomart_price: Optional[float] = None    # estimated from BB
    local_market_price: Optional[float] = None  # estimated from BB
    source: str = "bigbasket"
    products: list = field(default_factory=list)


# ─── BigBasket Scraper ──────────────────────────────────────────────

# BigBasket category slugs for search
BB_CATEGORIES = {
    # Vegetables
    "tomato": "potato-onion-tomato", "onion": "potato-onion-tomato",
    "potato": "potato-onion-tomato",
    "cabbage": "leafy-vegetables", "spinach": "leafy-vegetables",
    "capsicum": "leafy-vegetables", "carrot": "leafy-vegetables",
    "beans": "leafy-vegetables", "peas": "leafy-vegetables",
    "cauliflower": "leafy-vegetables", "brinjal": "leafy-vegetables",
    "lady_finger": "leafy-vegetables", "cucumber": "leafy-vegetables",
    "bitter_gourd": "leafy-vegetables", "bottle_gourd": "leafy-vegetables",
    "green_chilli": "chillies-ginger-garlic", "ginger": "chillies-ginger-garlic",
    "garlic": "chillies-ginger-garlic", "coriander": "herbs-seasonings",
    "lemon": "coriander-curry-leaves", "drumstick": "leafy-vegetables",
    # Fruits
    "apple": "apples-pomegranate", "banana": "banana-sapota-papaya",
    "mango": "mangoes", "grapes": "grapes-berries",
    "orange": "citrus-fruits", "papaya": "banana-sapota-papaya",
    "watermelon": "melons", "pomegranate": "apples-pomegranate",
    "guava": "citrus-fruits", "pineapple": "citrus-fruits",
    # Grains & staples
    "rice": "rice", "wheat": "wheat-flour-atta",
    "atta": "wheat-flour-atta", "atta_5kg": "wheat-flour-atta",
    "atta_10kg": "wheat-flour-atta",
    "sugar": "sugar-jaggery", "dal": "dals-pulses",
    "toor_dal": "dals-pulses", "arhar_dal": "dals-pulses",
    "moong_dal": "dals-pulses", "urad_dal": "dals-pulses",
    "chana_dal": "dals-pulses", "masoor_dal": "dals-pulses",
    # Spices
    "turmeric": "whole-spices", "cumin": "whole-spices",
    "jeera": "whole-spices", "red_chilli": "whole-spices",
    # Oils
    "mustard_oil": "mustard-oil", "coconut_oil": "coconut-oil",
    # Dairy
    "milk": "milk", "ghee": "ghee", "butter": "butter-margarine",
    "curd": "curd", "paneer": "paneer-tofu",
    # Eggs & meat
    "egg": "eggs", "chicken": "poultry",
}

# Search terms mapping: product_id → BigBasket search query
BB_SEARCH_TERMS = {
    "tomato": "tomato", "onion": "onion", "potato": "potato",
    "cabbage": "cabbage", "spinach": "spinach", "capsicum": "capsicum",
    "carrot": "carrot", "beans": "french beans", "peas": "green peas",
    "cauliflower": "cauliflower", "brinjal": "brinjal", "cucumber": "cucumber",
    "lady_finger": "lady finger", "green_chilli": "green chilli",
    "ginger": "ginger", "garlic": "garlic", "coriander": "coriander",
    "lemon": "lemon", "bitter_gourd": "bitter gourd",
    "bottle_gourd": "bottle gourd", "drumstick": "drumstick",
    "apple": "apple", "banana": "banana", "mango": "mango",
    "grapes": "grapes", "orange": "orange", "papaya": "papaya",
    "watermelon": "watermelon", "pomegranate": "pomegranate",
    "guava": "guava", "pineapple": "pineapple",
    "rice": "rice", "wheat": "wheat", "sugar": "sugar",
    "atta": "atta", "atta_5kg": "atta 5kg", "atta_10kg": "atta 10kg",
    "dal": "toor dal", "toor_dal": "toor dal", "arhar_dal": "toor dal",
    "moong_dal": "moong dal", "urad_dal": "urad dal",
    "chana_dal": "chana dal", "masoor_dal": "masoor dal",
    "turmeric": "turmeric powder", "cumin": "jeera",
    "jeera": "jeera", "red_chilli": "red chilli powder",
    "mustard_oil": "mustard oil", "coconut_oil": "coconut oil",
    "milk": "milk", "ghee": "ghee", "butter": "butter",
    "curd": "curd", "paneer": "paneer",
    "egg": "eggs", "chicken": "chicken",
    "jaggery": "jaggery", "tea": "tea",
    "coffee": "coffee", "coconut": "coconut",
    "fish": "fish", "mutton": "mutton",
}


class BigBasketScraper:
    """
    Scrapes product prices from BigBasket's internal listing API.
    
    How it works:
    1. Visits BigBasket homepage to get session cookies
    2. Uses the listing-svc API to fetch products by category
    3. Extracts prices from the JSON response
    4. Caches results with a 2-hour TTL
    """

    BASE_URL = "https://www.bigbasket.com"
    API_URL = f"{BASE_URL}/listing-svc/v2/products"
    CACHE_TTL = 7200  # 2 hours
    MIN_REQUEST_INTERVAL = 1.5  # seconds between requests
    SESSION_TTL = 1800  # refresh session every 30 min

    def __init__(self):
        self._client: Optional[httpx.Client] = None
        self._last_request_time = 0.0
        self._session_created_at = 0.0
        self._cache: dict[str, tuple[float, list[ScrapedProduct]]] = {}

    def _ensure_session(self):
        """Create or refresh the HTTP session with cookies."""
        now = time.time()
        if self._client and (now - self._session_created_at) < self.SESSION_TTL:
            return  # session still fresh

        # Close existing client
        if self._client:
            try:
                self._client.close()
            except:
                pass

        self._client = httpx.Client(follow_redirects=True, timeout=15)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        try:
            self._client.get(self.BASE_URL, headers=headers)
            self._session_created_at = now
            logger.info(f"BigBasket session created ({len(self._client.cookies)} cookies)")
        except Exception as e:
            logger.error(f"Failed to create BigBasket session: {e}")
            self._client = None

    def _rate_limit(self):
        """Enforce minimum interval between requests."""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self.MIN_REQUEST_INTERVAL:
            time.sleep(self.MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.time()

    def _parse_product(self, item: dict) -> Optional[ScrapedProduct]:
        """Parse a single product item from the BigBasket API response."""
        try:
            desc = item.get("desc", "").strip()
            brand = item.get("brand", {}).get("name", "").strip()
            weight_str = item.get("w", "").strip()
            magnitude = int(item.get("magnitude", 0))
            unit = item.get("unit", "g")

            # Extract pricing
            pricing = item.get("pricing", {})
            discount_info = pricing.get("discount", {})
            mrp = float(discount_info.get("mrp", 0))
            
            prim_price = discount_info.get("prim_price", {})
            sp = float(prim_price.get("sp", 0) or 0)
            
            d_text = discount_info.get("d_text", "")

            if not desc or sp <= 0:
                return None

            # Calculate price per kg (normalize to 1000g)
            if magnitude > 0:
                price_per_kg = (sp / magnitude) * 1000
            else:
                price_per_kg = sp  # assume 1kg if no weight info

            # Category
            category = item.get("category", {}).get("tlc_name", "")

            # URL
            url = item.get("absolute_url", "")
            if url:
                url = f"https://www.bigbasket.com{url}"

            return ScrapedProduct(
                name=desc,
                brand=brand,
                sp=sp,
                mrp=mrp,
                weight=weight_str,
                weight_grams=magnitude,
                unit=unit,
                price_per_kg=round(price_per_kg, 2),
                discount=d_text,
                category=category,
                source="bigbasket",
                url=url,
            )
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"Failed to parse BB product: {e}")
            return None

    def _fetch_category(self, slug: str, page: int = 1, size: int = 20) -> list[dict]:
        """Fetch products from a BigBasket category slug."""
        self._ensure_session()
        if not self._client:
            return []

        self._rate_limit()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{self.BASE_URL}/",
        }

        params = {
            "type": "pc",
            "slug": slug,
            "page": page,
            "size": size,
        }

        try:
            r = self._client.get(self.API_URL, headers=headers, params=params)
            if r.status_code != 200:
                logger.warning(f"BB API returned {r.status_code} for slug={slug}")
                return []

            data = r.json()
            products = []
            for tab in data.get("tabs", []):
                product_info = tab.get("product_info", {})
                for product in product_info.get("products", []):
                    products.append(product)
                    # Also include children (variant sizes)
                    for child in product.get("children", []):
                        products.append(child)

            return products
        except Exception as e:
            logger.error(f"BigBasket API error: {e}")
            return []

    def search_product(self, product_id: str) -> list[ScrapedProduct]:
        """
        Search for a product on BigBasket and return matching items with prices.

        Args:
            product_id: Internal product ID (e.g. "tomato", "atta", "onion")

        Returns:
            List of ScrapedProduct objects with real prices
        """
        # Check cache
        cache_key = f"bb_{product_id}"
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if time.time() - cached_time < self.CACHE_TTL:
                logger.info(f"BigBasket cache hit for {product_id}")
                return cached_data

        # Get the search term and category slug
        search_term = BB_SEARCH_TERMS.get(product_id, product_id.replace("_", " "))
        slug = BB_CATEGORIES.get(product_id)

        if not slug:
            logger.warning(f"No BigBasket category for product: {product_id}")
            return []

        # Fetch products from category
        raw_products = self._fetch_category(slug, size=30)

        if not raw_products:
            logger.warning(f"No products returned from BigBasket for {product_id}")
            return []

        # Parse and filter products matching the search term
        parsed = []
        for item in raw_products:
            product = self._parse_product(item)
            if product:
                parsed.append(product)

        # Filter: only keep products whose name matches the search term
        search_lower = search_term.lower()
        search_words = set(search_lower.split())

        matches = []
        for p in parsed:
            p_lower = p.name.lower()
            # Exact match or word match
            if search_lower in p_lower or any(w in p_lower for w in search_words):
                matches.append(p)

        # Sort by relevance (exact matches first) then by price
        def sort_key(p):
            name_lower = p.name.lower()
            exact = 0 if search_lower == name_lower else 1
            return (exact, p.sp)

        matches.sort(key=sort_key)

        # Cache results
        self._cache[cache_key] = (time.time(), matches)
        logger.info(f"BigBasket: found {len(matches)} products for '{product_id}'")

        return matches

    def get_best_price(self, product_id: str) -> Optional[PriceResult]:
        """
        Get the best (lowest) price for a product from BigBasket.

        Returns a PriceResult with BigBasket price, estimated JioMart price,
        and estimated local market price.
        """
        products = self.search_product(product_id)
        if not products:
            return None

        # Find the cheapest per-kg price (prefer 1kg packs for fair comparison)
        one_kg_products = [p for p in products if 900 <= p.weight_grams <= 1100]
        if one_kg_products:
            best = min(one_kg_products, key=lambda p: p.sp)
        else:
            # Use per-kg normalized price
            best = min(products, key=lambda p: p.price_per_kg)

        # Estimate JioMart and local market prices from BigBasket
        bb_price_per_kg = best.price_per_kg
        jiomart_est = round(bb_price_per_kg * 0.95, 2)    # JioMart typically 5% cheaper
        local_market_est = round(bb_price_per_kg * 0.90, 2)  # local market ~10% cheaper

        return PriceResult(
            product_name=best.name,
            bigbasket_price=best.price_per_kg,
            bigbasket_mrp=best.mrp,
            bigbasket_weight=best.weight,
            bigbasket_discount=best.discount,
            jiomart_price=jiomart_est,
            local_market_price=local_market_est,
            source="bigbasket",
            products=products[:5],  # top 5 matches
        )

    def close(self):
        """Close the HTTP client."""
        if self._client:
            try:
                self._client.close()
            except:
                pass
            self._client = None


# ─── Global scraper instance ───────────────────────────────────────

_scraper: Optional[BigBasketScraper] = None

def get_scraper() -> BigBasketScraper:
    """Get or create the global BigBasket scraper instance."""
    global _scraper
    if _scraper is None:
        _scraper = BigBasketScraper()
    return _scraper


def scrape_product_price(product_id: str) -> Optional[PriceResult]:
    """
    Public API: Get real retail prices for a product.

    Args:
        product_id: Internal product ID (e.g. "tomato", "atta", "onion")

    Returns:
        PriceResult with BigBasket, estimated JioMart, and local market prices,
        or None if scraping fails.
    """
    try:
        scraper = get_scraper()
        return scraper.get_best_price(product_id)
    except Exception as e:
        logger.error(f"Scraper error for {product_id}: {e}")
        return None
