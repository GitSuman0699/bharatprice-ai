import os
from groq import Groq

api_key = os.environ.get("GROQ_API_KEY") 
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")

client = Groq(api_key=api_key)

try:
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a test assistant."
            },
            {
                "role": "user",
                "content": "Hello"
            }
        ],
        model="llama3-8b-8192",
        temperature=0.3,
        max_tokens=512,
    )
    print(completion.choices[0].message.content)
except Exception as e:
    import traceback
    traceback.print_exc()
