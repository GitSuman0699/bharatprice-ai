import asyncio
from app.services.ai_engine import process_message

async def test_groq():
    print("Testing Intent: price_check (Tomato)")
    res1 = await process_message("What is the price of tomato today?", pincode="110001")
    print("\n--- AI RESPONSE 1 ---")
    print(res1["reply"])
    
    print("\n\nTesting Intent: compare (Onion)")
    res2 = await process_message("Should I buy onion from Mandi or JioMart?", pincode="110001")
    print("\n--- AI RESPONSE 2 ---")
    print(res2["reply"])

if __name__ == "__main__":
    asyncio.run(test_groq())
