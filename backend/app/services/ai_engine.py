import json
import logging
import os
from typing import Optional

from app.services.database import (
    get_current_price,
    get_competitor_prices,
    get_mandi_rates,
    get_price_trend,
    find_product_id,
    get_all_products,
    search_products,
)
from app.data.seed_data import find_product_id as find_pid, REGIONS
from app.data.product_mapping import resolve_product_id, get_hindi_name, is_mandi_product

logger = logging.getLogger(__name__)

from dotenv import load_dotenv
import boto3
from botocore.exceptions import BotoCoreError, ClientError

load_dotenv()

BEDROCK_AVAILABLE = True


# ─── Intent Classification ─────────────────────────────────────────

INTENT_KEYWORDS = {
    "price_check": [
        "price", "rate", "cost", "kitna", "kimat", "kya rate", "daam",
        "कीमत", "दाम", "रेट", "कितना", "कितने", "भाव",
        "today", "aaj", "आज",
    ],
    "compare": [
        "compare", "comparison", "vs", "versus", "competitor",
        "tulna", "तुलना", "compare karo", "तुलना करो",
        "bigbasket", "jiomart", "online",
    ],
    "mandi": [
        "mandi", "wholesale", "मंडी", "thok", "थोक",
    ],
    "trend": [
        "trend", "history", "itihas", "past", "week", "month",
        "इतिहास", "ट्रेंड", "graph", "chart", "badha", "gira", "बढ़ा", "गिरा",
    ],
    "forecast": [
        "forecast", "predict", "future", "demand", "upcoming",
        "भविष्य", "अनुमान", "festival", "season",
    ],
    "help": [
        "help", "madad", "मदद", "kaise", "कैसे", "kya kar sakte", "क्या कर सकते",
        "features", "menu",
    ],
    "greeting": [
        "hello", "hi", "hey", "namaste", "namaskar",
        "नमस्ते", "नमस्कार", "हेलो",
    ],
    "product_list": [
        "list", "products", "items", "saman", "सामान",
        "kya kya", "क्या क्या", "catalog",
    ],
}


def classify_intent(message: str) -> str:
    """Classify user message intent based on keywords."""
    msg_lower = message.lower().strip()

    scores = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in msg_lower)
        if score > 0:
            scores[intent] = score

    if not scores:
        if resolve_product_id(msg_lower) or find_pid(msg_lower):
            return "price_check"
        return "general"

    return max(scores, key=scores.get)


def extract_product(message: str) -> Optional[str]:
    """Extract product name/ID from message."""
    resolved = resolve_product_id(message)
    if resolved:
        return resolved
    return find_pid(message)


def extract_region(message: str) -> str:
    """Extract region from message, default to delhi."""
    msg_lower = message.lower()
    for region_id, region_data in REGIONS.items():
        if region_id in msg_lower or region_data["city"].lower() in msg_lower:
            return region_id
    return "delhi"


# ─── Data Context Fetchers ──────────────────────────────────────────

def _fetch_price_context(product_query: str, region: str, pincode: str | None = None, state: str | None = None, district: str | None = None) -> dict:
    price_data = get_current_price(product_query, region, pincode=pincode, state=state, district=district)
    if not price_data:
        return {"error": f"No pricing data found for {product_query}"}
    
    city = price_data.region if pincode else REGIONS.get(region, {}).get("city", "your area")

    # Build accurate source badge
    if pincode and state:
        source_badge = "Live data from data.gov.in (AGMARKNET) + BigBasket"
    elif pincode:
        source_badge = "Real-time data from data.gov.in (AGMARKNET)"
    else:
        source_badge = "Estimated data (set your pincode for live prices)"

    # Resolve product ID to check if it's mandi-eligible
    product_id = resolve_product_id(product_query)
    has_mandi = product_id and is_mandi_product(product_id)

    context = {
        "context_type": "current_price",
        "product": price_data.product_name,
        "location": city,
        "bigbasket_price": price_data.bigbasket_price,
        "jiomart_price": price_data.jiomart_price,
        "local_market_average": price_data.local_avg,
        "recommended_selling_price": price_data.recommended_retail,
        "unit": price_data.unit,
        "demand_trend": price_data.demand_trend,
        "data_source": source_badge,
    }

    # Only include mandi data for products actually traded in mandis
    if has_mandi and price_data.mandi_price > 0:
        context["mandi_wholesale_price"] = price_data.mandi_price
        context["profit_margin_tip"] = f"Buying at mandi rate ({price_data.mandi_price}) and selling at {price_data.recommended_retail} gives ~{((price_data.recommended_retail - price_data.mandi_price) / price_data.mandi_price * 100):.0f}% margin."
    else:
        context["note"] = "This product is not traded in wholesale mandis. Prices are from retail/online sources."

    return context

