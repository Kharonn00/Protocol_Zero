import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
GOOGLE_KEY = os.getenv("GEMINI_API_KEY")

if not GOOGLE_KEY:
    print("❌ ERROR: No GEMINI_API_KEY found.")
    exit()

print(f"🔑 Connecting...")
client = genai.Client(api_key=GOOGLE_KEY)

print("\n--- 📜 RAW MODEL LIST ---")
try:
    # We loop and print the 'name' attribute, which exists on all Model objects
    for model in client.models.list():
        print(f"Found: {model.name}")
        
    print("\n--- END OF LIST ---")
except Exception as e:
    print(f"❌ ERROR: {e}")