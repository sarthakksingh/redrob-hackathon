# Redrob AI Recruiter Ranking — Build Plan

## Objective

Rank the best 100 candidates for **Senior AI Engineer — Founding Team** from
`candidates.jsonl`, then produce a valid CSV with:

```text
candidate_id,rank,score,reasoning
```

The final run must be CPU-only, complete in under five minutes with 16 GB RAM,
and make no network/API calls. The system should be reproducible with one
command and should explain every recommendation in evidence-based language.

## Product decision

Build a deterministic, feature-based ranking pipeline. Do not make embeddings
or a hosted LLM a dependency of the final scoring run. The supplied data and
rubric reward credible career evidence more than semantic similarity, and a
transparent scorer is easier to tune, test, demonstrate, and defend.

Optional semantic retrieval can be evaluated later as an **offline development
experiment**, but the submission ranker remains a standard-library-friendly
hybrid of title, career-description, skills, company/industry, and Redrob
signals.

## System layout

```text
candidates.jsonl
      |
      v
streaming JSONL reader
      |
      v
feature extractor
  - titles and years of experience
  - career-history descriptions and tenure
  - technical capabilities and evidence counts
  - industry/product-company history
  - location and availability
  - Redrob engagement/activity signals
  - contradiction / honeypot flags
      |
      v
weighted scorer + gating rules
      |
      v
top 300 audit report (CSV/Markdown)
      |
      v
human weight tuning and top-100 review
      |
      v
validated submission CSV + metadata + small demo
```

## Scoring model (0–100)

Keep score components visible in the audit output. The final score is capped
to 0–100 after penalties.

| Component | Points | What counts as evidence |
|---|---:|---|
| Career evidence and role fit | 0–35 | Relevant current/past title and credible descriptions of applied ML, NLP, IR, retrieval, search, recommendation, or ranking work. |
| Retrieval, ranking, and evaluation | 0–20 | Vector/hybrid search, embeddings, semantic retrieval, recommender/ranking systems, NDCG/MRR/MAP, offline/online evaluation. Career-history evidence outweighs skill-list mentions. |
| Production ML and product impact | 0–18 | Built, deployed, shipped, scaled, monitored, served, production APIs/pipelines, measurable business/product impact. |
| Product-company fit | 0–8 | SaaS, software product, startup, marketplace, e-commerce, fintech, AI/ML. Award across history; consulting-only paths receive no bonus. |
| Experience and logistics | 0–9 | Best reward at 5–9 years; nearby Pune/Noida, relocation interest, shorter notice. |
| Engagement and availability | 0–10 | Open-to-work, recent activity, recruiter-response rate, interview completion, GitHub activity. |
| Penalties | 0 to -45 | Keyword stuffing, contradiction/honeypot signals, non-technical history, CV/speech/robotics-only background, research-only path, consulting-only history, low availability. |

### Scoring principles

1. A skill mentioned only in `skills` earns little; the same skill supported by
   a career description earns materially more.
2. Engagement adjusts an already relevant candidate; it must never promote an
   otherwise irrelevant person into the shortlist.
3. Use soft experience scores—not hard exclusions—so an exceptional 4.5- or
   9.5-year candidate can still rank.
4. Require credible technical/career evidence for the final top 100. A title
   match alone is insufficient.

## Feature rules to implement

### Positive evidence lexicons

Use normalised, case-insensitive phrase matching on title and career
descriptions. Keep terms grouped so a candidate's explanation can say *why*
they matched.

- **Applied AI/ML:** machine learning, applied scientist, ML engineer, data
  scientist, NLP, LLM (only when paired with production evidence).
- **Search/retrieval/ranking:** information retrieval, search, semantic search,
  vector search, embeddings, RAG, retrieval, recommendation, recommender,
  ranking, relevance, query understanding.
- **Evaluation:** NDCG, MRR, MAP, precision/recall, A/B test, offline
  evaluation, relevance metrics.
- **Production:** deployed, production, shipped, serving, inference, API,
  pipeline, scale, monitoring, latency, reliability, impact.
- **Technical foundations:** Python, SQL, PyTorch, TensorFlow, scikit-learn,
  Spark, Elasticsearch/OpenSearch, FAISS, vector database, Docker, Kubernetes,
  cloud.

### Negative evidence and gates

- Penalize careers that contain only research/academic evidence and no shipping
  evidence.
- Penalize CV, speech, robotics, or hardware-only work when there is no
  NLP/search/retrieval/ranking signal.
- Penalize generic recent `LangChain`/`OpenAI` demo language unless supported
  by earlier production ML history.