def _fetch_comparison_context(product_query: str, region: str, pincode: str | None = None, state: str | None = None, district: str | None = None) -> dict:
    comparison = get_competitor_prices(product_query, region, pincode=pincode, state=state, district=district)
    if not comparison:
        return {"error": f"No comparison data for {product_query}"}
    return {"context_type": "competitor_comparison", "data": comparison}

def _fetch_mandi_context(product_query: str, region: str, pincode: str | None = None, state: str | None = None, district: str | None = None) -> dict:
    rates = get_mandi_rates(product_query, region, pincode=pincode, state=state, district=district)
    if not rates:
        return {"error": f"No mandi rates for {product_query}"}
    
    rates_data = [{"market": r.mandi_name, "location": r.location, "price": r.price, "unit": r.unit} for r in rates]
    return {"context_type": "mandi_wholesale_rates", "data": rates_data}

def _fetch_trend_context(product_query: str, region: str) -> dict:
    trend = get_price_trend(product_query, region)
    if not trend:
        return {"error": f"No trend data for {product_query}"}
    return {
        "context_type": "price_trend",
        "product": trend.product_name,
        "current_price": trend.current_price,
        "trend_direction": trend.trend,
        "price_change_percent": trend.price_change_pct,
        "analysis": trend.summary
    }

def _fetch_forecast_context(product_query: str, region: str, pincode: str | None = None, state: str | None = None, district: str | None = None) -> dict:
    price_data = get_current_price(product_query, region, pincode=pincode, state=state, district=district)
    if not price_data:
        return {"error": f"No forecast data for {product_query}"}
    return {
        "context_type": "demand_forecast",
        "product": price_data.product_name,
        "current_demand": price_data.demand_trend,
        "forecast_factors": ["Holi (Mid-March): +15-20% demand for dairy", "Summer Season approaching: Rising demand for cold beverages & fruits"],
        "recommendation": "Stock up 20% more if trend is rising. Pre-order from mandi."
    }


# ─── LLM Generation (Bedrock) ────────────────────────────────

def _get_bedrock_client():
    if BEDROCK_AVAILABLE:
        try:
            return boto3.client(
                service_name='bedrock-runtime',
                region_name="ap-south-1"
            )
        except Exception as e:
            logger.warning(f"Could not init Bedrock client: {e}")
    return None

