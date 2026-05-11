import streamlit as st
import json
import os
from src.agent import run_pipeline, override_score
from src.report_generator import generate_html_report, generate_json_report

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="HR Shortlist Agent",
    page_icon="🎯",
    layout="wide"
)

# ── Header ───────────────────────────────────────────────────
st.title("🎯 HR Resume Shortlisting Agent")
st.markdown("*Powered by Groq LLaMA 3.3 70B · Built for fair, transparent hiring*")
st.divider()

# ── Session State ────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = []
if "jd_role" not in st.session_state:
    st.session_state.jd_role = ""

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Agent Settings")
    st.markdown("**LLM:** Groq LLaMA 3.3 70B")
    st.markdown("**Framework:** Direct API + Orchestrator")
    st.markdown("**Output:** HTML + JSON Reports")
    st.divider()
    st.markdown("**Scoring Weights:**")
    st.markdown("- Skills Match: 30%")
    st.markdown("- Experience: 25%")
    st.markdown("- Education: 15%")
    st.markdown("- Projects: 20%")
    st.markdown("- Communication: 10%")
    st.divider()
    st.markdown("🔒 PII masked before API call")
    st.markdown("✅ Structured JSON output enforced")
    st.markdown("👤 Human override enabled")

# ════════════════════════════════════════════════════════════
# STEP 1 — Job Description
# ════════════════════════════════════════════════════════════
st.header("Step 1 — Job Description")

sample_jd = """Senior Machine Learning Engineer

We are looking for a Senior ML Engineer with 5+ years of experience.

Requirements:
- Strong Python skills (NumPy, Pandas, PyTorch)
- Experience with LLMOps, RAG pipelines, vector databases
- Deploying models to production (Docker, Kubernetes, AWS SageMaker)
- Excellent written and verbal communication

Nice to have:
- Published research or open-source contributions
- Master's or PhD in CS or related field"""

jd_text = st.text_area(
    "Paste your Job Description here:",
    value=sample_jd,
    height=250
)

# ════════════════════════════════════════════════════════════
# STEP 2 — Candidates
# ════════════════════════════════════════════════════════════
st.header("Step 2 — Candidate Profiles")

st.markdown("### Option A — Upload Resume Files (PDF or DOCX)")
uploaded_files = st.file_uploader(
    "Drag and drop resume files here:",
    type=["pdf", "docx"],
    accept_multiple_files=True,
    help="You can upload multiple files at once. Supported: PDF, DOCX"
)

resume_paths = []
if uploaded_files:
    os.makedirs("data/uploaded_resumes", exist_ok=True)
    for file in uploaded_files:
        path = f"data/uploaded_resumes/{file.name}"
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        resume_paths.append(path)
    st.success(f"✅ {len(uploaded_files)} resume(s) uploaded successfully!")
    for file in uploaded_files:
        st.markdown(f"- 📄 {file.name}")

st.divider()

st.markdown("### Option B — Use Sample Candidates (for demo)")
use_sample = st.checkbox(
    "Load 5 pre-built sample candidates instead of uploading",
    value=False,
    help="Use this to quickly demo the agent without uploading files"
)

sample_candidates = [
    {
        "name": "Priya Sharma",
        "headline": "Senior ML Engineer at Google Brain",
        "summary": "7 years in ML. Expert in PyTorch, LLM fine-tuning, RAG pipelines.",
        "experience": "Google Brain 5 years, Spotify 2 years. Led recommendation system for 100M users.",
        "education": "PhD Computer Science, Stanford University",
        "skills": "Python, PyTorch, Kubernetes, Docker, LLMOps, SageMaker, RAG"
    },
    {
        "name": "Carlos Mendez",
        "headline": "ML Engineer at Startup",
        "summary": "4 years experience. Python, Scikit-learn, basic PyTorch.",
        "experience": "Startup NLP projects. Some Docker exposure.",
        "education": "Bachelor in Mathematics",
        "skills": "Python, Scikit-learn, PyTorch, Docker"
    },
    {
        "name": "James Whitfield",
        "headline": "Backend Engineer transitioning to ML",
        "summary": "3 years Python API dev, 1 year ML tutorials. No production ML yet.",
        "experience": "Backend development, REST APIs, AWS",
        "education": "BSc Computer Science",
        "skills": "Python, Docker, AWS, REST APIs"
    },
    {
        "name": "Aisha Okonkwo",
        "headline": "Data Scientist",
        "summary": "6 years. Python, Pandas, recently upskilled in LangChain and Pinecone.",
        "experience": "Deployed 2 RAG systems. Active Kaggle contributor.",
        "education": "MSc Statistics, UCL",
        "skills": "Python, Pandas, LangChain, Pinecone, Scikit-learn"
    },
    {
        "name": "Mei-Ling Chen",
        "headline": "ML Research Engineer",
        "summary": "5 years. PyTorch expert, co-authored DeepSpeed paper. PhD MIT.",
        "experience": "Research engineer. Published 8 papers. GCP Vertex AI.",
        "education": "PhD CS, MIT",
        "skills": "Python, PyTorch, DeepSpeed, FSDP, GCP Vertex AI"
    }
]

linkedin_data = []
if use_sample:
    linkedin_data = sample_candidates
    st.success(f"✅ 5 sample candidates loaded and ready!")
    for c in sample_candidates:
        st.markdown(f"- 👤 **{c['name']}** — {c['headline']}")

st.divider()

