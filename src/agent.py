import os
import json
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict
from src.jd_parser import parse_jd, JDRequirements
from src.resume_parser import parse_resume, CandidateProfile
from src.scoring_engine import score_candidate, ScoringResult

load_dotenv()

# ── Override log file path ───────────────────────────────────
OVERRIDE_LOG_PATH = "data/override_log.json"

# ── Run full pipeline ────────────────────────────────────────
def run_pipeline(
    jd_text: str,
    resume_paths: List[str] = [],
    linkedin_data: List[Dict] = []
) -> List[ScoringResult]:

    print("\n🚀 HR Shortlist Agent Starting...")
    print("=" * 50)

    # Step 1 — Parse JD
    print("\n📋 Step 1: Parsing Job Description...")
    jd = parse_jd(jd_text)
    print(f"✅ Role: {jd.role}")
    print(f"✅ Domain: {jd.domain}")
    print(f"✅ Experience Required: {jd.experience_years}+ years")

    # Step 2 — Parse all resumes and LinkedIn profiles
    print("\n👤 Step 2: Parsing Candidate Profiles...")
    candidates: List[CandidateProfile] = []

    for path in resume_paths:
        try:
            profile = parse_resume(file_path=path)
            candidates.append(profile)
            print(f"✅ Parsed resume: {profile.name} ({profile.source_type})")
        except Exception as e:
            print(f"❌ Failed to parse {path}: {e}")

    for linkedin in linkedin_data:
        try:
            profile = parse_resume(linkedin_data=linkedin)
            candidates.append(profile)
            print(f"✅ Parsed LinkedIn: {profile.name}")
        except Exception as e:
            print(f"❌ Failed to parse LinkedIn profile: {e}")

    if not candidates:
        print("❌ No candidates parsed. Exiting.")
        return []

    # Step 3 — Score all candidates
    print(f"\n🎯 Step 3: Scoring {len(candidates)} Candidates...")
    results: List[ScoringResult] = []

    for candidate in candidates:
        try:
            print(f"  Scoring {candidate.name}...")
            result = score_candidate(jd, candidate)
            results.append(result)
            print(f"  ✅ {result.candidate_name}: {result.weighted_total}/10 → {result.recommendation.upper()}")
        except Exception as e:
            print(f"  ❌ Failed to score {candidate.name}: {e}")

    # Step 4 — Rank candidates
    print("\n📊 Step 4: Ranking Candidates...")
    results.sort(key=lambda x: x.weighted_total, reverse=True)

    print("\n🏆 FINAL RANKINGS:")
    print("-" * 50)
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.candidate_name} — {result.weighted_total}/10 — {result.recommendation.upper()}")

    # Step 5 — Log results (no PII in log)
    log_run(results)

    return results


# ── Log run results ──────────────────────────────────────────
def log_run(results: List[ScoringResult]):
    log_path = "data/run_log.txt"
    os.makedirs("data", exist_ok=True)
    with open(log_path, "a") as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"Run Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        for r in results:
            # No PII — only scores logged
            f.write(f"Candidate: {r.candidate_name} | Score: {r.weighted_total} | {r.recommendation}\n")
    print(f"\n📝 Run logged to {log_path}")


# ── Human override function ──────────────────────────────────
def override_score(
    results: List[ScoringResult],
    candidate_name: str,
    dimension: str,
    new_score: int,
    reason: str
) -> List[ScoringResult]:

    os.makedirs("data", exist_ok=True)

    for result in results:
        if result.candidate_name.lower() == candidate_name.lower():
            # Get old score
            old_score = getattr(result, dimension).score

            # Apply new score
            getattr(result, dimension).score = new_score

            # Recompute weighted total
            result.weighted_total = round(
                result.skills_match.score        * 0.30 +
                result.experience_relevance.score * 0.25 +
                result.education_certs.score      * 0.15 +
                result.project_portfolio.score    * 0.20 +
                result.communication_quality.score * 0.10,
                2
            )

            # Update recommendation
            if result.weighted_total >= 7.5:
                result.recommendation = "hire"
            elif result.weighted_total >= 5.0:
                result.recommendation = "review"
            else:
                result.recommendation = "no-hire"

            # Log override
            log_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "hr_user": "HR",
                "candidate": candidate_name,
                "dimension": dimension,
                "old_score": old_score,
                "new_score": new_score,
                "reason": reason,
                "new_total": result.weighted_total,
                "new_recommendation": result.recommendation
            }

            # Save to override log
            logs = []
            if os.path.exists(OVERRIDE_LOG_PATH):
                with open(OVERRIDE_LOG_PATH, "r") as f:
                    logs = json.load(f)
            logs.append(log_entry)
            with open(OVERRIDE_LOG_PATH, "w") as f:
                json.dump(logs, f, indent=2)

            print(f"\n✅ Override Applied!")
            print(f"Candidate: {candidate_name}")
            print(f"Dimension: {dimension}")
            print(f"Score: {old_score} → {new_score}")
            print(f"New Total: {result.weighted_total}/10")
            print(f"New Recommendation: {result.recommendation.upper()}")
            print(f"Reason logged: {reason}")

            break

    # Re-rank after override
    results.sort(key=lambda x: x.weighted_total, reverse=True)
    return results


# ── Test it ──────────────────────────────────────────────────
if __name__ == "__main__":

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
            "experience": "Startup NLP projects. Some Docker exposure.",
            "education": "Bachelor in Mathematics",
            "skills": "Python, Scikit-learn, PyTorch, Docker"
        },
        {
            "name": "James Whitfield",
            "headline": "Backend Engineer transitioning to ML",
            "summary": "3 years Python API dev, 1 year ML tutorials. No production ML.",
            "experience": "Backend development, REST APIs",
            "education": "BSc Computer Science",
            "skills": "Python, Docker, AWS, REST APIs"
        }
    ]

    # Run pipeline
    results = run_pipeline(
        jd_text=sample_jd,
        linkedin_data=linkedin_profiles
    )

    # Test override
    print("\n\n🔧 Testing HR Override...")
    results = override_score(
        results=results,
        candidate_name="Carlos Mendez",
        dimension="skills_match",
        new_score=8,
        reason="HR verified candidate has additional skills not listed on profile"
    )

    print("\n📊 Updated Rankings After Override:")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r.candidate_name} — {r.weighted_total}/10 — {r.recommendation.upper()}")