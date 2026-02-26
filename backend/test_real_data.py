"""Quick test script for real data integration."""
import httpx
import json

BASE = "http://localhost:8000"

def test_price_with_pincode():
    print("=== TEST 1: Price Check WITH Pincode (real data) ===")
    r = httpx.post(f"{BASE}/api/chat", json={
        "message": "what is the price of potato",
        "language": "en",
        "region": "delhi",
        "pincode": "110001",
    }, timeout=15)
    data = r.json()
    print(f"Status: {r.status_code}")
    print(f"Intent: {data['intent']}")
    reply = data["reply"]
    print(reply[:700])
    print()
    has_real = "data.gov.in" in reply or "Real-time" in reply
    print(f"[{'PASS' if has_real else 'FAIL'}] Has real data badge: {has_real}")
    print()

def test_price_without_pincode():
    print("=== TEST 2: Price Check WITHOUT Pincode (seed data) ===")
    r = httpx.post(f"{BASE}/api/chat", json={
        "message": "potato price",
        "language": "en",
        "region": "delhi",
    }, timeout=10)
    data = r.json()
    print(f"Status: {r.status_code}")
    print(f"Intent: {data['intent']}")
    reply = data["reply"]
    print(reply[:400])
    print()
    has_est = "Estimated" in reply
    print(f"[{'PASS' if has_est else 'INFO'}] Has estimated badge: {has_est}")
    print()

def test_mandi_with_pincode():
    print("=== TEST 3: Mandi Rates WITH Pincode ===")
    r = httpx.post(f"{BASE}/api/chat", json={
        "message": "mandi rates for onion",
        "language": "en",
        "region": "delhi",
        "pincode": "400001",
    }, timeout=15)
    data = r.json()
    print(f"Status: {r.status_code}")
    print(f"Intent: {data['intent']}")
    reply = data["reply"]
    print(reply[:700])
    print()
    has_real = "data.gov.in" in reply or "Live" in reply or "AGMARKNET" in reply
    print(f"[{'PASS' if has_real else 'FAIL'}] Has live data badge: {has_real}")
    print()

def test_compare_with_pincode():
    print("=== TEST 4: Compare Prices WITH Pincode ===")
    r = httpx.post(f"{BASE}/api/chat", json={
        "message": "compare tomato prices",
        "language": "en",
        "region": "bangalore",
        "pincode": "560001",
    }, timeout=15)
    data = r.json()
    print(f"Status: {r.status_code}")
    print(f"Intent: {data['intent']}")
    reply = data["reply"]
    print(reply[:700])
    print()

if __name__ == "__main__":
    test_price_with_pincode()
    test_price_without_pincode()
    test_mandi_with_pincode()
    test_compare_with_pincode()
    print("=== ALL TESTS COMPLETE ===")
