"""
Product-to-commodity mapping for data.gov.in API.
Maps our product names/aliases to the exact commodity names used in the AGMARKNET database.
Also includes retail markup factors per category.
"""

# Map internal product IDs → data.gov.in commodity name
# The data.gov.in API uses specific commodity names (case-sensitive)
PRODUCT_TO_COMMODITY = {
    # Vegetables
    "tomato": "Tomato",
    "onion": "Onion",
    "potato": "Potato",
    "cabbage": "Cabbage",
    "cauliflower": "Cauliflower",
    "green_chilli": "Green Chilli",
    "ginger": "Ginger(Green)",
    "garlic": "Garlic",
    "brinjal": "Brinjal",
    "lady_finger": "Ladies Finger",
    "capsicum": "Capsicum",
    "carrot": "Carrot",
    "peas": "Green Peas",
    "spinach": "Spinach",
    "bitter_gourd": "Bitter gourd",
    "bottle_gourd": "Bottle gourd",
    "cucumber": "Cucumber",
    "drumstick": "Drumstick",
    "coriander": "Coriander(Leaves)",
    "lemon": "Lemon",
    "pumpkin": "Pumpkin",
    "radish": "Raddish",
    "beans": "Beans",

    # Fruits
    "apple": "Apple",
    "banana": "Banana",
    "mango": "Mango",
    "grapes": "Grapes",
    "orange": "Orange",
    "papaya": "Papaya",
    "watermelon": "Water Melon",
    "pomegranate": "Pomegranate",
    "guava": "Guava",
    "pineapple": "Pineapple",

    # Grains & Pulses
    "rice": "Rice",
    "wheat": "Wheat",
    "sugar": "Sugar",
    "dal": "Arhar Dal(Tur Dal)",
    "arhar_dal": "Arhar Dal(Tur Dal)",
    "toor_dal": "Arhar Dal(Tur Dal)",
    "moong_dal": "Moong Dal",
    "urad_dal": "Urad Dal",
    "chana_dal": "Gram Dal",
    "masoor_dal": "Masoor Dal",
    "maize": "Maize",
    "bajra": "Bajra(Pearl Millet/Cumbu)",
    "jowar": "Jowar(Sorghum)",
    "ragi": "Ragi (Finger Millet)",
    "soybean": "Soyabean",
    "groundnut": "Groundnut",
    "mustard": "Mustard",
    "atta": "Wheat",
    "atta_5kg": "Wheat",
    "atta_10kg": "Wheat",

    # Spices
    "turmeric": "Turmeric",
    "cumin": "Cummin(Jeera)",
    "jeera": "Cummin(Jeera)",
    "red_chilli": "Dry Chillies",
    "black_pepper": "Black pepper",
    "cardamom": "Cardamom",
    "cinnamon": "Cinnamon(Dalchini)",
    "clove": "Cloves",
    "ajwain": "Ajwan",
    "methi": "Methi (Fenugreek Seed)",

    # Oils & Others
    "mustard_oil": "Mustard Oil",
    "coconut_oil": "Coconut Oil",
    "coconut": "Coconut",
    "jaggery": "Jaggery(Gur)",
    "tea": "Tea",
    "coffee": "Coffee",
    "milk": "Milk",
    "ghee": "Ghee",
    "butter": "Butter",
    "curd": "Curd/Dahi (Packed)",
    "paneer": "Paneer",
    "egg": "Hen Egg (10 Pcs.)",
    "chicken": "Chicken",
    "fish": "Fish",
    "mutton": "Mutton",
}

