import os
import json
from datetime import datetime
from typing import List
from jinja2 import Environment, FileSystemLoader
from src.scoring_engine import ScoringResult

# ── Generate HTML Report ─────────────────────────────────────
def generate_html_report(
    results: List[ScoringResult],
    role: str = "Unknown Role",
    output_path: str = "output/shortlist_report.html"
) -> str:

    os.makedirs("output", exist_ok=True)

    # Load override log if exists
    overrides = []
    if os.path.exists("data/override_log.json"):
        with open("data/override_log.json", "r") as f:
            overrides = json.load(f)

    # Count verdicts
    hire_count   = sum(1 for r in results if r.recommendation == "hire")
    review_count = sum(1 for r in results if r.recommendation == "review")
    no_hire_count = sum(1 for r in results if r.recommendation == "no-hire")

    # Render template
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report.html")

    html = template.render(
        results=results,
        role=role,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        hire_count=hire_count,
        review_count=review_count,
        no_hire_count=no_hire_count,
        overrides=overrides
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ HTML Report saved to {output_path}")
    return output_path


# ── Generate JSON Report ─────────────────────────────────────
def generate_json_report(
    results: List[ScoringResult],
    output_path: str = "output/shortlist_report.json"
) -> str:

    os.makedirs("output", exist_ok=True)

    report = []
    for i, r in enumerate(results, 1):
        report.append({
            "rank": i,
            "candidate_name": r.candidate_name,
            "source_type": r.source_type,
            "weighted_total": r.weighted_total,
            "recommendation": r.recommendation,
            "dimensions": {
                "skills_match": {
                    "score": r.skills_match.score,
                    "weight": "30%",
                    "justification": r.skills_match.justification
                },
                "experience_relevance": {
                    "score": r.experience_relevance.score,
                    "weight": "25%",
                    "justification": r.experience_relevance.justification
                },
                "education_certs": {
                    "score": r.education_certs.score,
                    "weight": "15%",
                    "justification": r.education_certs.justification
                },
                "project_portfolio": {
                    "score": r.project_portfolio.score,
                    "weight": "20%",
                    "justification": r.project_portfolio.justification
                },
                "communication_quality": {
                    "score": r.communication_quality.score,
                    "weight": "10%",
                    "justification": r.communication_quality.justification
                }
            },
            "strengths": r.strengths,
            "gaps": r.gaps
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"✅ JSON Report saved to {output_path}")
    return output_path


# ── Test it ──────────────────────────────────────────────────
if __name__ == "__main__":
    from src.agent import run_pipeline

    sample_jd = """
    Senior Machine Learning Engineer
    5+ years experience required.
    Must have: Python, PyTorch, LLMOps, RAG pipelines, Docker, Kubernetes
    Nice to have: PhD, published research
    Strong communication skills required.
    """

    linkedin_profiles = [
        {
            "name": "Priya Sharma",
            "headline": "Senior ML Engineer at Google Brain",
            "summary": "7 years in ML. Expert in PyTorch, LLM fine-tuning, RAG pipelines.",
            "experience": "Google Brain 5 years, Spotify 2 years.",
            "education": "PhD Computer Science, Stanford",
            "skills": "Python, PyTorch, Kubernetes, Docker, LLMOps, SageMaker"
        },
        {
            "name": "Carlos Mendez",
            "headline": "ML Engineer",
            "summary": "4 years experience. Python, Scikit-learn, basic PyTorch.",
            "experience": "Startup NLP projects.",
            "education": "Bachelor in Mathematics",
            "skills": "Python, Scikit-learn, PyTorch, Docker"
        },
        {
            "name": "James Whitfield",
            "headline": "Backend Engineer transitioning to ML",
            "summary": "3 years Python API dev, 1 year ML tutorials.",
            "experience": "Backend development, REST APIs",
            "education": "BSc Computer Science",
            "skills": "Python, Docker, AWS, REST APIs"
        },
        {
            "name": "Aisha Okonkwo",
            "headline": "Data Scientist",
            "summary": "6 years. Python, Pandas, recently upskilled in LangChain, Pinecone.",
            "experience": "Deployed 2 RAG systems. MSc Statistics UCL.",
            "education": "MSc Statistics, UCL",
            "skills": "Python, Pandas, LangChain, Pinecone, Scikit-learn"
        },
        {
            "name": "Mei-Ling Chen",
            "headline": "ML Research Engineer",
            "summary": "5 years. PyTorch expert, co-authored DeepSpeed paper.",
            "experience": "PhD CS MIT. Published 8 papers. GCP Vertex AI.",
            "education": "PhD CS, MIT",
            "skills": "Python, PyTorch, DeepSpeed, FSDP, GCP Vertex AI"
        }
    ]

    results = run_pipeline(
        jd_text=sample_jd,
        linkedin_data=linkedin_profiles
    )

    generate_html_report(results, role="Senior ML Engineer")
    generate_json_report(results)

    print("\n✅ Reports generated in /output folder!")
    print("Open output/shortlist_report.html in your browser to view.")