"""Test product resolution after fixes."""
from app.data.product_mapping import resolve_product_id
from app.services.ai_engine import extract_product

print("=== resolve_product_id tests ===")
tests = [
    ("What is the price of atta today?", "atta"),
    ("potato price", "potato"),
    ("tomato ka rate kya hai", "tomato"),
    ("onion prices compare", "onion"),
    ("aloo ka mandi rate", "potato"),
    ("pyaaz ki kimat", "onion"),
    ("rice price", "rice"),
    ("compare dal prices", "dal"),
    ("show me sugar rate", "sugar"),
]

all_pass = True
for query, expected in tests:
    result = resolve_product_id(query)
    status = "PASS" if result == expected else "FAIL"
    if status == "FAIL":
        all_pass = False
    print(f"  [{status}] '{query}' -> '{result}' (expected: '{expected}')")

print()
print("=== extract_product tests ===")
tests2 = [
    ("What is the price of atta today?", "atta"),
    ("potato price", "potato"),
    ("aloo ka rate", "potato"),
]
for query, expected in tests2:
    result = extract_product(query)
    status = "PASS" if result == expected else "FAIL"
    if status == "FAIL":
        all_pass = False
    print(f"  [{status}] '{query}' -> '{result}' (expected: '{expected}')")

print()
print("ALL PASS" if all_pass else "SOME FAILURES")
