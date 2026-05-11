***# Prompt Design Documentation***



***## 1. JD Parser Prompt***



***You are a JD parser for an HR system.***

***Extract structured requirements from the job description.***

***Return ONLY valid JSON — no markdown, no explanation, no extra text.***



***### Design Decisions***

***- JSON-only instruction prevents markdown wrapping***

***- Explicit schema provided so LLM knows exact field names***

***- Temperature set to 0.1 for consistent extraction***

***- Input limited to 4000 chars to prevent token overflow***



***### Guardrails***

***- Pydantic validates output before use***

***- HTML tags stripped from input***

***- Empty input rejected before API call***



***### Iterations***

***- v1: No schema in prompt → inconsistent field names***

***- v2: Added explicit schema → consistent output ✅***

***- v3: Added temperature 0.1 → more reliable ✅***



***---***



***## 2. Resume Parser Prompt***



***### System Prompt***

***You are a resume parser for an HR system.***

***Extract structured information from the resume text.***

***Return ONLY valid JSON — no markdown, no explanation, no extra text.***



***### Design Decisions***

***- PII masked BEFORE sending to LLM***

***- Resume text limited to 3000 chars***

***- Structured fields force consistent output***



***### Guardrails***

***- Pydantic validates all extracted fields***

***- PII regex runs before any LLM call***

***- Emails replaced with \[EMAIL]***

***- Phones replaced with \[PHONE]***



***### Iterations***

***- v1: Sent raw resume text → PII leaked to API***

***- v2: Added PII masking → secure ✅***

***- v3: Added char limit → faster responses ✅***



***---***



***## 3. Scoring Engine Prompt***



***### System Prompt***

***You are an expert HR scoring agent.***

***Score candidates against job requirements using a strict rubric.***

***Return ONLY valid JSON — no markdown, no explanation, no extra text.***

***SCORING RUBRIC (score 0-10):***



***Skills Match (30%): 0-3 poor, 4-6 average, 7-10 excellent***

***Experience Relevance (25%): 0-3 unrelated, 4-6 adjacent, 7-10 exact***

***Education \& Certs (15%): 0-3 below min, 4-6 meets min, 7-10 exceeds***

***Project/Portfolio (20%): 0-3 none, 4-6 generic, 7-10 strong***

***Communication (10%): 0-3 poor, 4-6 adequate, 7-10 excellent***



***### Design Decisions***

***- Rubric anchors given explicitly to reduce ambiguity***

***- Candidate name anonymised as CANDIDATE\_ANONYMOUS***

***- Weighted total computed in Python NOT by LLM***

***- One justification sentence required per dimension***

***- Temperature 0.1 for consistent scoring***



***### Guardrails***

***- Pydantic validates score ranges***

***- Confidence check flags suspicious extreme scores***

***- Human override available for any score***

***- Weighted total never trusted from LLM***



***### Iterations***

***- v1: Asked LLM to compute weighted total → wrong math***

***- v2: Moved weighted total to Python → accurate ✅***

***- v3: Added rubric anchors → consistent scores ✅***

***- v4: Anonymised candidate name → reduced bias ✅***

***- v5: Added one sentence justification rule → clearer output ✅***

