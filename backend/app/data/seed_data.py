"""
Realistic seed data for BharatPrice AI prototype.
Contains 50+ products with prices across multiple Indian cities,
mandi rates, and 30-day price history with natural fluctuations.
"""

import random
import math
from datetime import datetime, timedelta

# ─── Product Catalog ───────────────────────────────────────────────

PRODUCTS = {
    # Staples
    "atta_10kg": {"name": "Atta (Wheat Flour)", "category": "staples", "unit": "per 10kg", "base_price": 320},
    "chawal_basmati_5kg": {"name": "Basmati Rice", "category": "staples", "unit": "per 5kg", "base_price": 450},
    "chawal_regular_5kg": {"name": "Regular Rice", "category": "staples", "unit": "per 5kg", "base_price": 250},
    "dal_toor_1kg": {"name": "Toor Dal", "category": "staples", "unit": "per kg", "base_price": 160},
    "dal_moong_1kg": {"name": "Moong Dal", "category": "staples", "unit": "per kg", "base_price": 130},
    "dal_chana_1kg": {"name": "Chana Dal", "category": "staples", "unit": "per kg", "base_price": 95},
    "dal_urad_1kg": {"name": "Urad Dal", "category": "staples", "unit": "per kg", "base_price": 140},
    "sugar_1kg": {"name": "Sugar", "category": "staples", "unit": "per kg", "base_price": 45},
    "salt_1kg": {"name": "Salt", "category": "staples", "unit": "per kg", "base_price": 22},
    "maida_1kg": {"name": "Maida", "category": "staples", "unit": "per kg", "base_price": 40},
    "besan_1kg": {"name": "Besan (Gram Flour)", "category": "staples", "unit": "per kg", "base_price": 90},
    "sooji_1kg": {"name": "Sooji (Semolina)", "category": "staples", "unit": "per kg", "base_price": 50},
    "poha_1kg": {"name": "Poha (Flattened Rice)", "category": "staples", "unit": "per kg", "base_price": 55},

    # Oils
    "oil_mustard_1l": {"name": "Mustard Oil", "category": "oils", "unit": "per litre", "base_price": 180},
    "oil_sunflower_1l": {"name": "Sunflower Oil", "category": "oils", "unit": "per litre", "base_price": 150},
    "oil_groundnut_1l": {"name": "Groundnut Oil", "category": "oils", "unit": "per litre", "base_price": 200},
    "ghee_1kg": {"name": "Desi Ghee", "category": "oils", "unit": "per kg", "base_price": 550},

    # Vegetables
    "tamatar_1kg": {"name": "Tamatar (Tomato)", "category": "vegetables", "unit": "per kg", "base_price": 40},
    "pyaaz_1kg": {"name": "Pyaaz (Onion)", "category": "vegetables", "unit": "per kg", "base_price": 35},
    "aloo_1kg": {"name": "Aloo (Potato)", "category": "vegetables", "unit": "per kg", "base_price": 30},
    "gobhi_1kg": {"name": "Gobhi (Cauliflower)", "category": "vegetables", "unit": "per kg", "base_price": 40},
    "palak_bunch": {"name": "Palak (Spinach)", "category": "vegetables", "unit": "per bunch", "base_price": 25},
    "shimla_mirch_1kg": {"name": "Shimla Mirch (Capsicum)", "category": "vegetables", "unit": "per kg", "base_price": 80},
    "bhindi_1kg": {"name": "Bhindi (Okra)", "category": "vegetables", "unit": "per kg", "base_price": 60},
    "baingan_1kg": {"name": "Baingan (Brinjal)", "category": "vegetables", "unit": "per kg", "base_price": 45},
    "gajar_1kg": {"name": "Gajar (Carrot)", "category": "vegetables", "unit": "per kg", "base_price": 50},
    "adrak_1kg": {"name": "Adrak (Ginger)", "category": "vegetables", "unit": "per kg", "base_price": 200},
    "lehsun_1kg": {"name": "Lehsun (Garlic)", "category": "vegetables", "unit": "per kg", "base_price": 250},
    "mirchi_hari_1kg": {"name": "Hari Mirch (Green Chilli)", "category": "vegetables", "unit": "per kg", "base_price": 100},

    # Fruits
    "kela_dozen": {"name": "Kela (Banana)", "category": "fruits", "unit": "per dozen", "base_price": 60},
    "seb_1kg": {"name": "Seb (Apple)", "category": "fruits", "unit": "per kg", "base_price": 180},
    "santra_1kg": {"name": "Santra (Orange)", "category": "fruits", "unit": "per kg", "base_price": 80},

    # Dairy
    "doodh_1l": {"name": "Doodh (Milk)", "category": "dairy", "unit": "per litre", "base_price": 60},
    "dahi_1kg": {"name": "Dahi (Curd)", "category": "dairy", "unit": "per kg", "base_price": 55},
    "paneer_1kg": {"name": "Paneer", "category": "dairy", "unit": "per kg", "base_price": 350},
    "butter_500g": {"name": "Butter", "category": "dairy", "unit": "per 500g", "base_price": 270},

    # Spices
    "haldi_100g": {"name": "Haldi (Turmeric)", "category": "spices", "unit": "per 100g", "base_price": 35},
    "mirchi_powder_100g": {"name": "Lal Mirch Powder", "category": "spices", "unit": "per 100g", "base_price": 50},
    "dhaniya_powder_100g": {"name": "Dhaniya Powder", "category": "spices", "unit": "per 100g", "base_price": 30},
    "jeera_100g": {"name": "Jeera (Cumin)", "category": "spices", "unit": "per 100g", "base_price": 55},
    "garam_masala_100g": {"name": "Garam Masala", "category": "spices", "unit": "per 100g", "base_price": 65},

    # FMCG / Packaged
    "chai_patti_250g": {"name": "Chai Patti (Tea)", "category": "fmcg", "unit": "per 250g", "base_price": 110},
    "coffee_100g": {"name": "Coffee Powder", "category": "fmcg", "unit": "per 100g", "base_price": 90},
    "maggi_4pack": {"name": "Maggi Noodles", "category": "fmcg", "unit": "4-pack", "base_price": 56},
    "biscuit_parle_g": {"name": "Parle-G Biscuit", "category": "fmcg", "unit": "per pack", "base_price": 10},
    "soap_lifebuoy": {"name": "Lifebuoy Soap", "category": "fmcg", "unit": "per bar", "base_price": 38},
    "detergent_1kg": {"name": "Surf Excel", "category": "fmcg", "unit": "per kg", "base_price": 230},
    "bread_400g": {"name": "Bread", "category": "fmcg", "unit": "per 400g", "base_price": 40},
}


