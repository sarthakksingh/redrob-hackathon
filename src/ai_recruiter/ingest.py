"""Memory-safe utilities for reading Redrob candidate JSONL files."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any


Candidate = dict[str, Any]


def iter_candidates(path: str | Path) -> Iterator[Candidate]:
    """Yield one validated JSON object at a time from a JSONL or JSON sample file.

    The challenge dataset is large (~100K profiles), so callers should process
    this iterator directly rather than collect it into a list.
    """

    path = Path(path)
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = data.get("candidates", [])
        if not isinstance(data, list):
            raise ValueError(f"Expected {path.name} to contain a list of candidates.")
        for index, candidate in enumerate(data, start=1):
            if not isinstance(candidate, dict):
                raise ValueError(f"Expected candidate object at index {index} in {path.name}.")
            yield candidate
        return

    with path.open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                candidate = json.loads(stripped)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON on line {line_number} of {path.name}: {error.msg}"
                ) from error
            if not isinstance(candidate, dict):
                raise ValueError(
                    f"Expected an object on line {line_number} of {path.name}."
                )
            yield candidate
