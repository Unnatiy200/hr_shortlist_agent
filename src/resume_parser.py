import os
import json
import re
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from typing import List
import pdfplumber
from docx import Document

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Pydantic model ──────────────────────────────────────────
class CandidateProfile(BaseModel):
    name: str
    source_type: str
    experience_years: int
    skills: List[str]
    education: str
    domain: str
    projects: List[str]
    raw_text: str

# ── PII Masking (security requirement) ──────────────────────
def mask_pii(text: str) -> str:
    # mask email addresses
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL]', text)
    # mask phone numbers
    text = re.sub(r'(\+?\d[\d\s\-]{8,}\d)', '[PHONE]', text)
    # mask Aadhar numbers (India)
    text = re.sub(r'\b\d{4}\s\d{4}\s\d{4}\b', '[AADHAR]', text)
    return text

# ── Extract text from PDF ────────────────────────────────────
def extract_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

# ── Extract text from DOCX ───────────────────────────────────
def extract_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return text.strip()

# ── Extract text from LinkedIn JSON ─────────────────────────
def extract_from_linkedin(data: dict) -> str:
    parts = []
    if data.get("name"): parts.append(f"Name: {data['name']}")
    if data.get("headline"): parts.append(f"Headline: {data['headline']}")
    if data.get("summary"): parts.append(f"Summary: {data['summary']}")
    if data.get("experience"): parts.append(f"Experience: {data['experience']}")
    if data.get("education"): parts.append(f"Education: {data['education']}")
    if data.get("skills"): parts.append(f"Skills: {data['skills']}")
    return "\n".join(parts)

# ── Parse with LLM ───────────────────────────────────────────
def parse_with_llm(raw_text: str, name: str = "Unknown") -> CandidateProfile:
    masked_text = mask_pii(raw_text)
    masked_text = masked_text[:3000]

    system_prompt = """You are a resume parser for an HR system.
Extract structured information from the resume text.
Return ONLY valid JSON — no markdown, no explanation, no extra text.
Use exactly this schema:
{
  "name": "candidate full name",
  "source_type": "resume",
  "experience_years": 0,
  "skills": ["list", "of", "technical", "skills"],
  "education": "highest education qualification",
  "domain": "primary domain or industry",
  "projects": ["project 1 description", "project 2 description"]
}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Parse this resume:\n\n{masked_text}"}
        ],
        temperature=0.1
    )

    raw = response.choices[0].message.content
    raw = raw.replace("```json", "").replace("```", "").strip()

    parsed = json.loads(raw)
    parsed["raw_text"] = masked_text
    return CandidateProfile(**parsed)

# ── Main parse function ───────────────────────────────────────
def parse_resume(file_path: str = None, linkedin_data: dict = None) -> CandidateProfile:
    if file_path:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            raw_text = extract_from_pdf(file_path)
            source = "PDF"
        elif ext in [".docx", ".doc"]:
            raw_text = extract_from_docx(file_path)
            source = "DOCX"
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    elif linkedin_data:
        raw_text = extract_from_linkedin(linkedin_data)
        source = "LinkedIn"
    else:
        raise ValueError("Provide either file_path or linkedin_data")

    profile = parse_with_llm(raw_text)
    profile.source_type = source
    return profile


# ── Test it ──────────────────────────────────────────────────
if __name__ == "__main__":
    sample_linkedin = {
        "name": "Priya Sharma",
        "headline": "Senior ML Engineer at Google Brain",
        "summary": "7 years experience in ML engineering. Expert in PyTorch, LLM fine-tuning, RAG pipelines.",
        "experience": "Google Brain 5 years, Spotify 2 years. Led recommendation system for 100M users.",
        "education": "PhD Computer Science, Stanford University",
        "skills": "Python, PyTorch, TensorFlow, Kubernetes, SageMaker, Docker, LLMOps, Vector DB"
    }

    result = parse_resume(linkedin_data=sample_linkedin)
    print("\n✅ Resume Parsed Successfully!")
    print(f"Name: {result.name}")
    print(f"Source: {result.source_type}")
    print(f"Experience: {result.experience_years} years")
    print(f"Skills: {result.skills}")
    print(f"Education: {result.education}")
    print(f"Domain: {result.domain}")
    print(f"Projects: {result.projects}")