# ─── Regions & Cities ──────────────────────────────────────────────

REGIONS = {
    "delhi": {
        "city": "Delhi",
        "mandis": ["Azadpur Mandi", "Okhla Mandi", "Ghazipur Mandi"],
        "price_factor": 1.0,
    },
    "mumbai": {
        "city": "Mumbai",
        "mandis": ["Vashi APMC", "Crawford Market", "Dadar Mandi"],
        "price_factor": 1.12,
    },
    "bangalore": {
        "city": "Bangalore",
        "mandis": ["Yeshwanthpur APMC", "KR Market", "Madiwala Market"],
        "price_factor": 1.05,
    },
    "kolkata": {
        "city": "Kolkata",
        "mandis": ["Koley Market", "Sealdah Market", "Maniktala Bazar"],
        "price_factor": 0.92,
    },
    "chennai": {
        "city": "Chennai",
        "mandis": ["Koyambedu Market", "Sowcarpet Market"],
        "price_factor": 0.98,
    },
    "hyderabad": {
        "city": "Hyderabad",
        "mandis": ["Begum Bazaar", "Gudimalkapur Market", "Mehdipatnam Market"],
        "price_factor": 0.95,
    },
    "jaipur": {
        "city": "Jaipur",
        "mandis": ["Muhana Mandi", "Chomu Mandi"],
        "price_factor": 0.88,
    },
    "lucknow": {
        "city": "Lucknow",
        "mandis": ["Alambagh Mandi", "Dubagga Mandi"],
        "price_factor": 0.85,
    },
}


# ─── Price Generation ──────────────────────────────────────────────

def _add_noise(price: float, pct: float = 0.08) -> float:
    """Add realistic random noise to a price."""
    return round(price * (1 + random.uniform(-pct, pct)), 2)


def _seasonal_factor(date: datetime) -> float:
    """Simulate seasonal price variation using a sine wave."""
    day_of_year = date.timetuple().tm_yday
    return 1 + 0.06 * math.sin(2 * math.pi * day_of_year / 365)


