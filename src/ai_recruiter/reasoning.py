"""Human-readable, non-hallucinated reasoning for ranked candidates."""

from __future__ import annotations

from .features import CandidateFeatures
from .scoring import ScoreBreakdown


def build_reasoning(features: CandidateFeatures, breakdown: ScoreBreakdown) -> str:
    flags = breakdown.flags
    parts: list[str] = []

    title = features.current_title.title() if features.current_title else "Candidate"
    years = f"{features.years:.1f}".rstrip("0").rstrip(".")
    parts.append(f"{title} with {years} years")

    if flags["retrieval_hits"] >= 3 and flags["eval_hits"] >= 1:
        parts.append("career evidence in retrieval/ranking plus evaluation")
    elif flags["retrieval_hits"] >= 3:
        parts.append("strong search/retrieval/ranking evidence")
    elif flags["career_ai_hits"] >= 3:
        parts.append("applied ML/NLP evidence in career history")
    elif flags["skill_ai_count"] >= 4:
        parts.append("AI skills supported by duration/endorsements")

    if flags["production_hits"] >= 4:
        parts.append("production-shipping language in role history")
    if flags["product_industry_hits"] >= 1:
        parts.append("product/software context")

    logistics: list[str] = []
    if "pune" in features.location or "noida" in features.location:
        logistics.append(features.location.title())
    elif flags["located_well"]:
        logistics.append("near target hiring hubs")
    if bool(features.signals.get("willing_to_relocate")):
        logistics.append("relocation-open")
    if bool(features.signals.get("open_to_work_flag")):
        logistics.append("open to work")
    if logistics:
        parts.append(", ".join(logistics))

    concerns: list[str] = []
    if breakdown.penalty >= 0.18:
        concerns.append("penalized for weak/nontechnical or inconsistent signals")
    elif breakdown.penalty >= 0.08:
        concerns.append("some availability/profile-risk penalty")
    notice = features.signals.get("notice_period_days")
    if isinstance(notice, int | float) and notice > 90:
        concerns.append(f"{notice:g}-day notice period")
    if concerns:
        parts.append("concern: " + "; ".join(concerns))

    sentence = "; ".join(parts)
    return sentence[:650]
