"""
Pincode → location mapping for Indian cities.
Maps pincodes to state, district, city for use with data.gov.in mandi price API.
"""

# Comprehensive pincode → location mapping
# Key = pincode prefix (first 3-4 digits for area-level matching)
# For exact pincodes, we use full 6-digit mapping
PINCODE_MAP = {
    # Delhi NCR
    "110001": {"state": "Delhi", "district": "New Delhi", "city": "New Delhi"},
    "110002": {"state": "Delhi", "district": "New Delhi", "city": "New Delhi"},
    "110003": {"state": "Delhi", "district": "New Delhi", "city": "New Delhi"},
    "110005": {"state": "Delhi", "district": "New Delhi", "city": "New Delhi"},
    "110006": {"state": "Delhi", "district": "New Delhi", "city": "New Delhi"},
    "110010": {"state": "Delhi", "district": "South Delhi", "city": "New Delhi"},
    "110016": {"state": "Delhi", "district": "South Delhi", "city": "New Delhi"},
    "110017": {"state": "Delhi", "district": "South Delhi", "city": "New Delhi"},
    "110019": {"state": "Delhi", "district": "South Delhi", "city": "New Delhi"},
    "110020": {"state": "Delhi", "district": "South Delhi", "city": "New Delhi"},
    "110025": {"state": "Delhi", "district": "South Delhi", "city": "New Delhi"},
    "110030": {"state": "Delhi", "district": "South Delhi", "city": "New Delhi"},
    "110044": {"state": "Delhi", "district": "South East Delhi", "city": "New Delhi"},
    "110048": {"state": "Delhi", "district": "South Delhi", "city": "New Delhi"},
    "110051": {"state": "Delhi", "district": "East Delhi", "city": "New Delhi"},
    "110060": {"state": "Delhi", "district": "West Delhi", "city": "New Delhi"},
    "110085": {"state": "Delhi", "district": "North East Delhi", "city": "New Delhi"},
    "110092": {"state": "Delhi", "district": "East Delhi", "city": "New Delhi"},
    "201301": {"state": "Uttar Pradesh", "district": "Gautam Buddha Nagar", "city": "Noida"},
    "201303": {"state": "Uttar Pradesh", "district": "Gautam Buddha Nagar", "city": "Noida"},
    "201304": {"state": "Uttar Pradesh", "district": "Gautam Buddha Nagar", "city": "Greater Noida"},
    "122001": {"state": "Haryana", "district": "Gurgaon", "city": "Gurgaon"},
    "122002": {"state": "Haryana", "district": "Gurgaon", "city": "Gurgaon"},
    "122018": {"state": "Haryana", "district": "Gurgaon", "city": "Gurgaon"},
    "121001": {"state": "Haryana", "district": "Faridabad", "city": "Faridabad"},
    "201001": {"state": "Uttar Pradesh", "district": "Ghaziabad", "city": "Ghaziabad"},

    # Mumbai / Maharashtra
    "400001": {"state": "Maharashtra", "district": "Mumbai", "city": "Mumbai"},
    "400002": {"state": "Maharashtra", "district": "Mumbai", "city": "Mumbai"},
    "400050": {"state": "Maharashtra", "district": "Mumbai Suburban", "city": "Mumbai"},
    "400053": {"state": "Maharashtra", "district": "Mumbai Suburban", "city": "Mumbai"},
    "400069": {"state": "Maharashtra", "district": "Mumbai Suburban", "city": "Mumbai"},
    "400076": {"state": "Maharashtra", "district": "Mumbai Suburban", "city": "Mumbai"},
    "400080": {"state": "Maharashtra", "district": "Mumbai Suburban", "city": "Mumbai"},
    "400093": {"state": "Maharashtra", "district": "Mumbai Suburban", "city": "Mumbai"},
    "400097": {"state": "Maharashtra", "district": "Mumbai Suburban", "city": "Mumbai"},
    "400601": {"state": "Maharashtra", "district": "Thane", "city": "Thane"},
    "400614": {"state": "Maharashtra", "district": "Thane", "city": "Navi Mumbai"},
    "411001": {"state": "Maharashtra", "district": "Pune", "city": "Pune"},
    "411038": {"state": "Maharashtra", "district": "Pune", "city": "Pune"},
    "440001": {"state": "Maharashtra", "district": "Nagpur", "city": "Nagpur"},
    "422001": {"state": "Maharashtra", "district": "Nashik", "city": "Nashik"},

    # Bangalore / Karnataka
    "560001": {"state": "Karnataka", "district": "Bangalore", "city": "Bangalore"},
    "560002": {"state": "Karnataka", "district": "Bangalore", "city": "Bangalore"},
    "560004": {"state": "Karnataka", "district": "Bangalore", "city": "Bangalore"},
    "560008": {"state": "Karnataka", "district": "Bangalore", "city": "Bangalore"},
    "560011": {"state": "Karnataka", "district": "Bangalore", "city": "Bangalore"},
    "560034": {"state": "Karnataka", "district": "Bangalore", "city": "Bangalore"},
    "560037": {"state": "Karnataka", "district": "Bangalore", "city": "Bangalore"},
    "560066": {"state": "Karnataka", "district": "Bangalore", "city": "Bangalore"},
    "560078": {"state": "Karnataka", "district": "Bangalore", "city": "Bangalore"},
    "560100": {"state": "Karnataka", "district": "Bangalore Rural", "city": "Bangalore"},
    "570001": {"state": "Karnataka", "district": "Mysore", "city": "Mysore"},
    "580001": {"state": "Karnataka", "district": "Dharwad", "city": "Hubli"},

    # Kolkata / West Bengal
    "700001": {"state": "West Bengal", "district": "Kolkata", "city": "Kolkata"},
    "700006": {"state": "West Bengal", "district": "Kolkata", "city": "Kolkata"},
    "700020": {"state": "West Bengal", "district": "Kolkata", "city": "Kolkata"},
    "700064": {"state": "West Bengal", "district": "South 24 Parganas", "city": "Kolkata"},
    "700091": {"state": "West Bengal", "district": "Kolkata", "city": "Kolkata"},
    "700100": {"state": "West Bengal", "district": "North 24 Parganas", "city": "Kolkata"},
    "711101": {"state": "West Bengal", "district": "Howrah", "city": "Howrah"},

    # Chennai / Tamil Nadu
    "600001": {"state": "Tamil Nadu", "district": "Chennai", "city": "Chennai"},
    "600002": {"state": "Tamil Nadu", "district": "Chennai", "city": "Chennai"},
    "600017": {"state": "Tamil Nadu", "district": "Chennai", "city": "Chennai"},
    "600028": {"state": "Tamil Nadu", "district": "Chennai", "city": "Chennai"},
    "600040": {"state": "Tamil Nadu", "district": "Chennai", "city": "Chennai"},
    "600096": {"state": "Tamil Nadu", "district": "Kancheepuram", "city": "Chennai"},
    "641001": {"state": "Tamil Nadu", "district": "Coimbatore", "city": "Coimbatore"},
    "625001": {"state": "Tamil Nadu", "district": "Madurai", "city": "Madurai"},

    # Hyderabad / Telangana
    "500001": {"state": "Telangana", "district": "Hyderabad", "city": "Hyderabad"},
    "500003": {"state": "Telangana", "district": "Hyderabad", "city": "Hyderabad"},
    "500016": {"state": "Telangana", "district": "Hyderabad", "city": "Hyderabad"},
    "500034": {"state": "Telangana", "district": "Hyderabad", "city": "Hyderabad"},
    "500072": {"state": "Telangana", "district": "Rangareddi", "city": "Hyderabad"},
    "500081": {"state": "Telangana", "district": "Rangareddi", "city": "Hyderabad"},
    "500090": {"state": "Telangana", "district": "Medchal-Malkajgiri", "city": "Hyderabad"},
    "530001": {"state": "Andhra Pradesh", "district": "Visakhapatnam", "city": "Visakhapatnam"},
    "520001": {"state": "Andhra Pradesh", "district": "Krishna", "city": "Vijayawada"},

    # Jaipur / Rajasthan
    "302001": {"state": "Rajasthan", "district": "Jaipur", "city": "Jaipur"},
    "302004": {"state": "Rajasthan", "district": "Jaipur", "city": "Jaipur"},
    "302012": {"state": "Rajasthan", "district": "Jaipur", "city": "Jaipur"},
    "302015": {"state": "Rajasthan", "district": "Jaipur", "city": "Jaipur"},
    "302020": {"state": "Rajasthan", "district": "Jaipur", "city": "Jaipur"},
    "342001": {"state": "Rajasthan", "district": "Jodhpur", "city": "Jodhpur"},
    "313001": {"state": "Rajasthan", "district": "Udaipur", "city": "Udaipur"},

    # Lucknow / UP
    "226001": {"state": "Uttar Pradesh", "district": "Lucknow", "city": "Lucknow"},
    "226010": {"state": "Uttar Pradesh", "district": "Lucknow", "city": "Lucknow"},
    "226016": {"state": "Uttar Pradesh", "district": "Lucknow", "city": "Lucknow"},
    "226024": {"state": "Uttar Pradesh", "district": "Lucknow", "city": "Lucknow"},
    "208001": {"state": "Uttar Pradesh", "district": "Kanpur Nagar", "city": "Kanpur"},
    "211001": {"state": "Uttar Pradesh", "district": "Allahabad", "city": "Prayagraj"},
    "221001": {"state": "Uttar Pradesh", "district": "Varanasi", "city": "Varanasi"},
    "250001": {"state": "Uttar Pradesh", "district": "Meerut", "city": "Meerut"},
    "282001": {"state": "Uttar Pradesh", "district": "Agra", "city": "Agra"},

    # Ahmedabad / Gujarat
    "380001": {"state": "Gujarat", "district": "Ahmedabad", "city": "Ahmedabad"},
    "380006": {"state": "Gujarat", "district": "Ahmedabad", "city": "Ahmedabad"},
    "380013": {"state": "Gujarat", "district": "Ahmedabad", "city": "Ahmedabad"},
    "380015": {"state": "Gujarat", "district": "Ahmedabad", "city": "Ahmedabad"},
    "395001": {"state": "Gujarat", "district": "Surat", "city": "Surat"},
    "390001": {"state": "Gujarat", "district": "Vadodara", "city": "Vadodara"},
    "360001": {"state": "Gujarat", "district": "Rajkot", "city": "Rajkot"},

    # Bhopal / MP
    "462001": {"state": "Madhya Pradesh", "district": "Bhopal", "city": "Bhopal"},
    "452001": {"state": "Madhya Pradesh", "district": "Indore", "city": "Indore"},
    "482001": {"state": "Madhya Pradesh", "district": "Jabalpur", "city": "Jabalpur"},

    # Patna / Bihar
    "800001": {"state": "Bihar", "district": "Patna", "city": "Patna"},
    "800004": {"state": "Bihar", "district": "Patna", "city": "Patna"},
    "800020": {"state": "Bihar", "district": "Patna", "city": "Patna"},

    # Others
    "751001": {"state": "Odisha", "district": "Khurda", "city": "Bhubaneswar"},
    "160001": {"state": "Chandigarh", "district": "Chandigarh", "city": "Chandigarh"},
    "141001": {"state": "Punjab", "district": "Ludhiana", "city": "Ludhiana"},
    "143001": {"state": "Punjab", "district": "Amritsar", "city": "Amritsar"},
    "180001": {"state": "Jammu and Kashmir", "district": "Jammu", "city": "Jammu"},
    "190001": {"state": "Jammu and Kashmir", "district": "Srinagar", "city": "Srinagar"},
    "682001": {"state": "Kerala", "district": "Ernakulam", "city": "Kochi"},
    "695001": {"state": "Kerala", "district": "Thiruvananthapuram", "city": "Thiruvananthapuram"},
    "781001": {"state": "Assam", "district": "Kamrup Metro", "city": "Guwahati"},
    "834001": {"state": "Jharkhand", "district": "Ranchi", "city": "Ranchi"},
    "440001": {"state": "Maharashtra", "district": "Nagpur", "city": "Nagpur"},
}