def generate_price_record(product_id: str, region_id: str, date: datetime) -> dict:
    """Generate a single price record for a product in a region on a date."""
    product = PRODUCTS[product_id]
    region = REGIONS[region_id]

    base = product["base_price"] * region["price_factor"] * _seasonal_factor(date)

    mandi_price = _add_noise(base * 0.7, 0.10)  # Mandi is ~30% cheaper
    bigbasket_price = _add_noise(base * 1.08, 0.05)  # Online slightly higher
    jiomart_price = _add_noise(base * 1.05, 0.05)
    local_avg = _add_noise(base, 0.06)
    recommended = round((local_avg * 0.6 + bigbasket_price * 0.2 + jiomart_price * 0.2) * 0.98, 2)

    # Determine trend
    trend_roll = random.random()
    if trend_roll < 0.3:
        demand_trend = "rising"
    elif trend_roll < 0.6:
        demand_trend = "falling"
    else:
        demand_trend = "stable"

    return {
        "product_id": product_id,
        "product_name": product["name"],
        "date": date.strftime("%Y-%m-%d"),
        "region": region_id,
        "city": region["city"],
        "category": product["category"],
        "mandi_price": mandi_price,
        "bigbasket_price": bigbasket_price,
        "jiomart_price": jiomart_price,
        "local_avg": local_avg,
        "recommended_retail": recommended,
        "demand_trend": demand_trend,
        "unit": product["unit"],
    }


def generate_mandi_rates(product_id: str, region_id: str, date: datetime) -> list[dict]:
    """Generate mandi rates for a product across mandis in a region."""
    product = PRODUCTS[product_id]
    region = REGIONS[region_id]

    rates = []
    for mandi_name in region["mandis"]:
        base = product["base_price"] * region["price_factor"] * 0.7 * _seasonal_factor(date)
        rates.append({
            "product_id": product_id,
            "product_name": product["name"],
            "mandi_name": mandi_name,
            "location": region["city"],
            "price": _add_noise(base * 100, 0.08),  # per quintal
            "unit": "per quintal",
            "date": date.strftime("%Y-%m-%d"),
        })
    return rates


def generate_all_prices(days: int = 30) -> list[dict]:
    """Generate price records for all products × regions × days."""
    records = []
    today = datetime.now()
    for day_offset in range(days):
        date = today - timedelta(days=day_offset)
        for product_id in PRODUCTS:
            for region_id in REGIONS:
                records.append(generate_price_record(product_id, region_id, date))
    return records


def generate_all_mandi_rates() -> list[dict]:
    """Generate today's mandi rates for all products × regions."""
    rates = []
    today = datetime.now()
    for product_id in PRODUCTS:
        if PRODUCTS[product_id]["category"] in ("vegetables", "fruits", "staples"):
            for region_id in REGIONS:
                rates.extend(generate_mandi_rates(product_id, region_id, today))
    return rates


def get_product_list() -> list[dict]:
    """Return the product catalog."""
    return [
        {"id": pid, "name": p["name"], "category": p["category"], "unit": p["unit"]}
        for pid, p in PRODUCTS.items()
    ]


# ─── Quick-Access Helpers ──────────────────────────────────────────