st.markdown("### Option C — Add LinkedIn Profile manually")
with st.expander("➕ Add a LinkedIn profile manually"):
    col1, col2 = st.columns(2)
    with col1:
        ln_name = st.text_input("Full Name")
        ln_headline = st.text_input("Job Title / Headline")
        ln_education = st.text_input("Education")
    with col2:
        ln_skills = st.text_input("Skills (comma separated)")
        ln_experience = st.text_area("Experience summary", height=80)
        ln_summary = st.text_area("Profile summary", height=80)

    if st.button("➕ Add this candidate"):
        if ln_name and ln_skills:
            linkedin_data.append({
                "name": ln_name,
                "headline": ln_headline,
                "summary": ln_summary,
                "experience": ln_experience,
                "education": ln_education,
                "skills": ln_skills
            })
            st.success(f"✅ {ln_name} added!")
        else:
            st.error("Please enter at least Name and Skills.")

# ════════════════════════════════════════════════════════════
# STEP 3 — Run Analysis
# ════════════════════════════════════════════════════════════
st.header("Step 3 — Run Analysis")

if st.button("🚀 Run AI Scoring Agent", type="primary", use_container_width=True):
    if not jd_text.strip():
        st.error("Please enter a Job Description first.")
    elif not linkedin_data and not resume_paths:
        st.error("Please add at least one candidate.")
    else:
        with st.spinner("Agent running... scoring all candidates..."):
            try:
                results = run_pipeline(
                    jd_text=jd_text,
                    resume_paths=resume_paths,
                    linkedin_data=linkedin_data
                )
                st.session_state.results = results
                st.session_state.jd_role = "ML Engineer"
                st.success(f"✅ Scored {len(results)} candidates successfully!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ════════════════════════════════════════════════════════════
# STEP 4 — Shortlist Results
# ════════════════════════════════════════════════════════════
if st.session_state.results:
    st.header("Step 4 — Ranked Shortlist")

    results = st.session_state.results

    # Summary metrics
    hire   = sum(1 for r in results if r.recommendation == "hire")
    review = sum(1 for r in results if r.recommendation == "review")
    no     = sum(1 for r in results if r.recommendation == "no-hire")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Candidates", len(results))
    col2.metric("✅ Hire", hire)
    col3.metric("🔍 Review", review)
    col4.metric("❌ No Hire", no)

    st.divider()

    # Filter
    filter_opt = st.radio(
        "Filter by recommendation:",
        ["All", "Hire", "Review", "No-hire"],
        horizontal=True
    )

    filtered = results
    if filter_opt != "All":
        filtered = [r for r in results if r.recommendation == filter_opt.lower()]

    # Candidate cards
    for i, result in enumerate(filtered, 1):
        rec = result.recommendation
        color = "🟢" if rec == "hire" else "🟡" if rec == "review" else "🔴"

        with st.expander(
            f"{color} #{i} {result.candidate_name} — {result.weighted_total}/10 — {rec.upper()}",
            expanded=(i == 1)
        ):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("**Dimension Scores:**")

                dims = [
                    ("Skills Match",          "30%", result.skills_match),
                    ("Experience Relevance",  "25%", result.experience_relevance),
                    ("Education & Certs",     "15%", result.education_certs),
                    ("Project / Portfolio",   "20%", result.project_portfolio),
                    ("Communication",         "10%", result.communication_quality),
                ]

                for name, weight, dim in dims:
                    score = dim.score
                    st.markdown(f"**{name}** ({weight}) — {score}/10")
                    st.progress(score / 10)
                    st.caption(dim.justification)

            with col2:
                st.markdown("**Strengths:**")
                for s in result.strengths:
                    st.success(f"✓ {s}")

                st.markdown("**Gaps:**")
                for g in result.gaps:
                    st.error(f"✗ {g}")

            # ── HR Override ──────────────────────────────────
            st.divider()
            st.markdown("**🔧 HR Override**")

            ov_col1, ov_col2, ov_col3 = st.columns([2, 1, 2])

            with ov_col1:
                ov_dim = st.selectbox(
                    "Dimension to override:",
                    ["skills_match", "experience_relevance",
                     "education_certs", "project_portfolio",
                     "communication_quality"],
                    key=f"dim_{i}"
                )

            with ov_col2:
                ov_score = st.number_input(
                    "New score (0-10):",
                    min_value=0,
                    max_value=10,
                    value=5,
                    key=f"score_{i}"
                )

            with ov_col3:
                ov_reason = st.text_input(
                    "Reason for override:",
                    key=f"reason_{i}"
                )

            if st.button(f"Apply Override", key=f"override_{i}"):
                if ov_reason.strip():
                    st.session_state.results = override_score(
                        results=st.session_state.results,
                        candidate_name=result.candidate_name,
                        dimension=ov_dim,
                        new_score=ov_score,
                        reason=ov_reason
                    )
                    st.success("✅ Override applied and logged!")
                    st.rerun()
                else:
                    st.error("Please enter a reason for the override.")

    # ── Export Reports ───────────────────────────────────────
    st.divider()
    st.header("Step 5 — Export Reports")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Generate HTML Report", use_container_width=True):
            path = generate_html_report(
                st.session_state.results,
                role=st.session_state.jd_role
            )
            st.success(f"✅ HTML report saved to {path}")
            with open(path, "r", encoding="utf-8") as f:
                st.download_button(
                    "⬇️ Download HTML Report",
                    f.read(),
                    file_name="shortlist_report.html",
                    mime="text/html",
                    use_container_width=True
                )

    with col2:
        if st.button("📊 Generate JSON Report", use_container_width=True):
            path = generate_json_report(st.session_state.results)
            st.success(f"✅ JSON report saved to {path}")
            with open(path, "r", encoding="utf-8") as f:
                st.download_button(
                    "⬇️ Download JSON Report",
                    f.read(),
                    file_name="shortlist_report.json",
                    mime="application/json",
                    use_container_width=True
                )