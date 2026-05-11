import os
import json
import re
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from typing import List

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Pydantic model ──────────────────────────────────────────
class JDRequirements(BaseModel):
    role: str
    skills: List[str]
    must_have_skills: List[str]
    experience_years: int
    domain: str
    education: str
    soft_skills: List[str]

# ── Input sanitisation (security) ───────────────────────────
def sanitise_input(text: str) -> str:
    text = re.sub(r'<[^>]+>', '', text)        # remove HTML tags
    text = text.strip()
    if not text:
        raise ValueError("JD text cannot be empty")
    return text[:4000]                          # limit to 4000 chars

# ── Main parser function ─────────────────────────────────────
def parse_jd(jd_text: str) -> JDRequirements:
    jd_text = sanitise_input(jd_text)

    system_prompt = """You are a JD parser for an HR system.
Extract structured requirements from the job description.
Return ONLY valid JSON — no markdown, no explanation, no extra text.
Use exactly this schema:
{
  "role": "job title string",
  "skills": ["list", "of", "all", "skills"],
  "must_have_skills": ["only", "mandatory", "skills"],
  "experience_years": 0,
  "domain": "industry or technical domain",
  "education": "minimum education required",
  "soft_skills": ["communication", "teamwork", "etc"]
}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Parse this JD:\n\n{jd_text}"}
        ],
        temperature=0.1
    )

    raw = response.choices[0].message.content
    raw = raw.replace("```json", "").replace("```", "").strip()

    parsed = json.loads(raw)
    return JDRequirements(**parsed)


# ── Test it ──────────────────────────────────────────────────
if __name__ == "__main__":
    sample_jd = """
    Senior Machine Learning Engineer

    We are looking for a Senior ML Engineer with 5+ years of experience.
    Requirements:
    - Strong Python skills (NumPy, Pandas, PyTorch)
    - Experience with LLMOps, RAG pipelines, vector databases
    - Deploying models to production (Docker, Kubernetes, AWS SageMaker)
    - Excellent written and verbal communication

    Nice to have:
    - Published research or open-source contributions
    - Master's or PhD in CS or related field
    """

    result = parse_jd(sample_jd)
    print("\n✅ JD Parsed Successfully!")
    print(f"Role: {result.role}")
    print(f"Domain: {result.domain}")
    print(f"Experience: {result.experience_years}+ years")
    print(f"Must-have skills: {result.must_have_skills}")
    print(f"Education: {result.education}")