"""Local validator for Redrob submission shape."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ai_recruiter.ingest import iter_candidates


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("submission")
    parser.add_argument("--candidates", required=True)
    args = parser.parse_args()

    valid_ids = {candidate["candidate_id"] for candidate in iter_candidates(args.candidates)}
    with Path(args.submission).open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert list(rows[0].keys()) == ["candidate_id", "rank", "score", "reasoning"], "Wrong columns/order"
    assert len(rows) == 100, f"Expected 100 rows, got {len(rows)}"
    ranks = [int(row["rank"]) for row in rows]
    assert ranks == list(range(1, 101)), "Ranks must be exactly 1..100"
    ids = [row["candidate_id"] for row in rows]
    assert len(set(ids)) == 100, "Duplicate candidate IDs"
    missing = [candidate_id for candidate_id in ids if candidate_id not in valid_ids]
    assert not missing, f"Unknown candidate IDs: {missing[:5]}"
    scores = [float(row["score"]) for row in rows]
    assert all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1)), "Scores must be non-increasing"
    assert all(row["reasoning"].strip() for row in rows), "Reasoning cannot be empty"
    print("OK: submission format is valid.")


if __name__ == "__main__":
    main()
