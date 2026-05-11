import os
import json
import re
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel
from typing import List
from src.jd_parser import JDRequirements
from src.resume_parser import CandidateProfile

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Pydantic Models ──────────────────────────────────────────
class DimensionScore(BaseModel):
    score: int
    justification: str

class ScoringResult(BaseModel):
    candidate_name: str
    source_type: str
    skills_match: DimensionScore
    experience_relevance: DimensionScore
    education_certs: DimensionScore
    project_portfolio: DimensionScore
    communication_quality: DimensionScore
    weighted_total: float
    recommendation: str
    strengths: List[str]
    gaps: List[str]

# ── Compute weighted total in Python (not LLM) ───────────────
def compute_weighted_total(
    skills: int,
    experience: int,
    education: int,
    projects: int,
    communication: int
) -> float:
    total = (
        skills        * 0.30 +
        experience    * 0.25 +
        education     * 0.15 +
        projects      * 0.20 +
        communication * 0.10
    )
    return round(total, 2)

# ── Get recommendation based on score ───────────────────────
def get_recommendation(score: float) -> str:
    if score >= 7.5:
        return "hire"
    elif score >= 5.0:
        return "review"
    else:
        return "no-hire"

# ── Confidence guardrail (security) ─────────────────────────
def check_confidence(score: int, justification: str) -> bool:
    if score in [0, 10] and len(justification.split()) < 10:
        return False
    return True

# ── Main scoring function ────────────────────────────────────
def score_candidate(
    jd: JDRequirements,
    candidate: CandidateProfile
) -> ScoringResult:

    system_prompt = """You are an expert HR scoring agent.
Score candidates against job requirements using a strict rubric.
Return ONLY valid JSON — no markdown, no explanation, no extra text.

SCORING RUBRIC (score 0-10):
- Skills Match (30%):
  0-3 = less than 30% skills match
  4-6 = 50-70% skills match
  7-10 = more than 85% skills match

- Experience Relevance (25%):
  0-3 = unrelated domain
  4-6 = adjacent domain
  7-10 = exact domain and seniority match

- Education & Certs (15%):
  0-3 = does not meet minimum
  4-6 = meets minimum
  7-10 = exceeds minimum with extra certifications

- Project/Portfolio (20%):
  0-3 = no evidence of projects
  4-6 = 1-2 generic projects
  7-10 = strong relevant portfolio

- Communication Quality (10%):
  0-3 = poor structure or grammar
  4-6 = adequate clarity
  7-10 = crisp, structured, impactful writing

Use exactly this JSON schema:
{
  "skills_match": {"score": 0, "justification": "one sentence explanation"},
  "experience_relevance": {"score": 0, "justification": "one sentence explanation"},
  "education_certs": {"score": 0, "justification": "one sentence explanation"},
  "project_portfolio": {"score": 0, "justification": "one sentence explanation"},
  "communication_quality": {"score": 0, "justification": "one sentence explanation"},
  "strengths": ["strength 1", "strength 2"],
  "gaps": ["gap 1", "gap 2"]
}"""

    user_prompt = f"""
JOB REQUIREMENTS:
Role: {jd.role}
Domain: {jd.domain}
Experience Required: {jd.experience_years}+ years
Must-have Skills: {', '.join(jd.must_have_skills)}
All Skills: {', '.join(jd.skills)}
Education: {jd.education}

CANDIDATE PROFILE:
Name: CANDIDATE_ANONYMOUS
Domain: {candidate.domain}
Experience: {candidate.experience_years} years
Skills: {', '.join(candidate.skills)}
Education: {candidate.education}
Projects: {', '.join(candidate.projects)}
Profile Summary: {candidate.raw_text[:500]}

Score this candidate against the job requirements.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1
    )

    raw = response.choices[0].message.content
    raw = raw.replace("```json", "").replace("```", "").strip()

    parsed = json.loads(raw)

    # compute weighted total in Python
    weighted_total = compute_weighted_total(
        skills=parsed["skills_match"]["score"],
        experience=parsed["experience_relevance"]["score"],
        education=parsed["education_certs"]["score"],
        projects=parsed["project_portfolio"]["score"],
        communication=parsed["communication_quality"]["score"]
    )

    recommendation = get_recommendation(weighted_total)

    return ScoringResult(
        candidate_name=candidate.name,
        source_type=candidate.source_type,
        skills_match=DimensionScore(**parsed["skills_match"]),
        experience_relevance=DimensionScore(**parsed["experience_relevance"]),
        education_certs=DimensionScore(**parsed["education_certs"]),
        project_portfolio=DimensionScore(**parsed["project_portfolio"]),
        communication_quality=DimensionScore(**parsed["communication_quality"]),
        weighted_total=weighted_total,
        recommendation=recommendation,
        strengths=parsed.get("strengths", []),
        gaps=parsed.get("gaps", [])
    )


# ── Test it ──────────────────────────────────────────────────
if __name__ == "__main__":
    from src.jd_parser import parse_jd
    from src.resume_parser import parse_resume

    sample_jd = """
    Senior Machine Learning Engineer
    5+ years experience required.
    Must have: Python, PyTorch, LLMOps, RAG pipelines, Docker, Kubernetes
    Nice to have: PhD, published research, open-source contributions
    Strong communication skills required.
    """

    sample_linkedin = {
        "name": "Priya Sharma",
        "headline": "Senior ML Engineer at Google Brain",
        "summary": "7 years experience in ML. Expert in PyTorch, LLM fine-tuning, RAG pipelines.",
        "experience": "Google Brain 5 years, Spotify 2 years. Led recommendation system for 100M users.",
        "education": "PhD Computer Science, Stanford University",
        "skills": "Python, PyTorch, TensorFlow, Kubernetes, SageMaker, Docker, LLMOps"
    }

    print("Parsing JD...")
    jd = parse_jd(sample_jd)

    print("Parsing Resume...")
    candidate = parse_resume(linkedin_data=sample_linkedin)

    print("Scoring candidate...")
    result = score_candidate(jd, candidate)

    print("\n✅ Scoring Complete!")
    print(f"Candidate: {result.candidate_name}")
    print(f"Skills Match: {result.skills_match.score}/10 — {result.skills_match.justification}")
    print(f"Experience: {result.experience_relevance.score}/10 — {result.experience_relevance.justification}")
    print(f"Education: {result.education_certs.score}/10 — {result.education_certs.justification}")
    print(f"Projects: {result.project_portfolio.score}/10 — {result.project_portfolio.justification}")
    print(f"Communication: {result.communication_quality.score}/10 — {result.communication_quality.justification}")
    print(f"\nWeighted Total: {result.weighted_total}/10")
    print(f"Recommendation: {result.recommendation.upper()}")
    print(f"Strengths: {result.strengths}")
    print(f"Gaps: {result.gaps}")