# Hindi aliases → internal product ID
HINDI_ALIASES = {
    "टमाटर": "tomato", "tamatar": "tomato",
    "प्याज": "onion", "pyaz": "onion", "pyaaz": "onion",
    "आलू": "potato", "aloo": "potato", "alu": "potato",
    "पत्ता गोभी": "cabbage", "band gobi": "cabbage",
    "फूल गोभी": "cauliflower", "phool gobi": "cauliflower",
    "हरी मिर्च": "green_chilli", "hari mirch": "green_chilli",
    "अदरक": "ginger", "adrak": "ginger",
    "लहसुन": "garlic", "lehsun": "garlic", "lahsun": "garlic",
    "बैंगन": "brinjal", "baingan": "brinjal",
    "भिंडी": "lady_finger", "bhindi": "lady_finger",
    "शिमला मिर्च": "capsicum", "shimla mirch": "capsicum",
    "गाजर": "carrot", "gajar": "carrot",
    "मटर": "peas", "matar": "peas",
    "पालक": "spinach", "palak": "spinach",
    "करेला": "bitter_gourd", "karela": "bitter_gourd",
    "लौकी": "bottle_gourd", "lauki": "bottle_gourd",
    "खीरा": "cucumber", "kheera": "cucumber",
    "धनिया": "coriander", "dhaniya": "coriander",
    "नींबू": "lemon", "nimbu": "lemon",
    "कद्दू": "pumpkin", "kaddu": "pumpkin",
    "मूली": "radish", "mooli": "radish",
    "सेब": "apple", "seb": "apple",
    "केला": "banana", "kela": "banana",
    "आम": "mango", "aam": "mango",
    "अंगूर": "grapes", "angoor": "grapes",
    "संतरा": "orange", "santra": "orange",
    "पपीता": "papaya", "papita": "papaya",
    "तरबूज": "watermelon", "tarbooz": "watermelon",
    "अनार": "pomegranate", "anaar": "pomegranate",
    "अमरूद": "guava", "amrood": "guava",
    "चावल": "rice", "chawal": "rice",
    "गेहूं": "wheat", "gehun": "wheat", "gehu": "wheat",
    "चीनी": "sugar", "cheeni": "sugar",
    "दाल": "dal", "dal": "dal",
    "अरहर दाल": "arhar_dal", "तूर दाल": "toor_dal",
    "मूंग दाल": "moong_dal", "moong": "moong_dal",
    "उड़द दाल": "urad_dal", "urad": "urad_dal",
    "चना दाल": "chana_dal", "chana": "chana_dal",
    "मसूर दाल": "masoor_dal", "masoor": "masoor_dal",
    "हल्दी": "turmeric", "haldi": "turmeric",
    "जीरा": "cumin", "zeera": "cumin",
    "लाल मिर्च": "red_chilli", "lal mirch": "red_chilli",
    "काली मिर्च": "black_pepper", "kali mirch": "black_pepper",
    "इलायची": "cardamom", "elaichi": "cardamom",
    "दालचीनी": "cinnamon", "dalchini": "cinnamon",
    "लौंग": "clove", "laung": "clove",
    "सरसों का तेल": "mustard_oil", "sarson tel": "mustard_oil",
    "नारियल तेल": "coconut_oil", "nariyal tel": "coconut_oil",
    "गुड़": "jaggery", "gur": "jaggery", "gud": "jaggery",
    "चाय": "tea", "chai": "tea",
    "दूध": "milk", "doodh": "milk",
    "घी": "ghee",
    "मक्खन": "butter", "makhan": "butter",
    "दही": "curd", "dahi": "curd",
    "पनीर": "paneer",
    "अंडा": "egg", "anda": "egg",
    "मुर्गा": "chicken", "murga": "chicken", "murgi": "chicken",
    "मछली": "fish", "machli": "fish", "machhi": "fish",
    "मटन": "mutton",
    "आटा": "atta", "aata": "atta",
}

# Retail markup factors: mandi wholesale → estimated retail
# Different categories have different supply chain markups
RETAIL_MARKUP = {
    # Perishable vegetables: higher markup (transport loss, wastage)
    "vegetables": 1.5,
    "fruits": 1.6,
    # Staples: lower markup (efficient supply chain)
    "grains": 1.2,
    "pulses": 1.25,
    "spices": 1.5,
    "oils": 1.15,
    "dairy": 1.1,
    "eggs_meat": 1.3,
    "others": 1.3,
}

