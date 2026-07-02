"""Feature extraction for Redrob candidate profiles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .normalize import count_any, days_since, has_any, safe_float, text


Candidate = dict[str, Any]


TECH_TITLES = {
    "ai engineer",
    "machine learning",
    "ml engineer",
    "data scientist",
    "applied scientist",
    "nlp",
    "search engineer",
    "ranking",
    "recommendation",
    "recommender",
    "backend engineer",
    "software engineer",
    "data engineer",
    "platform engineer",
    "founding engineer",
}

BAD_TITLES = {
    "hr manager",
    "recruiter",
    "marketing",
    "content writer",
    "graphic designer",
    "sales",
    "business analyst",
    "mechanical engineer",
    "civil engineer",
    "finance manager",
    "accountant",
    "teacher",
}

AI_TERMS = {
    "machine learning",
    "deep learning",
    "ml",
    "ai",
    "nlp",
    "llm",
    "transformer",
    "bert",
    "rag",
    "fine-tuning",
    "fine tuning",
    "recommendation",
    "recommender",
    "ranking",
    "search",
    "retrieval",
    "embedding",
    "embeddings",
    "vector",
    "semantic",
}

RETRIEVAL_TERMS = {
    "retrieval",
    "ranking",
    "ranker",
    "recommendation",
    "recommender",
    "search",
    "semantic search",
    "hybrid search",
    "bm25",
    "vector",
    "embedding",
    "embeddings",
    "faiss",
    "pinecone",
    "weaviate",
    "qdrant",
    "milvus",
    "elasticsearch",
    "opensearch",
    "solr",
}

EVAL_TERMS = {
    "ndcg",
    "mrr",
    "map",
    "precision@",
    "recall@",
    "a/b",
    "ab test",
    "online experiment",
    "offline evaluation",
    "evaluation framework",
    "ranking metrics",
    "feedback loop",
}

PRODUCTION_TERMS = {
    "production",
    "deployed",
    "shipped",
    "launched",
    "served",
    "real users",
    "users",
    "scale",
    "latency",
    "monitoring",
    "pipeline",
    "index refresh",
    "drift",
    "on-call",
    "owned",
    "built",
    "implemented",
}

PRODUCT_INDUSTRIES = {
    "software",
    "saas",
    "ai/ml",
    "e-commerce",
    "fintech",
    "marketplace",
    "hr tech",
    "edtech",
    "healthtech",
}

SERVICE_COMPANIES = {
    "tcs",
    "infosys",
    "wipro",
    "accenture",
    "cognizant",
    "capgemini",
    "mindtree",
    "hcl",
    "tech mahindra",
    "lti",
    "ltimindtree",
}

GOOD_LOCATIONS = {
    "pune",
    "noida",
    "delhi",
    "gurgaon",
    "gurugram",
    "ncr",
    "mumbai",
    "bangalore",
    "bengaluru",
    "hyderabad",
}


@dataclass(frozen=True)
class CandidateFeatures:
    candidate_id: str
    current_title: str
    location: str
    country: str
    years: float
    career_text: str
    all_text: str
    skills: list[dict[str, Any]]
    signals: dict[str, Any]
    current_industry: str
    career_industries: list[str]
    companies: list[str]
    current_company: str
    current_company_size: str

    @property
    def is_india(self) -> bool:
        return "india" in self.country.lower()


def extract_features(candidate: Candidate) -> CandidateFeatures:
    profile = candidate.get("profile", {}) or {}
    history = candidate.get("career_history", []) or []
    skills = candidate.get("skills", []) or []
    signals = candidate.get("redrob_signals", {}) or {}

    career_bits: list[str] = []
    companies: list[str] = []
    industries: list[str] = []
    for role in history:
        companies.append(text(role.get("company")))
        industries.append(text(role.get("industry")))
        career_bits.extend(
            [
                text(role.get("title")),
                text(role.get("company")),
                text(role.get("industry")),
                text(role.get("description")),
            ]
        )

    skill_bits = [text(skill.get("name")) for skill in skills]
    career_text = " ".join(career_bits)
    all_text = " ".join(
        [
            text(profile.get("headline")),
            text(profile.get("summary")),
            text(profile.get("current_title")),
            text(profile.get("current_company")),
            text(profile.get("current_industry")),
            career_text,
            " ".join(skill_bits),
        ]
    )

    return CandidateFeatures(
        candidate_id=str(candidate.get("candidate_id", "")),
        current_title=text(profile.get("current_title")),
        location=text(profile.get("location")),
        country=text(profile.get("country")),
        years=safe_float(profile.get("years_of_experience")),
        career_text=career_text,
        all_text=all_text,
        skills=skills,
        signals=signals,
        current_industry=text(profile.get("current_industry")),
        career_industries=industries,
        companies=companies,
        current_company=text(profile.get("current_company")),
        current_company_size=text(profile.get("current_company_size")),
    )


def profile_flags(features: CandidateFeatures) -> dict[str, Any]:
    title_text = features.current_title
    title_hits = count_any(title_text, TECH_TITLES)
    bad_title_hits = count_any(title_text, BAD_TITLES)
    career_ai_hits = count_any(features.career_text, AI_TERMS)
    retrieval_hits = count_any(features.career_text, RETRIEVAL_TERMS)
    eval_hits = count_any(features.career_text, EVAL_TERMS)
    production_hits = count_any(features.career_text, PRODUCTION_TERMS)
    all_ai_hits = count_any(features.all_text, AI_TERMS)
    product_industry_hits = sum(
        1
        for industry in [features.current_industry, *features.career_industries]
        if any(product in industry for product in PRODUCT_INDUSTRIES)
    )
    service_company_hits = sum(
        1 for company in features.companies if any(svc in company for svc in SERVICE_COMPANIES)
    )
    service_industry_hits = sum(1 for industry in features.career_industries if "it services" in industry)
    located_well = has_any(features.location, GOOD_LOCATIONS)
    recent_days = days_since(features.signals.get("last_active_date"))

    return {
        "title_hits": title_hits,
        "bad_title_hits": bad_title_hits,
        "career_ai_hits": career_ai_hits,
        "retrieval_hits": retrieval_hits,
        "eval_hits": eval_hits,
        "production_hits": production_hits,
        "all_ai_hits": all_ai_hits,
        "product_industry_hits": product_industry_hits,
        "service_company_hits": service_company_hits,
        "service_industry_hits": service_industry_hits,
        "located_well": located_well,
        "recent_days": recent_days,
        "skill_ai_count": count_relevant_skills(features.skills),
        "expert_zero_duration_count": count_expert_zero_duration(features.skills),
    }


def count_relevant_skills(skills: list[dict[str, Any]]) -> int:
    count = 0
    for skill in skills:
        name = text(skill.get("name"))
        if any(term in name for term in AI_TERMS | RETRIEVAL_TERMS | EVAL_TERMS | {"python", "pytorch", "tensorflow"}):
            duration = safe_float(skill.get("duration_months"))
            endorsements = safe_float(skill.get("endorsements"))
            if duration >= 12 or endorsements >= 5:
                count += 1
    return count


def count_expert_zero_duration(skills: list[dict[str, Any]]) -> int:
    return sum(
        1
        for skill in skills
        if text(skill.get("proficiency")) == "expert" and safe_float(skill.get("duration_months"), -1) <= 1
    )