# Prefix-based fallback: first 2-3 digits of pincode → state
# Used when exact pincode is not in the map
PINCODE_PREFIX_MAP = {
    "11": {"state": "Delhi", "district": "New Delhi", "city": "Delhi"},
    "12": {"state": "Haryana", "district": "Gurgaon", "city": "Gurgaon"},
    "13": {"state": "Punjab", "district": "Ludhiana", "city": "Punjab"},
    "14": {"state": "Punjab", "district": "Amritsar", "city": "Punjab"},
    "15": {"state": "Himachal Pradesh", "district": "Shimla", "city": "Shimla"},
    "16": {"state": "Chandigarh", "district": "Chandigarh", "city": "Chandigarh"},
    "17": {"state": "Himachal Pradesh", "district": "Shimla", "city": "Shimla"},
    "18": {"state": "Jammu and Kashmir", "district": "Jammu", "city": "Jammu"},
    "19": {"state": "Jammu and Kashmir", "district": "Srinagar", "city": "Srinagar"},
    "20": {"state": "Uttar Pradesh", "district": "Ghaziabad", "city": "UP West"},
    "21": {"state": "Uttar Pradesh", "district": "Allahabad", "city": "UP East"},
    "22": {"state": "Uttar Pradesh", "district": "Lucknow", "city": "Lucknow"},
    "23": {"state": "Uttar Pradesh", "district": "Lucknow", "city": "UP Central"},
    "24": {"state": "Uttar Pradesh", "district": "Bareilly", "city": "UP North"},
    "25": {"state": "Uttar Pradesh", "district": "Meerut", "city": "UP West"},
    "26": {"state": "Uttarakhand", "district": "Dehradun", "city": "Dehradun"},
    "27": {"state": "Uttar Pradesh", "district": "Varanasi", "city": "UP East"},
    "28": {"state": "Uttar Pradesh", "district": "Agra", "city": "UP West"},
    "30": {"state": "Rajasthan", "district": "Jaipur", "city": "Jaipur"},
    "31": {"state": "Rajasthan", "district": "Alwar", "city": "Rajasthan"},
    "32": {"state": "Rajasthan", "district": "Udaipur", "city": "Rajasthan"},
    "33": {"state": "Rajasthan", "district": "Jodhpur", "city": "Rajasthan"},
    "34": {"state": "Rajasthan", "district": "Jodhpur", "city": "Rajasthan"},
    "36": {"state": "Gujarat", "district": "Rajkot", "city": "Gujarat"},
    "37": {"state": "Gujarat", "district": "Bhavnagar", "city": "Gujarat"},
    "38": {"state": "Gujarat", "district": "Ahmedabad", "city": "Ahmedabad"},
    "39": {"state": "Gujarat", "district": "Surat", "city": "Surat"},
    "40": {"state": "Maharashtra", "district": "Mumbai", "city": "Mumbai"},
    "41": {"state": "Maharashtra", "district": "Pune", "city": "Pune"},
    "42": {"state": "Maharashtra", "district": "Nashik", "city": "Maharashtra"},
    "43": {"state": "Maharashtra", "district": "Aurangabad", "city": "Maharashtra"},
    "44": {"state": "Maharashtra", "district": "Nagpur", "city": "Nagpur"},
    "45": {"state": "Madhya Pradesh", "district": "Indore", "city": "Indore"},
    "46": {"state": "Madhya Pradesh", "district": "Bhopal", "city": "Bhopal"},
    "47": {"state": "Madhya Pradesh", "district": "Jabalpur", "city": "MP"},
    "48": {"state": "Madhya Pradesh", "district": "Rewa", "city": "MP"},
    "49": {"state": "Chhattisgarh", "district": "Raipur", "city": "Chhattisgarh"},
    "50": {"state": "Telangana", "district": "Hyderabad", "city": "Hyderabad"},
    "51": {"state": "Andhra Pradesh", "district": "Kurnool", "city": "AP"},
    "52": {"state": "Andhra Pradesh", "district": "Krishna", "city": "AP"},
    "53": {"state": "Andhra Pradesh", "district": "Visakhapatnam", "city": "Vizag"},
    "56": {"state": "Karnataka", "district": "Bangalore", "city": "Bangalore"},
    "57": {"state": "Karnataka", "district": "Mysore", "city": "Karnataka"},
    "58": {"state": "Karnataka", "district": "Dharwad", "city": "Karnataka"},
    "60": {"state": "Tamil Nadu", "district": "Chennai", "city": "Chennai"},
    "61": {"state": "Tamil Nadu", "district": "Tiruchirappalli", "city": "TN"},
    "62": {"state": "Tamil Nadu", "district": "Madurai", "city": "TN"},
    "63": {"state": "Tamil Nadu", "district": "Salem", "city": "TN"},
    "64": {"state": "Tamil Nadu", "district": "Coimbatore", "city": "Coimbatore"},
    "67": {"state": "Kerala", "district": "Kozhikode", "city": "Kerala"},
    "68": {"state": "Kerala", "district": "Ernakulam", "city": "Kochi"},
    "69": {"state": "Kerala", "district": "Thiruvananthapuram", "city": "Kerala"},
    "70": {"state": "West Bengal", "district": "Kolkata", "city": "Kolkata"},
    "71": {"state": "West Bengal", "district": "Howrah", "city": "West Bengal"},
    "73": {"state": "West Bengal", "district": "Murshidabad", "city": "West Bengal"},
    "75": {"state": "Odisha", "district": "Khurda", "city": "Odisha"},
    "76": {"state": "Odisha", "district": "Cuttack", "city": "Odisha"},
    "78": {"state": "Assam", "district": "Kamrup", "city": "Guwahati"},
    "80": {"state": "Bihar", "district": "Patna", "city": "Patna"},
    "81": {"state": "Bihar", "district": "Muzaffarpur", "city": "Bihar"},
    "82": {"state": "Bihar", "district": "Bhagalpur", "city": "Bihar"},
    "83": {"state": "Jharkhand", "district": "Ranchi", "city": "Jharkhand"},
}


def lookup_pincode(pincode: str) -> dict | None:
    """
    Look up location details for a given pincode.
    Returns {state, district, city} or None if not found.
    Tries exact match first, then prefix-based fallback.
    """
    pincode = str(pincode).strip()

    # Exact match
    if pincode in PINCODE_MAP:
        return PINCODE_MAP[pincode]

    # Try 3-digit prefix (some areas share prefix patterns)
    prefix3 = pincode[:3]
    for pin, loc in PINCODE_MAP.items():
        if pin.startswith(prefix3):
            return loc

    # Fallback to 2-digit prefix
    prefix2 = pincode[:2]
    if prefix2 in PINCODE_PREFIX_MAP:
        return PINCODE_PREFIX_MAP[prefix2]

    # Default to Delhi if nothing matches
    return {"state": "Delhi", "district": "New Delhi", "city": "Delhi"}


def get_city_name(pincode: str) -> str:
    """Get the city name for a pincode."""
    loc = lookup_pincode(pincode)
    return loc["city"] if loc else "Unknown"
