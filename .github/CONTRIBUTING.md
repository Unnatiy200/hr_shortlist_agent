# Contributing

## Setup
1. Fork the repo
2. Clone your fork
3. Install dependencies: `pip install -r requirements.txt`
4. Add your API key to `.env`
5. Run: `streamlit run app.py`

## Project Structure
- `src/jd_parser.py` — JD parsing module
- `src/resume_parser.py` — Resume/LinkedIn parsing
- `src/scoring_engine.py` — 5-dimension scoring rubric
- `src/agent.py` — Main orchestrator + HR override
- `src/report_generator.py` — HTML + JSON reports
- `app.py` — Streamlit UI