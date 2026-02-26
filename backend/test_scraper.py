"""End-to-end test: scraper → price_fetcher → real prices."""
import logging
logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")

from app.services.price_fetcher import get_real_price
from app.services.scraper import scrape_product_price

print("=" * 70)
print("END-TO-END SCRAPER TEST")
print("=" * 70)

# Test 1: Direct scraper test (vegetables only - these work with category API)
print("\n--- Test 1: Direct BigBasket scraper ---")
for product in ["tomato", "onion", "potato"]:
    result = scrape_product_price(product)
    if result:
        print(f"  {product}: BB ₹{result.bigbasket_price}/kg | JM(est) ₹{result.jiomart_price}/kg | Local(est) ₹{result.local_market_price}/kg")
        if result.products:
            p = result.products[0]
            print(f"    Top match: {p.name} ({p.brand}) [{p.weight}] SP=₹{p.sp} MRP=₹{p.mrp}")
    else:
        print(f"  {product}: No BigBasket data")

# Test 2: Full pipeline (price_fetcher) with scraper integration
print("\n--- Test 2: Full price pipeline (mandi + scraper) ---")
for product in ["tomato", "onion", "potato", "atta", "rice"]:
    result = get_real_price(product, pincode="110001")
    if result:
        scraped_tag = "✅ SCRAPED" if result.get("bigbasket_scraped") else "📊 estimated"
        print(f"  {product}: mandi ₹{result['mandi_price']}/kg | BB ₹{result['bigbasket_price']}/kg [{scraped_tag}] | JM ₹{result['jiomart_price']}/kg | local ₹{result['local_avg']}/kg")
        print(f"    Recommended retail: ₹{result['recommended_retail']}/kg | Source: {result['data_source']}")
    else:
        print(f"  {product}: No data available")

print("\n" + "=" * 70)
print("DONE")
