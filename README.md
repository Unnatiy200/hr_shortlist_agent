# HR Resume & LinkedIn Shortlisting Agent

An AI-powered HR agent that evaluates candidates against a Job Description
and produces a ranked shortlist with transparent scoring rubric.

---

## Project Overview

HR teams screen hundreds of applications per role leading to fatigue and bias.
This agent standardises evaluation using LLM-powered scoring across 5 dimensions
while keeping humans in the loop for final decisions.

---

## Agent Architecture

Input (JD + Resumes/LinkedIn)
↓
JD Parser (src/jd_parser.py)
Extracts: role, skills, experience, domain, education
↓
Resume Parser (src/resume_parser.py)
Extracts: skills, experience, projects, education
Masks: emails, phones, PII
↓
Scoring Engine (src/scoring_engine.py)
Scores 5 dimensions using LLM
Computes weighted total in Python
↓
Agent Orchestrator (src/agent.py)
Ranks candidates by score
Logs results (no PII)
↓
Report Generator (src/report_generator.py)
Outputs HTML + JSON reports
↓
HR Override (src/agent.py → override_score)
HR adjusts scores with reason
All changes logged to data/override_log.json

---

## Scoring Rubric

| Dimension | Weight | 0 — Poor | 5 — Average | 10 — Excellent |
|---|---|---|---|---|
| Skills Match | 30% | <30% match | 50–70% match | >85% match |
| Experience Relevance | 25% | Unrelated domain | Adjacent domain | Exact domain & seniority |
| Education & Certs | 15% | Below minimum | Meets minimum | Exceeds + extra certs |
| Project / Portfolio | 20% | No evidence | 1–2 generic | Strong relevant portfolio |
| Communication | 10% | Poor structure | Adequate | Crisp and impactful |

---

## Tech Stack & Decision Log

| Layer | Choice | Reason |
|---|---|---|
| LLM | Groq LLaMA 3.3 70B | Free tier, fast, strong reasoning, JSON mode support |
| Agent Framework | Direct API + Orchestrator | Simple, transparent, no framework overhead for prototype |
| Resume Parse | pdfplumber + python-docx | Best text extraction for PDF and DOCX |
| Output | Jinja2 HTML + JSON | Lightweight, no extra dependencies |
| UI | Streamlit | Fastest way to build HR-facing interface |
| Validation | Pydantic | Structured output enforcement, catches hallucinations |

### LLM Choice Rationale
We chose Groq LLaMA 3.3 70B over Gemini 1.5 Pro and GPT-4o because:
- Completely free with generous rate limits
- Fast inference (ideal for scoring multiple candidates)
- Strong instruction following for JSON-only outputs
- Architecture is LLM-agnostic — swap to any model by changing one line

### Prompt Design
- System prompts enforce JSON-only output with explicit schema
- Temperature set to 0.1 for consistent scoring
- PII masked before any text reaches the LLM
- Rubric anchors (0/5/10) included in every scoring prompt

---

## Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/Unnatiy200/hr_shortlist_agent.git
cd hr_shortlist_agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment
```bash
cp .env.example .env
# Edit .env and add your Groq API key
```

### 4. Run the Streamlit app
```bash
streamlit run app.py
```

### 5. Or run pipeline directly
```bash
python -m src.agent
```

---

## Sample Output

See `docs/sample_output/` for:
- `shortlist_report.html` — full ranked report with scoring breakdown
- `shortlist_report.json` — machine-readable results

---

## Security

See [SECURITY.md](SECURITY.md) for full security risk mitigation documentation.

---

## Project Structure

hr_shortlist_agent/
├── src/
│   ├── jd_parser.py          # JD parsing module
│   ├── resume_parser.py      # Resume/LinkedIn parsing
│   ├── scoring_engine.py     # 5-dimension scoring rubric
│   ├── agent.py              # Main orchestrator + override
│   └── report_generator.py  # HTML + JSON report generation
├── templates/
│   └── report.html           # Jinja2 report template
├── data/
│   ├── sample_resumes/       # Sample PDF/DOCX files
│   ├── override_log.json     # HR override audit trail
│   └── run_log.txt           # Run logs (no PII)
├── output/                   # Generated reports
├── docs/sample_output/       # Sample outputs for submission
├── app.py                    # Streamlit UI
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
├── SECURITY.md               # Security documentation
└── README.md                 # This file