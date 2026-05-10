# 🎯 Antigravity HR: AI Talent Agent

A premium, AI-powered HR agent that automates the candidate screening process. It parses Job Descriptions (JD), evaluates resumes/LinkedIn data, and provides a ranked shortlist with transparent scoring justification.

## 🚀 Features

- **JD Requirements Extraction**: Automatically identifies skills, experience, and education from any JD text.
- **Multiformat Ingestion**: Supports PDF, DOCX, and LinkedIn JSON profiles.
- **5-Dimension Scoring**:
  - Skills Match (30%)
  - Experience Relevance (25%)
  - Education & Certifications (15%)
  - Project/Portfolio (20%)
  - Communication Quality (10%)
- **Human-in-the-Loop**: Admin dashboard to override scores with justifications.
- **Premium UI**: Modern glassmorphic design with real-time feedback.
- **Detailed Reports**: Exportable HTML/PDF shortlisting reports.

## 🛠️ Tech Stack

- **Backend**: FastAPI, LangChain, Google Gemini 1.5 Pro
- **Frontend**: React (Vite), Framer Motion, Lucide Icons, Vanilla CSS
- **Parsing**: PyMuPDF, python-docx

## 🏃 Getting Started

### 1. Backend Setup
1. Fill in your `GOOGLE_API_KEY` in `backend/.env`.
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run the server:
   ```bash
   python backend/main.py
   ```

### 2. Frontend Setup
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Run the development server:
   ```bash
   npm run dev
   ```

## 📄 License
MIT
