# Security Risk Mitigation

This document covers all security risks as required by the project brief.

---

## 1. Prompt Injection

**Risk:** Malicious input in resumes or JD could manipulate agent behaviour.

**Mitigation:**
- All inputs sanitised before sending to LLM (HTML tags stripped, length limited)
- Structured output schemas enforced — LLM must return valid JSON only
- Pydantic models validate every LLM response before use
- If JSON parsing fails, agent throws error instead of using bad data

**Code location:** `src/jd_parser.py → sanitise_input()` and `src/resume_parser.py → mask_pii()`

---

## 2. Data Privacy / PII

**Risk:** Resumes contain personal info — emails, phone numbers, national IDs.

**Mitigation:**
- PII masked using regex before any text is sent to LLM API
- Emails replaced with [EMAIL]
- Phone numbers replaced with [PHONE]
- Aadhar numbers replaced with [AADHAR]
- Raw text never written to log files
- Only scores and names stored in run_log.txt

**Code location:** `src/resume_parser.py → mask_pii()`

---

## 3. API Key Exposure

**Risk:** Groq API key leaked in source code or GitHub.

**Mitigation:**
- API key stored in `.env` file only
- `.env` added to `.gitignore` on day one — never committed
- `.env.example` provided with placeholder values
- `python-dotenv` loads key at runtime via `os.getenv()`
- Never hardcoded anywhere in source code

**Code location:** `.env`, `.gitignore`, `.env.example`

---

## 4. Hallucination Risk

**Risk:** LLM generating false scores or wrong justifications.

**Mitigation:**
- JSON-only system prompts enforced on every LLM call
- Pydantic models validate all LLM responses
- Weighted total computed in Python — not trusted from LLM
- Confidence guardrail flags suspicious scores (0 or 10 with short justification)
- Human-in-the-loop override allows HR to correct any score
- Temperature set to 0.1 for consistent outputs

**Code location:** `src/scoring_engine.py → check_confidence()` and `compute_weighted_total()`

---

## 5. Unauthorised Access

**Risk:** Anyone could trigger the agent endpoint.

**Mitigation:**
- In this prototype: runs locally only
- In production: would add API key authentication on any exposed endpoint
- Would add rate limiting (max N requests per minute per user)
- Would add OAuth2 authentication for HR portal access
- Streamlit app runs on localhost by default

---

## 6. Email Spoofing (Task 2 relevant)

**Risk:** Emails appearing from wrong sender.

**Mitigation:**
- Not applicable to Task 1
- For Task 2: would implement SPF/DKIM/DMARC setup
- Would use verified sender domain only
- Would implement dry-run mode during testing
- Would never send real emails during development

---

## Summary Table

| Risk | Status |
|---|---|
| Prompt Injection | ✅ Mitigated |
| Data Privacy / PII | ✅ Mitigated |
| API Key Exposure | ✅ Mitigated |
| Hallucination Risk | ✅ Mitigated |
| Unauthorised Access | ✅ Mitigated |
| Email Spoofing | ✅ Documented |