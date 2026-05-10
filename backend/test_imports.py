try:
    import langchain
    print("langchain ok")
    from langchain_core.prompts import PromptTemplate
    print("prompts ok")
    import langchain_google_genai
    print("google-genai ok")
except Exception as e:
    print(f"Error: {e}")
