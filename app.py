import streamlit as st
import json
import os
from src.agent import run_pipeline, override_score
from src.report_generator import generate_html_report, generate_json_report

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="HR Shortlist Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0f1117;
    }

    /* Hide default streamlit menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Hero section */
    .hero {
        background: linear-gradient(135deg, #1a1f2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 16px;
        padding: 40px;
        margin-bottom: 30px;
        border: 1px solid #2d3561;
        text-align: center;
    }
    .hero h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
    }
    .hero p {
        color: #8892b0;
        font-size: 1.1rem;
        margin: 0;
    }
    .hero .badge {
        display: inline-block;
        background: #2d3561;
        color: #64ffda;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 8px 4px;
        border: 1px solid #64ffda33;
    }

    /* Step cards */
    .step-card {
        background: #1a1f2e;
        border: 1px solid #2d3561;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
    }
    .step-header {
        display: flex;
        align-items: center;
        margin-bottom: 16px;
    }
    .step-number {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        margin-right: 12px;
        flex-shrink: 0;
    }
    .step-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #ccd6f6;
    }

    /* Metric cards */
    .metric-row {
        display: flex;
        gap: 16px;
        margin: 20px 0;
    }
    .metric-card {
        flex: 1;
        background: #1a1f2e;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #2d3561;
    }
    .metric-card .number {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .metric-card .label {
        color: #8892b0;
        font-size: 0.85rem;
    }
    .metric-hire { border-top: 3px solid #64ffda; }
    .metric-hire .number { color: #64ffda; }
    .metric-review { border-top: 3px solid #ffd700; }
    .metric-review .number { color: #ffd700; }
    .metric-nohire { border-top: 3px solid #ff6b6b; }
    .metric-nohire .number { color: #ff6b6b; }
    .metric-total { border-top: 3px solid #667eea; }
    .metric-total .number { color: #667eea; }

    /* Candidate cards */
    .candidate-card {
        background: #1a1f2e;
        border: 1px solid #2d3561;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
        transition: border-color 0.2s;
    }
    .candidate-card:hover {
        border-color: #667eea;
    }
    .candidate-card.hire { border-left: 4px solid #64ffda; }
    .candidate-card.review { border-left: 4px solid #ffd700; }
    .candidate-card.nohire { border-left: 4px solid #ff6b6b; }

    .candidate-name {
        font-size: 1.3rem;
        font-weight: 600;
        color: #ccd6f6;
    }
    .candidate-meta {
        color: #8892b0;
        font-size: 0.9rem;
        margin-top: 4px;
    }

    /* Score badge */
    .score-badge {
        font-size: 2rem;
        font-weight: 700;
        text-align: right;
    }
    .score-hire { color: #64ffda; }
    .score-review { color: #ffd700; }
    .score-nohire { color: #ff6b6b; }

    /* Verdict badge */
    .verdict {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 4px;
    }
    .verdict-hire { background: #64ffda22; color: #64ffda; border: 1px solid #64ffda44; }
    .verdict-review { background: #ffd70022; color: #ffd700; border: 1px solid #ffd70044; }
    .verdict-nohire { background: #ff6b6b22; color: #ff6b6b; border: 1px solid #ff6b6b44; }

    /* Dimension bars */
    .dim-row {
        margin: 8px 0;
    }
    .dim-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
        font-size: 0.85rem;
        color: #8892b0;
    }
    .dim-bar-bg {
        background: #2d3561;
        border-radius: 4px;
        height: 6px;
        overflow: hidden;
    }
    .dim-bar-fill {
        height: 6px;
        border-radius: 4px;
    }
    .bar-high { background: linear-gradient(90deg, #64ffda, #00b4d8); }
    .bar-mid { background: linear-gradient(90deg, #ffd700, #ff9f1c); }
    .bar-low { background: linear-gradient(90deg, #ff6b6b, #ee0979); }

    /* Tags */
    .tag-strength {
        display: inline-block;
        background: #64ffda22;
        color: #64ffda;
        border: 1px solid #64ffda44;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        margin: 3px;
    }
    .tag-gap {
        display: inline-block;
        background: #ff6b6b22;
        color: #ff6b6b;
        border: 1px solid #ff6b6b44;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        margin: 3px;
    }

    /* Rank badge */
    .rank-1 { background: linear-gradient(135deg, #ffd700, #ff9f1c); }
    .rank-2 { background: linear-gradient(135deg, #c0c0c0, #a0a0a0); }
    .rank-3 { background: linear-gradient(135deg, #cd7f32, #a0522d); }
    .rank-other { background: #2d3561; }
    .rank-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        font-weight: 700;
        font-size: 0.85rem;
        color: white;
        margin-right: 10px;
    }

    /* Override section */
    .override-box {
        background: #0f1117;
        border: 1px solid #2d3561;
        border-radius: 8px;
        padding: 16px;
        margin-top: 16px;
    }
    .override-title {
        color: #8892b0;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Sidebar */
    .sidebar-card {
        background: #1a1f2e;
        border: 1px solid #2d3561;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .sidebar-title {
        color: #64ffda;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .sidebar-item {
        color: #8892b0;
        font-size: 0.85rem;
        padding: 4px 0;
    }

    /* Security badge */
    .security-badge {
        background: #64ffda11;
        border: 1px solid #64ffda33;
        border-radius: 8px;
        padding: 10px 14px;
        margin: 6px 0;
        font-size: 0.8rem;
        color: #64ffda;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button:hover {
        opacity: 0.9 !important;
    }

    /* Divider */
    .custom-divider {
        border: none;
        border-top: 1px solid #2d3561;
        margin: 24px 0;
    }

    /* Filter pills */
    .filter-pill {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        cursor: pointer;
        margin: 4px;
        border: 1px solid #2d3561;
        color: #8892b0;
    }
    .filter-pill.active {
        background: #667eea22;
        border-color: #667eea;
        color: #667eea;
    }

    /* Info box */
    .info-box {
        background: #667eea11;
        border: 1px solid #667eea33;
        border-radius: 8px;
        padding: 12px 16px;
        color: #8892b0;
        font-size: 0.85rem;
        margin: 12px 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Session State ────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = []
if "jd_role" not in st.session_state:
    st.session_state.jd_role = ""

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-title">⚙️ Agent Configuration</div>
        <div class="sidebar-item">🤖 LLM: Groq LLaMA 3.3 70B</div>
        <div class="sidebar-item">🏗️ Framework: Direct API + Orchestrator</div>
        <div class="sidebar-item">📊 Output: HTML + JSON Reports</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-title">📊 Scoring Weights</div>
        <div class="sidebar-item">🎯 Skills Match — 30%</div>
        <div class="sidebar-item">💼 Experience — 25%</div>
        <div class="sidebar-item">🎓 Education — 15%</div>
        <div class="sidebar-item">🚀 Projects — 20%</div>
        <div class="sidebar-item">💬 Communication — 10%</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-title">🔒 Security Features</div>
        <div class="security-badge">✓ PII masked before API call</div>
        <div class="security-badge">✓ Structured JSON output enforced</div>
        <div class="security-badge">✓ Human override with audit log</div>
        <div class="security-badge">✓ Input sanitisation active</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-title">📈 Score Guide</div>
        <div class="sidebar-item">🟢 7.5–10.0 → Recommended Hire</div>
        <div class="sidebar-item">🟡 5.0–7.4 → Further Review</div>
        <div class="sidebar-item">🔴 0.0–4.9 → Not Suitable</div>
    </div>
    """, unsafe_allow_html=True)

# ── Hero Section ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🎯 HR Shortlist Agent</h1>
    <p>AI-powered candidate evaluation · Transparent scoring · Human-in-the-loop</p>
    <br>
    <span class="badge">⚡ Groq LLaMA 3.3 70B</span>
    <span class="badge">🔒 PII Protected</span>
    <span class="badge">📊 5-Dimension Rubric</span>
    <span class="badge">👤 HR Override</span>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# STEP 1 — Job Description
# ════════════════════════════════════════════════════════════
st.markdown("""
<div class="step-card">
    <div class="step-header">
        <div class="step-number">1</div>
        <div class="step-title">Job Description</div>
    </div>
</div>
""", unsafe_allow_html=True)

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
    height=220,
    help="The agent will extract skills, experience, domain and education requirements automatically."
)

word_count = len(jd_text.split())
st.caption(f"📝 {word_count} words detected")

# ════════════════════════════════════════════════════════════
# STEP 2 — Candidates
# ════════════════════════════════════════════════════════════
st.markdown("""
<div class="step-card">
    <div class="step-header">
        <div class="step-number">2</div>
        <div class="step-title">Add Candidates</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### 📁 Option A — Upload Resume Files")
st.markdown("""
<div class="info-box">
    Supported formats: PDF, DOCX · Upload multiple files at once
</div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Drag and drop resume files here:",
    type=["pdf", "docx"],
    accept_multiple_files=True,
    label_visibility="collapsed"
)

resume_paths = []
if uploaded_files:
    os.makedirs("data/uploaded_resumes", exist_ok=True)
    for file in uploaded_files:
        path = f"data/uploaded_resumes/{file.name}"
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        resume_paths.append(path)
    st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")
    cols = st.columns(min(len(uploaded_files), 3))
    for i, file in enumerate(uploaded_files):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:#1a1f2e;border:1px solid #2d3561;border-radius:8px;
            padding:10px;text-align:center;font-size:0.8rem;color:#ccd6f6;">
                📄 {file.name}
            </div>
            """, unsafe_allow_html=True)

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

st.markdown("### 👥 Option B — Sample Candidates")
st.markdown("""
<div class="info-box">
    Use 5 pre-built candidates for demo — good match, partial match, and no match included
</div>
""", unsafe_allow_html=True)

sample_candidates = [
    {
        "name": "Priya Sharma",
        "headline": "Senior ML Engineer at Google Brain",
        "summary": "7 years in ML. Expert in PyTorch, LLM fine-tuning, RAG pipelines.",
        "experience": "Google Brain 5 years, Spotify 2 years. Led recommendation system for 100M users.",
        "education": "PhD Computer Science, Stanford University",
        "skills": "Python, PyTorch, Kubernetes, Docker, LLMOps, SageMaker, RAG, Pinecone"
    },
    {
        "name": "Carlos Mendez",
        "headline": "ML Engineer at Startup",
        "summary": "4 years experience. Python, Scikit-learn, basic PyTorch. Good communicator.",
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
        "skills": "Python, PyTorch, DeepSpeed, FSDP, GCP Vertex AI, distributed training"
    }
]

use_sample = st.checkbox("Load 5 sample candidates", value=False)
linkedin_data = []

if use_sample:
    linkedin_data = sample_candidates
    cols = st.columns(5)
    avatars = ["👩‍💻", "👨‍💻", "👨‍💼", "👩‍🔬", "👩‍💻"]
    colors = ["#64ffda", "#667eea", "#ffd700", "#ff9f1c", "#ff6b6b"]
    for i, (c, col) in enumerate(zip(sample_candidates, cols)):
        with col:
            st.markdown(f"""
            <div style="background:#1a1f2e;border:1px solid #2d3561;border-radius:10px;
            padding:12px;text-align:center;border-top:3px solid {colors[i]}">
                <div style="font-size:1.5rem">{avatars[i]}</div>
                <div style="color:#ccd6f6;font-size:0.8rem;font-weight:600;margin-top:4px">
                    {c['name'].split()[0]}
                </div>
                <div style="color:#8892b0;font-size:0.7rem;margin-top:2px">
                    {c['headline'].split(' at ')[0][:20]}
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

st.markdown("### ➕ Option C — Add LinkedIn Profile Manually")
with st.expander("Click to add a candidate manually"):
    col1, col2 = st.columns(2)
    with col1:
        ln_name = st.text_input("Full Name *")
        ln_headline = st.text_input("Job Title / Headline")
        ln_education = st.text_input("Education")
    with col2:
        ln_skills = st.text_input("Skills (comma separated) *")
        ln_experience = st.text_area("Experience Summary", height=80)
        ln_summary = st.text_area("Profile Summary", height=80)

    if st.button("➕ Add Candidate"):
        if ln_name and ln_skills:
            linkedin_data.append({
                "name": ln_name,
                "headline": ln_headline,
                "summary": ln_summary,
                "experience": ln_experience,
                "education": ln_education,
                "skills": ln_skills
            })
            st.success(f"✅ {ln_name} added successfully!")
        else:
            st.error("Please fill in Name and Skills at minimum.")

# ════════════════════════════════════════════════════════════
# STEP 3 — Run Analysis
# ════════════════════════════════════════════════════════════
st.markdown("""
<div class="step-card">
    <div class="step-header">
        <div class="step-number">3</div>
        <div class="step-title">Run AI Analysis</div>
    </div>
</div>
""", unsafe_allow_html=True)

total_candidates = len(linkedin_data) + len(resume_paths)
if total_candidates > 0:
    st.markdown(f"""
    <div class="info-box">
        ✅ Ready to score <strong>{total_candidates} candidate(s)</strong>
        against the job description
    </div>
    """, unsafe_allow_html=True)

if st.button("🚀 Run AI Scoring Agent", use_container_width=True):
    if not jd_text.strip():
        st.error("⚠️ Please enter a Job Description first.")
    elif not linkedin_data and not resume_paths:
        st.error("⚠️ Please add at least one candidate.")
    else:
        progress_bar = st.progress(0)
        status = st.empty()

        status.markdown("🔍 **Parsing Job Description...**")
        progress_bar.progress(10)

        try:
            status.markdown("👤 **Parsing candidate profiles...**")
            progress_bar.progress(30)

            results = run_pipeline(
                jd_text=jd_text,
                resume_paths=resume_paths,
                linkedin_data=linkedin_data
            )

            progress_bar.progress(80)
            status.markdown("📊 **Generating rankings...**")

            st.session_state.results = results
            st.session_state.jd_role = "ML Engineer"

            progress_bar.progress(100)
            status.empty()
            progress_bar.empty()

            st.success(f"✅ Successfully scored {len(results)} candidates!")
            st.balloons()

        except Exception as e:
            st.error(f"❌ Error: {e}")
            progress_bar.empty()
            status.empty()

# ════════════════════════════════════════════════════════════
# STEP 4 — Results
# ════════════════════════════════════════════════════════════
if st.session_state.results:
    results = st.session_state.results

    st.markdown("""
    <div class="step-card">
        <div class="step-header">
            <div class="step-number">4</div>
            <div class="step-title">Ranked Shortlist</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    hire   = sum(1 for r in results if r.recommendation == "hire")
    review = sum(1 for r in results if r.recommendation == "review")
    no     = sum(1 for r in results if r.recommendation == "no-hire")

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card metric-total">
            <div class="number">{len(results)}</div>
            <div class="label">Total Candidates</div>
        </div>
        <div class="metric-card metric-hire">
            <div class="number">{hire}</div>
            <div class="label">Recommended Hire</div>
        </div>
        <div class="metric-card metric-review">
            <div class="number">{review}</div>
            <div class="label">Further Review</div>
        </div>
        <div class="metric-card metric-nohire">
            <div class="number">{no}</div>
            <div class="label">Not Suitable</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Filter
    filter_opt = st.radio(
        "Filter:",
        ["All", "Hire", "Review", "No-hire"],
        horizontal=True,
        label_visibility="collapsed"
    )

    filtered = results
    if filter_opt != "All":
        filtered = [r for r in results if r.recommendation == filter_opt.lower()]

    # Candidate Cards
    for rank, result in enumerate(filtered, 1):
        rec = result.recommendation
        score_class = "hire" if rec == "hire" else "review" if rec == "review" else "nohire"
        verdict_label = "✓ Hire" if rec == "hire" else "~ Review" if rec == "review" else "✗ No Hire"
        rank_class = f"rank-{rank}" if rank <= 3 else "rank-other"

        with st.expander(
            f"{'🥇' if rank==1 else '🥈' if rank==2 else '🥉' if rank==3 else '  '} "
            f"#{rank} {result.candidate_name} — {result.weighted_total}/10 — {verdict_label}",
            expanded=(rank == 1)
        ):
            col1, col2 = st.columns([3, 2])

            with col1:
                st.markdown("**📊 Dimension Scores**")

                dims = [
                    ("🎯 Skills Match",         "30%", result.skills_match),
                    ("💼 Experience Relevance", "25%", result.experience_relevance),
                    ("🎓 Education & Certs",    "15%", result.education_certs),
                    ("🚀 Project / Portfolio",  "20%", result.project_portfolio),
                    ("💬 Communication",        "10%", result.communication_quality),
                ]

                for dim_name, weight, dim in dims:
                    score = dim.score
                    pct = score * 10
                    bar_class = "bar-high" if score >= 7 else "bar-mid" if score >= 4 else "bar-low"
                    st.markdown(f"""
                    <div class="dim-row">
                        <div class="dim-label">
                            <span>{dim_name} <span style="color:#4a5568">({weight})</span></span>
                            <span style="color:{'#64ffda' if score>=7 else '#ffd700' if score>=4 else '#ff6b6b'};
                            font-weight:600">{score}/10</span>
                        </div>
                        <div class="dim-bar-bg">
                            <div class="dim-bar-fill {bar_class}" style="width:{pct}%"></div>
                        </div>
                        <div style="color:#4a5568;font-size:0.78rem;margin-top:3px;
                        font-style:italic">{dim.justification}</div>
                    </div>
                    """, unsafe_allow_html=True)

            with col2:
                st.markdown("**💪 Strengths**")
                for s in result.strengths:
                    st.markdown(f'<span class="tag-strength">✓ {s}</span>',
                               unsafe_allow_html=True)

                st.markdown("<br>**⚠️ Gaps**", unsafe_allow_html=True)
                for g in result.gaps:
                    st.markdown(f'<span class="tag-gap">✗ {g}</span>',
                               unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                total = result.weighted_total
                score_col = "#64ffda" if total >= 7.5 else "#ffd700" if total >= 5 else "#ff6b6b"
                st.markdown(f"""
                <div style="background:#0f1117;border-radius:10px;padding:16px;text-align:center;
                border:1px solid #2d3561;">
                    <div style="font-size:2.5rem;font-weight:700;color:{score_col}">
                        {total}/10
                    </div>
                    <div style="color:#8892b0;font-size:0.85rem">Weighted Total</div>
                    <div class="verdict verdict-{score_class}" style="margin-top:8px">
                        {verdict_label}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Override Section
            st.markdown("""
            <div class="override-box">
                <div class="override-title">🔧 HR Override</div>
            </div>
            """, unsafe_allow_html=True)

            ov_col1, ov_col2, ov_col3, ov_col4 = st.columns([2, 1, 2, 1])
            with ov_col1:
                ov_dim = st.selectbox(
                    "Dimension",
                    ["skills_match", "experience_relevance",
                     "education_certs", "project_portfolio",
                     "communication_quality"],
                    key=f"dim_{rank}"
                )
            with ov_col2:
                ov_score = st.number_input(
                    "New Score",
                    min_value=0, max_value=10, value=5,
                    key=f"score_{rank}"
                )
            with ov_col3:
                ov_reason = st.text_input(
                    "Reason",
                    placeholder="Why are you overriding this score?",
                    key=f"reason_{rank}"
                )
            with ov_col4:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Apply", key=f"override_{rank}"):
                    if ov_reason.strip():
                        st.session_state.results = override_score(
                            results=st.session_state.results,
                            candidate_name=result.candidate_name,
                            dimension=ov_dim,
                            new_score=ov_score,
                            reason=ov_reason
                        )
                        st.success("✅ Override applied!")
                        st.rerun()
                    else:
                        st.error("Please enter a reason.")

    # ── Export Reports ───────────────────────────────────────
    st.markdown("""
    <div class="step-card">
        <div class="step-header">
            <div class="step-number">5</div>
            <div class="step-title">Export Reports</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Generate & Download HTML Report",
                     use_container_width=True):
            path = generate_html_report(
                st.session_state.results,
                role=st.session_state.jd_role
            )
            with open(path, "r", encoding="utf-8") as f:
                st.download_button(
                    "⬇️ Download HTML",
                    f.read(),
                    file_name="shortlist_report.html",
                    mime="text/html",
                    use_container_width=True
                )

    with col2:
        if st.button("📊 Generate & Download JSON Report",
                     use_container_width=True):
            path = generate_json_report(st.session_state.results)
            with open(path, "r", encoding="utf-8") as f:
                st.download_button(
                    "⬇️ Download JSON",
                    f.read(),
                    file_name="shortlist_report.json",
                    mime="application/json",
                    use_container_width=True
                )