- Penalize consulting/services-only histories; do not automatically reject a
  candidate who also has strong product evidence.
- Apply a heavy penalty to clearly non-technical career histories, even when
  their skills list contains AI words.
- Flag but do not silently discard contradictory timelines, impossible skill
  durations, and seniority claims unsupported by work history.

### Honeypot checks

Put each check and its penalty in one named function so it can be tested:

1. Overlapping roles or total tenure materially inconsistent with stated years.
2. Skills claimed for longer than the candidate's full career.
3. Expert/proficient ML skill lists with no matching role or description text.
4. Relevant current title but no relevant career evidence.
5. Sudden recent LLM buzzwords on an otherwise unrelated career path.

## Repository layout at completion

```text
ai-recruiter-ranking/
  README.md                         # setup, one-command reproduction, method
  requirements.txt                  # preferably no required third-party deps
  submission_metadata.yaml          # completed from challenge template
  BUILD_PLAN.md
  .gitignore                        # excludes data/, outputs/, __pycache__
  src/ai_recruiter/
    ingest.py                       # existing streaming reader
    normalize.py                    # safe text/date/number helpers
    features.py                     # candidate -> feature dictionary
    scoring.py                      # component scores, penalties, total
    reasoning.py                    # factual one-sentence explanations
    export.py                       # sorting and CSV output
  scripts/
    profile_data.py                 # existing profiling
    rank_candidates.py              # end-to-end CLI
    audit_shortlist.py              # ranked top-N detailed review file
    validate_local.py               # IDs, fields, ranks, descending scores
  tests/
    test_features.py
    test_scoring.py
    test_submission.py
  demo/
    app.py                          # small Streamlit demo or a Colab notebook
  reports/
    data_profile.md
    shortlist_audit.md              # generated, no candidate PII in Git if prohibited
  outputs/
    .gitkeep
```

## Required command interface

The README should advertise a command shaped like this:

```powershell
python scripts/rank_candidates.py `
  --candidates "C:\path\to\candidates.jsonl" `
  --out outputs\your_participant_id.csv `
  --audit-out reports\shortlist_audit.md
python validate_submission.py outputs\your_participant_id.csv
```

The script must stream the input, retain only the scored candidates needed for
the final sort/audit, and include a `--limit` option for the demo sample.

## Ten-day execution plan

| Day | Deliverable | Definition of done |
|---|---|---|
| 1 | Data understanding | Existing streaming reader and profile report; schema and sample output inspected. |
| 2 | Feature extraction | `normalize.py` and `features.py` produce structured evidence for sample candidates. |
| 3 | Baseline ranker | Scoring, explanations, CSV export; valid top 100 generated. |
| 4 | Career-evidence depth | Separate title, description, production, IR/ranking, and evaluation evidence; skills are supporting only. |
| 5 | Trap defence | Honeypot, keyword-stuffing, research-only, services-only, and non-technical penalties tested. |
| 6 | Recruiter signals | Experience/location/notice/activity/response/interview features added and documented. |
| 7 | Audit and tuning | Inspect top 300, tune against obvious false positives and false negatives, record changes. |
| 8 | Reliability | Tests, deterministic output, local validation, runtime/memory measurement. |
| 9 | Demo and handoff | Small Streamlit/Colab sandbox; README and metadata complete; GitHub repo cleaned. |
| 10 | Submission rehearsal | Fresh run from documented command, validate CSV, inspect every top-100 explanation and ID, submit. |

## Manual shortlist review rubric

Review the top 200–300 in a spreadsheet/audit report. For each candidate ask:

1. Would a senior recruiter believe the evidence without reading the skills
   list?
2. Is there real NLP/IR/retrieval/ranking or applied ML work, not just generic
   AI wording?
3. Did they build and ship something? Is the impact credible?
4. Is the career path product-oriented enough for a founding-team role?
5. Are there timeline, duration, or activity warning signs?

Tune broad component weights only after collecting several concrete examples;
avoid one-off rules tailored to a single candidate.

## Submission checklist

- [ ] CSV has exactly 100 candidates and columns in the required order.
- [ ] Ranks are unique integers 1–100; scores are descending and finite.
- [ ] Each ID exists in `candidates.jsonl`.
- [ ] Every reasoning string cites actual evidence, no invented claims.
- [ ] `python validate_submission.py ...` passes.
- [ ] Fresh CPU-only run is under five minutes with no network calls.
- [ ] `README.md`, dependencies, `submission_metadata.yaml`, and demo link are complete.
- [ ] Dataset and generated submission are not committed unless the rules explicitly permit it.