async def generate_ai_response(message: str, data_context: dict, language: str = "en", chat_history: list = None) -> str:
    """Generate a dynamic response using Amazon Bedrock (Claude 3 Haiku) based on the scraped data context."""
    
    # If no data found AND no chat history, return standard fallback early.
    # But if there IS chat history, let the LLM use it to answer follow-up questions.
    if "error" in data_context and not chat_history:
        return f"I'm sorry, I couldn't find exact pricing data for that. Please try asking about common staples like Tomato, Onion, Potato, Atta, or Rice."

    client = _get_bedrock_client()
    if not client:
        # Fallback to a static string if no LLM is available
        logger.error("LLM Client not available. Falling back to simple string dump.")
        return f"Error connecting to AI. Here is the raw data: {json.dumps(data_context, indent=2)}"

    language_instruction = {
        "hi": "Respond entirely in Hindi (Devanagari script). Be very helpful and conversational like a friendly local advisor.",
        "en": "Respond in English. Be professional, concise, and friendly.",
        "ta": "Respond in Tamil script.",
        "te": "Respond in Telugu script.",
        "mr": "Respond in Marathi (Devanagari script).",
    }.get(language, "Respond in English.")

    disclaimers = {
        "hi": "⚠️ **अस्वीकरण:** **भारतप्राइस एआई बाजार के उतार-चढ़ाव के कारण गलतियां कर सकता है। कीमतें data.gov.in (AGMARKNET) और ऑनलाइन बाजारों से ली गई हैं।**",
        "en": "⚠️ **Disclaimer:** **BharatPrice AI can make mistakes due to fluctuating market conditions and data delays. Prices are aggregated from sources like data.gov.in (AGMARKNET) and online marketplaces.**"
    }
    disclaimer_text = disclaimers.get(language, disclaimers["en"])

    prompt = f"""You are BharatPrice AI, a highly intelligent pricing assistant for Indian Kirana (grocery) store owners.
Your job is to answer the user's specific question using the provided real-time market data context AND any previous conversation history.

CRITICAL INSTRUCTIONS:
1. {language_instruction}
2. Directly answer what the user asked. If they asked for a comparison, focus on the comparison. If they asked for a price, give the price clearly.
3. ALWAYS list ALL available prices from the context in your response using bullet points. This includes BigBasket price, JioMart price, Local Market Average, Mandi Wholesale Price (if available), and Recommended Selling Price. Never omit any price.
4. Provide the 'Profit Margin Tip' if available.
5. Embellish your response with proper formatting (bolding, bullet points) and relevant emojis to make it easy to read on a mobile phone.
6. Use the symbol ₹ for all currency values.
7. If the user asks a follow-up question (e.g., "which is cheaper?", "what about onion?", "what was the mandi price?"), use the CONVERSATION HISTORY to understand what they're referring to and answer accordingly. Do NOT say "I don't have previous information" if the conversation history contains the answer.
8. RIGHT BEFORE the disclaimer, add a line showing the data source from the context. Format it as: 📡 **Data Source:** [value of data_source from context]
9. AT THE VERY END of your response, you MUST append this exact markdown text with empty lines before and after it:
   
   ---
   
   > {disclaimer_text}


REAL-TIME MARKET DATA CONTEXT (Use this to answer):
{json.dumps(data_context, indent=2)}

USER QUESTION:
"{message}"
"""

    try:
        # Build messages array with optional conversation history for context
        messages = []
        if chat_history:
            messages.extend(chat_history)
        messages.append({
            "role": "user",
            "content": prompt
        })

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "temperature": 0.3,
            "system": "You are BharatPrice AI, the ultimate data-driven pricing assistant for Kirana stores.",
            "messages": messages
        })
        
        response = client.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=body
        )
        
        response_body = json.loads(response.get("body").read())
        return response_body.get("content")[0].get("text")
        
    except (ClientError, BotoCoreError) as e:
        logger.error(f"Bedrock Claude call failed: {e}. Trying fallback model...")
        
        # Fallback to Amazon Titan if Claude access is not yet approved
        try:
            fallback_body = json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 512,
                    "temperature": 0.3,
                }
            })
            fallback_response = client.invoke_model(
                modelId="amazon.titan-text-lite-v1",
                body=fallback_body
            )
            fallback_body_res = json.loads(fallback_response.get("body").read())
            return fallback_body_res.get("results")[0].get("outputText")
            
        except (ClientError, BotoCoreError) as fallback_e:
            logger.error(f"Bedrock Titan Fallback failed: {fallback_e}")
            return f"Model access pending. Please approve Amazon Titan or Anthropic Claude in AWS Console. Status: {e}"


# ─── Main Chat Handler ─────────────────────────────────────────────

