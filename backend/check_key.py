import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

try:
    # Try a very simple model list call
    models = genai.list_models()
    print("API Key check: VALID")
except Exception as e:
    print(f"API Key check: FAILED - {e}")
