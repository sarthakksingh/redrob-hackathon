# Redrob AI Recruiter Ranking System

An explainable, CPU-only candidate ranker for the Redrob Intelligent Candidate Discovery & Ranking Challenge.

The system ranks candidates for the **Senior AI Engineer - Founding Team at Redrob AI** role by reading career evidence, retrieval/ranking experience, production/product context, logistics, and Redrob behavioral signals. It intentionally avoids the keyword-stuffing trap in the sample submission.

## Final deliverables

- Ranked CSV: `deliverables/redrob_submission.csv`
- Portal XLSX copy: `deliverables/redrob_submission.xlsx`
- Approach deck PDF: `deliverables/redrob_ai_recruiter_approach.pdf`

## Reproduce the ranking

This ranking step uses only the Python standard library. It makes no network calls and does not require a GPU.

```powershell
python scripts\rank_candidates.py `
  --candidates "C:\path\to\candidates.jsonl" `
  --out deliverables\redrob_submission.csv `
  --xlsx deliverables\redrob_submission.xlsx
```

Expected local runtime on the released 100,000-candidate file: about 55 seconds on this Windows laptop, well below the 5-minute CPU-only limit.

Validate the generated CSV:

```powershell
python scripts\validate_local.py deliverables\redrob_submission.csv --candidates "C:\path\to\candidates.jsonl"
python "C:\path\to\validate_submission.py" deliverables\redrob_submission.csv
```

## Method

The ranker streams `candidates.jsonl` and keeps only the best candidates in memory. Each profile is converted into structured recruiter-style signals:

- career/title fit for AI, ML, search, retrieval, recommendation, ranking, NLP and senior software roles
- evidence of retrieval, hybrid search, vector databases, embeddings and ranking-system evaluation
- production language such as shipped, deployed, launched, owned, scaled, monitored, on-call and real users
- product-company context versus service-only histories
- experience band, location, relocation willingness and notice period
- Redrob activity signals such as open-to-work, last active date, recruiter response rate, interview completion and GitHub activity
- penalties for nontechnical title traps, pure keyword stuffing, inactive profiles, service-only weak fits and honeypot-like skill inconsistencies

Final score:

```text
45% career evidence / title fit
20% retrieval, ranking and evaluation evidence
15% production and product-company context
10% experience, location and logistics
10% engagement and availability
- explicit risk penalties
```

Reasoning strings are generated from the same observed profile fields, so they stay specific and non-hallucinated.

## Demo / sandbox path

The repo includes `streamlit_app.py`, a small-sample demo app that accepts a JSONL upload and runs the same scorer:

```powershell
pip install streamlit
streamlit run streamlit_app.py
```

For a hosted sandbox, deploy this repository to Streamlit Cloud or HuggingFace Spaces and set the app entry point to `streamlit_app.py`.

## Repository layout

```text
.
├── deliverables/
│   ├── redrob_ai_recruiter_approach.pdf
│   ├── redrob_submission.csv
│   └── redrob_submission.xlsx
├── reports/
│   └── data_profile.md
├── scripts/
│   ├── create_deck_pdf.py
│   ├── profile_data.py
│   ├── rank_candidates.py
│   └── validate_local.py
├── src/ai_recruiter/
│   ├── export.py
│   ├── features.py
│   ├── ingest.py
│   ├── normalize.py
│   ├── reasoning.py
│   └── scoring.py
├── streamlit_app.py
├── submission_metadata.yaml
└── requirements.txt
```

## Notes

- The large `candidates.jsonl` file is intentionally not committed.
- The submitted ranking is produced by code, not manual edits.
- AI tools were used for implementation assistance, but the ranker itself does not call any LLM or hosted API.
