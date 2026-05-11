import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key
    )
    res = llm.invoke("Hi")
    print("Model gemini-2.5-flash works!")
    print(res.content)
except Exception as e:
    print(f"Model gemini-2.5-flash FAILED: {e}")

try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key
    )
    res = llm.invoke("Hi")
    print("Model gemini-1.5-flash works!")
except Exception as e:
    print(f"Model gemini-1.5-flash FAILED: {e}")
