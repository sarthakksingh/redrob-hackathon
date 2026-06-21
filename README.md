# Redrob AI Recruiter Ranking System

An explainable, CPU-only candidate ranker for the Redrob Intelligent Candidate Discovery & Ranking Challenge.

## Day 1 status

- Streaming JSONL ingestion is implemented: no need to load the 100,000-candidate dataset into memory.
- `scripts/profile_data.py` creates a reproducible data-profile report.
- Ranking logic is intentionally not implemented yet; it will be added after feature design and trap analysis.

## Setup

This first milestone uses only the Python standard library.

```powershell
python scripts/profile_data.py --candidates "..\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl" --out reports\data_profile.md
```

## Repository layout

```text
ai-recruiter-ranking/
  README.md
  requirements.txt
  reports/
  scripts/
    profile_data.py
  src/
    ai_recruiter/
      __init__.py
      ingest.py
```

## Next milestone

Build candidate features from career evidence, skills, location, and Redrob engagement signals; then score and inspect a broad shortlist before producing the final top 100.
