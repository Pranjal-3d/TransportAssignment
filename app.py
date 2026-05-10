import streamlit as st
import pandas as pd
import os
import json
from agents.scorer import HRScorer
from utils.parsers import get_candidate_text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(page_title="AI HR Agent | Candidate Shortlisting", page_icon="🎯", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
    }
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }
    .card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    h1, h2, h3 {
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    .metric-card {
        text-align: center;
        padding: 15px;
        background: rgba(99, 102, 241, 0.1);
        border-radius: 10px;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Initialization
if 'candidates' not in st.session_state:
    st.session_state.candidates = []
if 'jd_reqs' not in st.session_state:
    st.session_state.jd_reqs = None
if 'overrides' not in st.session_state:
    st.session_state.overrides = {}

def main():
    st.title("🎯 HR Agent: Intelligent Shortlisting")
    st.markdown("---")

    # API Key Handling
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        st.warning("Please provide a Gemini API Key in the sidebar or .env file.")
        st.stop()

    scorer = HRScorer(api_key=api_key)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.header("Step 1: Job Description")
        jd_input = st.text_area("Paste the Job Description here", height=250, placeholder="We are looking for a Senior Python Developer with...")
        if st.button("Parse Requirements"):
            if jd_input:
                with st.spinner("Analyzing JD..."):
                    try:
                        st.session_state.jd_reqs = scorer.parse_jd(jd_input)
                        st.success("JD Parsed Successfully!")
                    except Exception as e:
                        st.error(f"Error parsing JD: {e}")
            else:
                st.error("Please paste a JD.")

        if st.session_state.jd_reqs:
            with st.expander("Extracted Requirements", expanded=True):
                reqs = st.session_state.jd_reqs
                st.write(f"**Domain:** {reqs.domain}")
                st.write(f"**Experience:** {reqs.experience_years}")
                st.write(f"**Education:** {', '.join(reqs.education)}")
                st.write(f"**Top Skills:** {', '.join(reqs.skills)}")

    with col2:
        st.header("Step 2: Candidate Profiles")
        uploaded_files = st.file_uploader("Upload Resumes (PDF/DOCX) or LinkedIn Data (JSON)", accept_multiple_files=True, type=['pdf', 'docx', 'json'])
        
        if st.button("Generate Shortlist"):
            if not st.session_state.jd_reqs:
                st.error("Please parse a JD first.")
            elif not uploaded_files:
                st.error("Please upload at least one resume.")
            else:
                st.session_state.candidates = []
                progress_bar = st.progress(0)
                for i, file in enumerate(uploaded_files):
                    with st.spinner(f"Evaluating {file.name}..."):
                        # Save temp file
                        temp_path = os.path.join("temp_uploads", file.name)
                        os.makedirs("temp_uploads", exist_ok=True)
                        with open(temp_path, "wb") as f:
                            f.write(file.getbuffer())
                        
                        try:
                            candidate_text = get_candidate_text(temp_path)
                            score_res = scorer.score_candidate(st.session_state.jd_reqs, candidate_text)
                            
                            st.session_state.candidates.append({
                                "name": file.name,
                                "scores": score_res,
                                "original_score": score_res.total_weighted_score
                            })
                        except Exception as e:
                            st.error(f"Error evaluating {file.name}: {e}")
                        
                        progress_bar.progress((i + 1) / len(uploaded_files))
                
                st.success(f"Processed {len(st.session_state.candidates)} candidates!")

    # Display Results
    if st.session_state.candidates:
        st.markdown("---")
        st.header("Step 3: Ranked Shortlist")
        
        # Sort candidates
        ranked_candidates = sorted(st.session_state.candidates, 
                                   key=lambda x: st.session_state.overrides.get(x['name'], {}).get('new_score', x['original_score']), 
                                   reverse=True)

        for i, cand in enumerate(ranked_candidates):
            name = cand['name']
            orig_score = cand['original_score']
            override_data = st.session_state.overrides.get(name, {})
            current_score = override_data.get('new_score', orig_score)
            
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>#{i+1} {name}</h3>
                        <div class="metric-card">
                            <span style="font-size: 0.8rem; opacity: 0.8;">TOTAL SCORE</span><br/>
                            <span style="font-size: 1.5rem; font-weight: bold; color: #818cf8;">{current_score:.2f}/10</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                res = cand['scores']
                
                # Rubric Breakdown
                cols = st.columns(5)
                dims = [
                    ("Skills", res.skills_match),
                    ("Experience", res.experience_relevance),
                    ("Education", res.education_certs),
                    ("Projects", res.project_portfolio),
                    ("Comm", res.communication_quality)
                ]
                
                for idx, (label, data) in enumerate(dims):
                    cols[idx].metric(label, f"{data.score}/10")
                    cols[idx].caption(data.justification)

                st.info(f"**Recommendation:** {res.hire_recommendation}")

                # Override Hook
                with st.expander("Admin Override (Human-in-the-Loop)"):
                    new_score = st.slider(f"Adjust Score for {name}", 0.0, 10.0, float(current_score), key=f"slider_{name}")
                    reason = st.text_input("Reason for override", value=override_data.get('reason', ''), key=f"reason_{name}")
                    if st.button("Apply Override", key=f"btn_{name}"):
                        st.session_state.overrides[name] = {"new_score": new_score, "reason": reason}
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

        # Export Options
        st.markdown("### Export Report")
        col_ex1, col_ex2 = st.columns(2)
        if col_ex1.button("Download JSON Report"):
            report = {
                "jd": st.session_state.jd_reqs.json() if st.session_state.jd_reqs else None,
                "shortlist": ranked_candidates
            }
            st.download_button("Click to Download", data=json.dumps(report, indent=4), file_name="shortlist_report.json")

if __name__ == "__main__":
    main()
