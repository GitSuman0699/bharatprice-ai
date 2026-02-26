"""Test BigBasket search page HTML parsing for product data."""
import httpx
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

client = httpx.Client(follow_redirects=True, timeout=15)

# Get all search pages for various products
products = ["atta", "tomato", "rice", "sugar", "dal", "milk", "paneer", "egg"]

import time
for product in products:
    time.sleep(1.5)
    r = client.get(f"https://www.bigbasket.com/ps/?q={product}", headers=HEADERS)
    text = r.text
    
    # Try to find product data embedded by Next.js build process
    # Look for JSON-LD structured data
    jsonld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.DOTALL)
    
    # Look for any script containing pricing data
    # BigBasket renders everything client-side, but the page does have some meta info
    meta_title = re.search(r'<title>(.*?)</title>', text)
    meta_desc = re.search(r'<meta name="description" content="(.*?)"', text)
    
    # Check for price patterns in the HTML
    price_patterns = re.findall(r'Rs\.?\s*(\d+(?:\.\d+)?)', text)
    
    print(f"\n{product.upper()}: {r.status_code} ({len(text)} bytes)")
    if meta_title:
        print(f"  Title: {meta_title.group(1)[:80]}")
    if meta_desc:
        print(f"  Desc: {meta_desc.group(1)[:100]}")
    if jsonld:
        for j in jsonld:
            try:
                data = json.loads(j)
                if isinstance(data, dict):
                    dtype = data.get("@type", "unknown")
                    print(f"  JSON-LD type: {dtype}")
                    if "offers" in data:
                        print(f"  Offers: {data['offers']}")
                    if "itemListElement" in data:
                        elements = data["itemListElement"]
                        for el in elements[:3]:
                            print(f"  Item: {el.get('name', el.get('item', {}).get('name', '?'))}")
            except:
                pass
    if price_patterns:
        print(f"  Found {len(price_patterns)} prices in HTML: {price_patterns[:5]}")
    else:
        print(f"  No prices found in HTML")

client.close()
