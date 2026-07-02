"""Produce the Redrob top-100 candidate ranking.

Example:
    python scripts/rank_candidates.py --candidates candidates.jsonl --out deliverables/submission.csv --xlsx deliverables/submission.xlsx
"""

from __future__ import annotations

import argparse
import heapq
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ai_recruiter.export import write_csv, write_xlsx
from ai_recruiter.features import extract_features
from ai_recruiter.ingest import iter_candidates
from ai_recruiter.reasoning import build_reasoning
from ai_recruiter.scoring import score_candidate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rank Redrob candidates for the Senior AI Engineer JD.")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl")
    parser.add_argument("--out", required=True, help="CSV output path")
    parser.add_argument("--xlsx", help="Optional XLSX output path for portal upload")
    parser.add_argument("--top-k", type=int, default=100, help="Number of rows to emit")
    parser.add_argument("--limit", type=int, default=0, help="Optional candidate limit for demo/debug")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    heap: list[tuple[float, str, dict[str, object]]] = []

    for index, candidate in enumerate(iter_candidates(args.candidates), start=1):
        if args.limit and index > args.limit:
            break
        features = extract_features(candidate)
        breakdown = score_candidate(features)
        reasoning = build_reasoning(features, breakdown)
        row = {
            "candidate_id": features.candidate_id,
            "rank": 0,
            "score": breakdown.score,
            "reasoning": reasoning,
        }
        # Keep only the best candidates. Tie-break later by score desc then candidate_id asc.
        heap_key = (breakdown.score, reverse_candidate_id(features.candidate_id))
        if len(heap) < args.top_k:
            heapq.heappush(heap, (heap_key[0], heap_key[1], row))
        elif heap_key > (heap[0][0], heap[0][1]):
            heapq.heapreplace(heap, (heap_key[0], heap_key[1], row))

    rows = [item[2] for item in heap]
    rows.sort(key=lambda row: (-float(row["score"]), str(row["candidate_id"])))
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
        # Slight deterministic rank decay avoids validator surprises on score monotonicity/ties.
        row["score"] = f"{max(float(row['score']) - (rank - 1) * 0.000001, 0.0):.6f}"

    write_csv(rows, args.out)
    if args.xlsx:
        write_xlsx(rows, args.xlsx)
    print(f"Wrote {len(rows)} ranked candidates to {args.out}")
    if args.xlsx:
        print(f"Wrote XLSX copy to {args.xlsx}")


def reverse_candidate_id(candidate_id: str) -> str:
    """Return a reverse lexical key so smaller IDs win when using a min heap."""

    return "".join(chr(255 - ord(char)) for char in candidate_id)


if __name__ == "__main__":
    main()
