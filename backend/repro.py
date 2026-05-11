import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash-latest")

print(f"API KEY: {api_key}")
print(f"MODEL NAME: {model_name}")

try:
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0,
    )
    res = llm.invoke("Hi")
    print("SUCCESS")
    print(res.content)
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