async def process_message(
    message: str,
    user_id: str = "demo_user",
    language: str = "en",
    region: str = "delhi",
    pincode: str | None = None,
    state: str | None = None,
    district: str | None = None,
    chat_history: list = None,
) -> dict:
    """Process a user message, fetch context, and generate an AI response."""

    intent = classify_intent(message)
    product_id = extract_product(message)
    product_name = product_id or message 

    extracted_region = extract_region(message)

    # If the user explicitly asks for a region in their message (e.g., "in Mumbai"), prioritize it.
    if extracted_region and extracted_region != "delhi":  # Assuming 'delhi' is the fallback in extract_region
        resolved_region = extracted_region
    # Otherwise, fallback to GPS data (state/district/pincode) or default region.
    elif state and district and region:
        resolved_region = region
    elif region and region in REGIONS:
        resolved_region = region
    else:
        resolved_region = extracted_region

    if state and district:
        logger.info(f"Processing with GPS State: {state}, District: {district}, Pincode: {pincode}")

    data_context = {}
    suggestions = []

    # Fetch factual data based on intent
    if intent in ["greeting", "help"]:
        # No specific product data needed
        data_context = {
            "context_type": "general_help",
            "capabilities": [
                "I can tell you today's wholesale mandi rates.",
                "I can scrape online competitors like BigBasket.",
                "I can recommend the perfect retail selling price.",
                "I can analyze price trends and forecast demand."
            ],
            "data_source": "BharatPrice AI Engine"
        }
        suggestions = ["Aaj atta ka rate kya hai?", "Compare tomato prices", "Show mandi rates for onion"]

    elif intent == "product_list":
        products = get_all_products()
        cat_list = list(set([p["category"] for p in products]))
        data_context = {"context_type": "product_catalog", "categories_supported": cat_list, "total_products": len(products), "data_source": "BharatPrice Catalog"}
        suggestions = ["Price of atta", "Tomato price trend", "Compare paneer prices"]

    elif intent == "price_check":
        data_context = _fetch_price_context(product_name, resolved_region, pincode=pincode, state=state, district=district)
        suggestions = [f"Compare {product_name} prices", f"Mandi rates for {product_name}", f"Price trend of {product_name}"]

    elif intent == "compare":
        data_context = _fetch_comparison_context(product_name, resolved_region, pincode=pincode, state=state, district=district)
        data_context["data_source"] = "BigBasket Scraper + Mandi Data"
        suggestions = [f"Mandi rates for {product_name}", f"Price trend of {product_name}"]

    elif intent == "mandi":
        data_context = _fetch_mandi_context(product_name, resolved_region, pincode=pincode, state=state, district=district)
        data_context["data_source"] = "data.gov.in (AGMARKNET)"
        suggestions = [f"Price of {product_name}", f"Compare {product_name} prices"]

    elif intent == "trend":
        data_context = _fetch_trend_context(product_name, resolved_region)
        data_context["data_source"] = "Historical Mandi Data"
        suggestions = [f"Price of {product_name}", f"Demand forecast for {product_name}"]

    elif intent == "forecast":
        data_context = _fetch_forecast_context(product_name, resolved_region, pincode=pincode, state=state, district=district)
        data_context["data_source"] = "BharatPrice ML Predictions"
        suggestions = [f"Price of {product_name}", f"Mandi rates for {product_name}"]

    else:
        data_context = {"context_type": "unknown_query", "instruction": "Politely inform the user you are a Kirana pricing assistant and ask them to specify a grocery product.", "data_source": "BharatPrice AI"}
        suggestions = ["Price of atta", "Compare tomato prices", "Show mandi rates"]

    # Translate suggestions if language is Hindi
    if language == "hi":
        hi_name = get_hindi_name(product_id) if product_id else product_name
        hi_suggestions = {
            "Aaj atta ka rate kya hai?": "आज आटा का रेट क्या है?",
            "Compare tomato prices": "टमाटर की कीमत की तुलना करें",
            "Show mandi rates for onion": "प्याज का मंडी रेट दिखाएं",
            "Price of atta": "आटा की कीमत",
            "Tomato price trend": "टमाटर का प्राइस ट्रेंड",
            "Compare paneer prices": "पनीर की कीमत की तुलना करें",
            f"Compare {product_name} prices": f"{hi_name} की कीमत की तुलना करें",
            f"Mandi rates for {product_name}": f"{hi_name} का मंडी रेट",
            f"Price trend of {product_name}": f"{hi_name} का प्राइस ट्रेंड",
            f"Price of {product_name}": f"{hi_name} की कीमत",
            f"Demand forecast for {product_name}": f"{hi_name} की डिमांड फोरकास्ट",
            "Show mandi rates": "मंडी रेट दिखाएं",
        }
        suggestions = [hi_suggestions.get(s, s) for s in suggestions]

    # Generate the final natural language response using the LLM
    final_reply = await generate_ai_response(message, data_context, language, chat_history)

    return {
        "reply": final_reply,
        "intent": intent,
        "language": language,
        "suggestions": suggestions,
    }
