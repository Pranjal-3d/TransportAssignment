import fitz  # PyMuPDF
import docx
import json
import os

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file using PyMuPDF."""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file."""
    text = ""
    try:
        doc = docx.Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text

def parse_linkedin_json(json_data):
    """
    Parse LinkedIn profile JSON data into a structured string.
    Expected format is commonly returned by RapidAPI or similar scrapers.
    """
    if isinstance(json_data, str):
        try:
            json_data = json.loads(json_data)
        except json.JSONDecodeError:
            return "Invalid JSON data"

    profile_text = []
    
    # Basic Info
    full_name = json_data.get("full_name") or f"{json_data.get('first_name', '')} {json_data.get('last_name', '')}".strip()
    if full_name:
        profile_text.append(f"Name: {full_name}")
    
    headline = json_data.get("headline") or json_data.get("occupation")
    if headline:
        profile_text.append(f"Headline: {headline}")
    
    summary = json_data.get("summary") or json_data.get("about")
    if summary:
        profile_text.append(f"Summary: {summary}")

    # Experience
    experiences = json_data.get("experiences") or json_data.get("experience", [])
    if experiences:
        profile_text.append("\nExperience:")
        for exp in experiences:
            title = exp.get("title")
            company = exp.get("company") or exp.get("company_name")
            location = exp.get("location")
            description = exp.get("description")
            period = f"{exp.get('start_date', '')} - {exp.get('end_date', 'Present')}"
            
            profile_text.append(f"- {title} at {company} ({period})")
            if location: profile_text.append(f"  Location: {location}")
            if description: profile_text.append(f"  Description: {description}")

    # Education
    education = json_data.get("education", [])
    if education:
        profile_text.append("\nEducation:")
        for edu in education:
            school = edu.get("school") or edu.get("school_name")
            degree = edu.get("degree") or edu.get("degree_name")
            field = edu.get("field") or edu.get("field_of_study")
            profile_text.append(f"- {degree} in {field} from {school}")

    # Skills
    skills = json_data.get("skills", [])
    if skills:
        if isinstance(skills[0], dict):
            skill_list = [s.get("name") for s in skills if s.get("name")]
        else:
            skill_list = skills
        profile_text.append(f"\nSkills: {', '.join(skill_list)}")

    return "\n".join(profile_text)

def get_candidate_text(file_path):
    """Generic function to get text from any supported file type."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".json":
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return parse_linkedin_json(data)
    else:
        return "Unsupported file format"
