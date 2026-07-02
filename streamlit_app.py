"""Small-sample demo app for the Redrob ranker.

Run locally:
    streamlit run streamlit_app.py
"""

from __future__ import annotations

import csv
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from ai_recruiter.features import extract_features
from ai_recruiter.reasoning import build_reasoning
from ai_recruiter.scoring import score_candidate


def rank_jsonl(text: str, top_k: int = 100) -> list[dict[str, object]]:
    rows = []
    for line in text.splitlines():
        if not line.strip():
            continue
        candidate = json.loads(line)
        features = extract_features(candidate)
        breakdown = score_candidate(features)
        rows.append(
            {
                "candidate_id": features.candidate_id,
                "rank": 0,
                "score": breakdown.score,
                "reasoning": build_reasoning(features, breakdown),
            }
        )
    rows.sort(key=lambda row: (-float(row["score"]), str(row["candidate_id"])))
    rows = rows[:top_k]
    for index, row in enumerate(rows, start=1):
        row["rank"] = index
        row["score"] = f"{float(row['score']):.6f}"
    return rows


def to_csv(rows: list[dict[str, object]]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["candidate_id", "rank", "score", "reasoning"])
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def main() -> None:
    import streamlit as st

    st.set_page_config(page_title="Redrob AI Recruiter Ranker", layout="wide")
    st.title("Redrob AI Recruiter Ranker")
    st.write("Upload a small JSONL sample and run the same offline scorer used for the final submission.")
    uploaded = st.file_uploader("Candidate JSONL", type=["jsonl", "txt"])
    top_k = st.slider("Top K", min_value=5, max_value=100, value=20)
    if uploaded:
        rows = rank_jsonl(uploaded.read().decode("utf-8"), top_k)
        st.dataframe(rows, use_container_width=True)
        st.download_button("Download ranked CSV", to_csv(rows), "ranked_candidates.csv", "text/csv")


if __name__ == "__main__":
    main()
