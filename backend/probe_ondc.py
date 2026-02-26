"""
Advanced ONDC Gateway Probe - Magicpin
"""
import httpx
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://magicpin.in",
    "Referer": "https://magicpin.in/",
}

# Magicpin's search API usually looks like this
url = "https://magicpin.in/api/v1/search"
params = {
    "query": "tomato",
    "lat": "28.6139",
    "lon": "77.2090",
    "city": "delhi"
}

print(f"Testing advanced probe on {url}...")

with httpx.Client(timeout=15) as client:
    try:
        r = client.get(url, headers=HEADERS, params=params)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            try:
                data = r.json()
                print(f"Response keys: {list(data.keys())}")
                with open("ondc_magicpin_probe.json", "w") as f:
                    json.dump(data, f, indent=2)
                print("Saved successful response to ondc_magicpin_probe.json")
            except:
                print(f"Not JSON. Output start: {r.text[:200]}")
        else:
            print(f"Failed. Response preview: {r.text[:200]}")
            
    except Exception as e:
        print(f"Error: {e}")