# Product → category for markup calculation
PRODUCT_CATEGORY = {
    "tomato": "vegetables", "onion": "vegetables", "potato": "vegetables",
    "cabbage": "vegetables", "cauliflower": "vegetables", "green_chilli": "vegetables",
    "ginger": "vegetables", "garlic": "vegetables", "brinjal": "vegetables",
    "lady_finger": "vegetables", "capsicum": "vegetables", "carrot": "vegetables",
    "peas": "vegetables", "spinach": "vegetables", "bitter_gourd": "vegetables",
    "bottle_gourd": "vegetables", "cucumber": "vegetables", "drumstick": "vegetables",
    "coriander": "vegetables", "lemon": "vegetables", "pumpkin": "vegetables",
    "radish": "vegetables", "beans": "vegetables",
    "apple": "fruits", "banana": "fruits", "mango": "fruits",
    "grapes": "fruits", "orange": "fruits", "papaya": "fruits",
    "watermelon": "fruits", "pomegranate": "fruits", "guava": "fruits",
    "pineapple": "fruits",
    "rice": "grains", "wheat": "grains", "sugar": "grains",
    "maize": "grains", "bajra": "grains", "jowar": "grains", "ragi": "grains",
    "dal": "pulses", "arhar_dal": "pulses", "toor_dal": "pulses",
    "moong_dal": "pulses", "urad_dal": "pulses", "chana_dal": "pulses",
    "masoor_dal": "pulses", "soybean": "pulses", "groundnut": "pulses",
    "turmeric": "spices", "cumin": "spices", "jeera": "spices",
    "red_chilli": "spices", "black_pepper": "spices", "cardamom": "spices",
    "cinnamon": "spices", "clove": "spices", "ajwain": "spices", "methi": "spices",
    "mustard_oil": "oils", "coconut_oil": "oils", "mustard": "oils",
    "coconut": "others", "jaggery": "others", "tea": "others", "coffee": "others",
    "milk": "dairy", "ghee": "dairy", "butter": "dairy", "curd": "dairy", "paneer": "dairy",
    "egg": "eggs_meat", "chicken": "eggs_meat", "fish": "eggs_meat", "mutton": "eggs_meat",
    "atta": "grains", "atta_5kg": "grains", "atta_10kg": "grains",
}


import re

def resolve_product_id(query: str) -> str | None:
    """Resolve a user query (English/Hindi) to an internal product ID.
    
    Uses word-boundary matching to avoid false positives like
    'rice' matching inside 'price'.
    """
    q = query.lower().strip()

    # Direct exact match (single-word query)
    if q in PRODUCT_TO_COMMODITY:
        return q
    if q in HINDI_ALIASES:
        return HINDI_ALIASES[q]

    # Tokenize the query into words for word-boundary matching
    words = set(re.findall(r'[\w]+', q))

    # Priority 1: Check product IDs as whole words in the query
    # Sort by length descending so longer matches win (e.g. 'green_chilli' > 'chilli')
    best_match = None
    best_len = 0
    for pid in PRODUCT_TO_COMMODITY:
        # Handle multi-word product IDs (e.g. 'green_chilli' → check 'green chilli')
        pid_words = set(pid.replace('_', ' ').split())
        if pid_words.issubset(words) and len(pid) > best_len:
            best_match = pid
            best_len = len(pid)

    if best_match:
        return best_match

    # Priority 2: Check Hindi aliases as whole words
    for alias, pid in HINDI_ALIASES.items():
        alias_words = set(re.findall(r'[\w]+', alias.lower()))
        if alias_words.issubset(words):
            return pid

    # Priority 3: Word-boundary regex match for product IDs in longer text
    for pid in sorted(PRODUCT_TO_COMMODITY.keys(), key=len, reverse=True):
        # Only match whole words, not substrings
        pattern = r'\b' + re.escape(pid.replace('_', ' ')) + r'\b'
        if re.search(pattern, q):
            return pid

    return None


def get_commodity_name(product_id: str) -> str | None:
    """Get the data.gov.in commodity name for a product."""
    return PRODUCT_TO_COMMODITY.get(product_id)


def get_retail_markup(product_id: str) -> float:
    """Get the retail markup factor for a product category."""
    category = PRODUCT_CATEGORY.get(product_id, "others")
    return RETAIL_MARKUP.get(category, 1.3)


def get_online_markup(product_id: str) -> dict:
    """Get estimated BigBasket/JioMart markup factors."""
    category = PRODUCT_CATEGORY.get(product_id, "others")
    base_markup = RETAIL_MARKUP.get(category, 1.3)
    return {
        "bigbasket": base_markup * 1.05,  # BigBasket typically 5% above local retail
        "jiomart": base_markup * 0.98,     # JioMart often slightly cheaper
    }
