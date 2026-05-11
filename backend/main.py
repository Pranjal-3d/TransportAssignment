from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import shutil
from typing import List, Optional
from pydantic import BaseModel
from agents.scorer import HRScorer, JDRequirements, ScoringResult
from utils.parsers import get_candidate_text
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="HR Agent API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temp storage for files
UPLOAD_DIR = "/tmp/temp_uploads" if os.name != 'nt' else "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Shared state (in-memory for demo, could be SQLite)
class AppState:
    def __init__(self):
        self.jd_reqs: Optional[JDRequirements] = None
        self.candidates = []
        self.overrides = {}

state = AppState()

# Initialize Scorer
api_key = os.getenv("GOOGLE_API_KEY")
scorer = HRScorer(api_key=api_key) if api_key else None

@app.get("/")
def read_root():
    return {"status": "HR Agent API is running"}

@app.post("/parse-jd")
async def parse_jd(jd_text: str = Form(...)):
    if not scorer:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured")
    try:
        state.jd_reqs = scorer.parse_jd(jd_text)
        return state.jd_reqs
    except Exception as e:
        error_msg = f"LLM Error: {str(e)}"
        print(f"JD Parsing Error: {error_msg}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/evaluate-candidates")
async def evaluate_candidates(files: List[UploadFile] = File(...)):
    if not scorer:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured")
    if not state.jd_reqs:
        raise HTTPException(status_code=400, detail="Parse a JD first")

    results = []
    print(f"Received {len(files)} files for evaluation.")
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        print(f"Processing candidate: {file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            text = get_candidate_text(file_path)
            print(f"Extracted {len(text)} characters from {file.filename}")
            
            if len(text) < 50:
                 print(f"Warning: Extracted text for {file.filename} is too short ({len(text)} chars).")

            score_res = scorer.score_candidate(state.jd_reqs, text)
            print(f"Scored {file.filename}: {score_res.total_weighted_score}/10")
            
            candidate_data = {
                "id": file.filename,
                "name": file.filename,
                "scores": score_res,
                "original_score": score_res.total_weighted_score,
                "final_score": score_res.total_weighted_score,
                "override_reason": ""
            }
            results.append(candidate_data)
        except Exception as e:
            import traceback
            print(f"Error processing {file.filename}: {e}")
            traceback.print_exc()
            continue
    
    state.candidates = results
    return results

@app.get("/get-shortlist")
async def get_shortlist():
    return sorted(state.candidates, key=lambda x: x["final_score"], reverse=True)

@app.post("/override-score")
async def override_score(candidate_id: str, new_score: float, reason: str):
    for cand in state.candidates:
        if cand["id"] == candidate_id:
            cand["final_score"] = new_score
            cand["override_reason"] = reason
            return {"status": "success", "candidate": cand}
    raise HTTPException(status_code=404, detail="Candidate not found")

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")

@app.get("/generate-report", response_class=HTMLResponse)
async def generate_report(request: Request):
    return templates.TemplateResponse("report.html", {"request": request, "candidates": sorted(state.candidates, key=lambda x: x["final_score"], reverse=True)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
