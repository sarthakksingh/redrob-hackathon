"""Deterministic recruiter-style scoring for the Redrob challenge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .features import CandidateFeatures, profile_flags
from .normalize import clamp, safe_float


@dataclass(frozen=True)
class ScoreBreakdown:
    score: float
    career: float
    retrieval_eval: float
    production_product: float
    logistics: float
    engagement: float
    penalty: float
    flags: dict[str, Any]


def score_candidate(features: CandidateFeatures) -> ScoreBreakdown:
    flags = profile_flags(features)

    career = career_score(features, flags)
    retrieval_eval = retrieval_eval_score(flags)
    production_product = production_product_score(flags)
    logistics = logistics_score(features, flags)
    engagement = engagement_score(features)
    penalty = penalty_score(features, flags)

    raw = (
        0.45 * career
        + 0.20 * retrieval_eval
        + 0.15 * production_product
        + 0.10 * logistics
        + 0.10 * engagement
        - penalty
    )
    return ScoreBreakdown(
        score=round(clamp(raw), 6),
        career=career,
        retrieval_eval=retrieval_eval,
        production_product=production_product,
        logistics=logistics,
        engagement=engagement,
        penalty=penalty,
        flags=flags,
    )


def career_score(features: CandidateFeatures, flags: dict[str, Any]) -> float:
    title = min(flags["title_hits"] * 0.23, 0.46)
    career_ai = min(flags["career_ai_hits"] * 0.08, 0.32)
    skill_support = min(flags["skill_ai_count"] * 0.025, 0.12)
    production = min(flags["production_hits"] * 0.03, 0.18)
    base = title + career_ai + skill_support + production

    if 5 <= features.years <= 9:
        base += 0.10
    elif 4 <= features.years < 5 or 9 < features.years <= 11:
        base += 0.05

    if flags["bad_title_hits"] and flags["career_ai_hits"] < 2:
        base -= 0.35
    elif flags["bad_title_hits"]:
        base -= 0.12

    return clamp(base)


def retrieval_eval_score(flags: dict[str, Any]) -> float:
    retrieval = min(flags["retrieval_hits"] * 0.12, 0.72)
    evaluation = min(flags["eval_hits"] * 0.14, 0.28)
    return clamp(retrieval + evaluation)


def production_product_score(flags: dict[str, Any]) -> float:
    production = min(flags["production_hits"] * 0.08, 0.48)
    product = min(flags["product_industry_hits"] * 0.12, 0.36)
    service_drag = 0.18 if flags["service_industry_hits"] >= 2 and flags["product_industry_hits"] == 0 else 0.0
    return clamp(production + product - service_drag)


def logistics_score(features: CandidateFeatures, flags: dict[str, Any]) -> float:
    score = 0.0
    if features.is_india:
        score += 0.20
    if flags["located_well"]:
        score += 0.22
    if bool(features.signals.get("willing_to_relocate")):
        score += 0.16

    notice = safe_float(features.signals.get("notice_period_days"), 180)
    if notice <= 30:
        score += 0.22
    elif notice <= 60:
        score += 0.12
    elif notice <= 90:
        score += 0.05

    if 5 <= features.years <= 9:
        score += 0.20
    elif 4 <= features.years <= 11:
        score += 0.10
    return clamp(score)


def engagement_score(features: CandidateFeatures) -> float:
    signals = features.signals
    score = 0.0
    if bool(signals.get("open_to_work_flag")):
        score += 0.18

    response_rate = safe_float(signals.get("recruiter_response_rate"))
    score += min(response_rate * 0.22, 0.22)

    avg_hours = safe_float(signals.get("avg_response_time_hours"), 999)
    if avg_hours <= 12:
        score += 0.10
    elif avg_hours <= 36:
        score += 0.06
    elif avg_hours <= 72:
        score += 0.03

    recent_days = features.signals.get("_recent_days")
    if recent_days is None:
        from .normalize import days_since

        recent_days = days_since(signals.get("last_active_date"))
    if recent_days is not None:
        if recent_days <= 30:
            score += 0.14
        elif recent_days <= 90:
            score += 0.09
        elif recent_days <= 180:
            score += 0.04

    github = safe_float(signals.get("github_activity_score"), -1)
    if github >= 75:
        score += 0.10
    elif github >= 40:
        score += 0.06
    elif github >= 10:
        score += 0.03

    saved = safe_float(signals.get("saved_by_recruiters_30d"))
    search = safe_float(signals.get("search_appearance_30d"))
    score += min(saved / 20.0, 0.08)
    score += min(search / 250.0, 0.05)
    score += min(safe_float(signals.get("interview_completion_rate")) * 0.08, 0.08)
    score += min(safe_float(signals.get("offer_acceptance_rate"), 0) * 0.05, 0.05)
    return clamp(score)


def penalty_score(features: CandidateFeatures, flags: dict[str, Any]) -> float:
    penalty = 0.0
    if features.years < 3:
        penalty += 0.18
    if features.years > 14:
        penalty += 0.10
    if flags["bad_title_hits"] and flags["retrieval_hits"] == 0:
        penalty += 0.22
    if flags["service_industry_hits"] >= 2 and flags["product_industry_hits"] == 0 and flags["retrieval_hits"] < 2:
        penalty += 0.12
    if flags["expert_zero_duration_count"] >= 4:
        penalty += 0.25
    if flags["all_ai_hits"] >= 10 and flags["career_ai_hits"] <= 1:
        penalty += 0.18

    recent_days = flags.get("recent_days")
    response_rate = safe_float(features.signals.get("recruiter_response_rate"))
    if recent_days is not None and recent_days > 180:
        penalty += 0.10
    if response_rate < 0.15:
        penalty += 0.08
    if safe_float(features.signals.get("notice_period_days"), 0) > 120:
        penalty += 0.06
    return clamp(penalty, 0.0, 0.55)
