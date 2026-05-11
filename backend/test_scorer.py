import os
from agents.scorer import HRScorer
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
scorer = HRScorer(api_key=api_key)

jd_text = "Software Engineer with 5 years experience in Python and React."
try:
    print("Parsing JD...")
    res = scorer.parse_jd(jd_text)
    print("Success!")
    print(res)
except Exception as e:
    print(f"Failed: {e}")
    import traceback
    traceback.print_exc()