def find_product_id(query: str) -> str | None:
    """Fuzzy-match a product name from user query."""
    query_lower = query.lower().strip()

    # Direct ID match
    if query_lower in PRODUCTS:
        return query_lower

    # Name/keyword matching
    keyword_map = {
        "atta": "atta_10kg", "wheat": "atta_10kg", "flour": "atta_10kg", "गेहूं": "atta_10kg", "आटा": "atta_10kg",
        "basmati": "chawal_basmati_5kg", "rice": "chawal_regular_5kg", "chawal": "chawal_regular_5kg", "चावल": "chawal_regular_5kg",
        "toor": "dal_toor_1kg", "arhar": "dal_toor_1kg", "अरहर": "dal_toor_1kg",
        "moong": "dal_moong_1kg", "मूंग": "dal_moong_1kg",
        "chana": "dal_chana_1kg", "चना": "dal_chana_1kg",
        "urad": "dal_urad_1kg", "उड़द": "dal_urad_1kg",
        "dal": "dal_toor_1kg", "daal": "dal_toor_1kg", "दाल": "dal_toor_1kg",
        "sugar": "sugar_1kg", "cheeni": "sugar_1kg", "चीनी": "sugar_1kg",
        "salt": "salt_1kg", "namak": "salt_1kg", "नमक": "salt_1kg",
        "maida": "maida_1kg", "मैदा": "maida_1kg",
        "besan": "besan_1kg", "बेसन": "besan_1kg",
        "sooji": "sooji_1kg", "semolina": "sooji_1kg", "सूजी": "sooji_1kg",
        "poha": "poha_1kg", "पोहा": "poha_1kg",
        "mustard oil": "oil_mustard_1l", "sarson": "oil_mustard_1l", "सरसों": "oil_mustard_1l",
        "sunflower": "oil_sunflower_1l", "oil": "oil_mustard_1l", "तेल": "oil_mustard_1l",
        "groundnut": "oil_groundnut_1l",
        "ghee": "ghee_1kg", "घी": "ghee_1kg",
        "tomato": "tamatar_1kg", "tamatar": "tamatar_1kg", "टमाटर": "tamatar_1kg",
        "onion": "pyaaz_1kg", "pyaaz": "pyaaz_1kg", "प्याज़": "pyaaz_1kg",
        "potato": "aloo_1kg", "aloo": "aloo_1kg", "aaloo": "aloo_1kg", "आलू": "aloo_1kg",
        "cauliflower": "gobhi_1kg", "gobhi": "gobhi_1kg", "गोभी": "gobhi_1kg",
        "spinach": "palak_bunch", "palak": "palak_bunch", "पालक": "palak_bunch",
        "capsicum": "shimla_mirch_1kg", "shimla mirch": "shimla_mirch_1kg",
        "okra": "bhindi_1kg", "bhindi": "bhindi_1kg", "lady finger": "bhindi_1kg", "भिंडी": "bhindi_1kg",
        "brinjal": "baingan_1kg", "baingan": "baingan_1kg", "बैंगन": "baingan_1kg",
        "carrot": "gajar_1kg", "gajar": "gajar_1kg", "गाजर": "gajar_1kg",
        "ginger": "adrak_1kg", "adrak": "adrak_1kg", "अदरक": "adrak_1kg",
        "garlic": "lehsun_1kg", "lehsun": "lehsun_1kg", "लहसुन": "lehsun_1kg",
        "green chilli": "mirchi_hari_1kg", "hari mirch": "mirchi_hari_1kg", "हरी मिर्च": "mirchi_hari_1kg",
        "banana": "kela_dozen", "kela": "kela_dozen", "केला": "kela_dozen",
        "apple": "seb_1kg", "seb": "seb_1kg", "सेब": "seb_1kg",
        "orange": "santra_1kg", "santra": "santra_1kg", "संतरा": "santra_1kg",
        "milk": "doodh_1l", "doodh": "doodh_1l", "दूध": "doodh_1l",
        "curd": "dahi_1kg", "dahi": "dahi_1kg", "दही": "dahi_1kg",
        "paneer": "paneer_1kg", "पनीर": "paneer_1kg",
        "butter": "butter_500g", "makkhan": "butter_500g", "मक्खन": "butter_500g",
        "turmeric": "haldi_100g", "haldi": "haldi_100g", "हल्दी": "haldi_100g",
        "red chilli": "mirchi_powder_100g", "lal mirch": "mirchi_powder_100g", "लाल मिर्च": "mirchi_powder_100g",
        "coriander": "dhaniya_powder_100g", "dhaniya": "dhaniya_powder_100g", "धनिया": "dhaniya_powder_100g",
        "cumin": "jeera_100g", "jeera": "jeera_100g", "जीरा": "jeera_100g",
        "garam masala": "garam_masala_100g", "masala": "garam_masala_100g",
        "tea": "chai_patti_250g", "chai": "chai_patti_250g", "चाय": "chai_patti_250g",
        "coffee": "coffee_100g", "कॉफी": "coffee_100g",
        "maggi": "maggi_4pack", "noodles": "maggi_4pack",
        "biscuit": "biscuit_parle_g", "parle": "biscuit_parle_g",
        "soap": "soap_lifebuoy", "साबुन": "soap_lifebuoy",
        "detergent": "detergent_1kg",
        "bread": "bread_400g", "ब्रेड": "bread_400g",
    }

    for keyword, pid in keyword_map.items():
        if keyword in query_lower:
            return pid

    return None
