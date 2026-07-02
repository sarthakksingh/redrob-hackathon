"""Create the PDF deck submitted to Hack2Skill."""

from __future__ import annotations

import argparse
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


PAGE = landscape((13.333 * inch, 7.5 * inch))
BLUE = colors.HexColor("#2563EB")
NAVY = colors.HexColor("#0F172A")
MUTED = colors.HexColor("#475569")
LIGHT = colors.HexColor("#EFF6FF")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="deliverables/redrob_ai_recruiter_approach.pdf")
    args = parser.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out), pagesize=PAGE)

    slide(c, "AI Recruiter Ranker", "A CPU-only, explainable system for ranking Senior AI Engineer candidates", [
        "Ranks 100,000 profiles into a trusted top-100 shortlist.",
        "Optimized for the Redrob founding Senior AI Engineer JD.",
        "No hosted APIs, no GPU, no hidden manual edits during ranking.",
    ])
    slide(c, "What the JD really asks for", "The model ranks for evidence, not keyword density", [
        "Strongest signal: shipped search, retrieval, recommendation, ranking, NLP or ML systems.",
        "Must be a hands-on product engineer, not a pure researcher or demo-only framework user.",
        "5-9 years is ideal, with Pune/Noida or nearby Indian hubs preferred.",
        "Availability matters: recent activity, recruiter response, short notice and open-to-work improve trust.",
    ])
    slide(c, "Ranking architecture", "Streaming feature extraction plus deterministic hybrid scoring", [
        "1. Stream candidates.jsonl so memory stays small.",
        "2. Build structured features from profile, career history, skills and Redrob behavioral signals.",
        "3. Score five components: career fit, retrieval/eval, production/product context, logistics, engagement.",
        "4. Apply penalties for nontechnical profiles, service-only histories, inactive candidates and honeypot-like inconsistencies.",
        "5. Emit ranked CSV/XLSX with specific reasoning for every shortlisted candidate.",
    ])
    slide(c, "Why this works against traps", "Career-history evidence beats skill stuffing", [
        "Skills are only supporting evidence; role titles and descriptions carry more weight.",
        "HR, marketing, content and design profiles are penalized unless career text proves real ML/search work.",
        "Expert skills with near-zero duration and keyword-heavy profiles with weak career evidence are down-ranked.",
        "Service-only histories are discounted unless the candidate has strong retrieval/ranking or product evidence.",
    ])
    slide(c, "Score design", "Weighted to mimic how a strong recruiter would shortlist", [
        "45% career evidence and role-title fit.",
        "20% retrieval, search, recommendation and evaluation evidence.",
        "15% production and product-company context.",
        "10% experience, location, relocation and notice-period logistics.",
        "10% engagement and availability signals, minus explicit risk penalties.",
    ])
    slide(c, "Reproducibility", "Simple command, fast offline runtime", [
        "Command: python scripts/rank_candidates.py --candidates candidates.jsonl --out deliverables/submission.csv --xlsx deliverables/submission.xlsx",
        "Implementation uses the Python standard library for ranking and XLSX export.",
        "The same code creates the submitted top-100; no candidate data is sent to any LLM/API.",
        "Local validation checks row count, rank order, candidate existence, monotonic scores and reasoning.",
    ])
    slide(c, "Deliverables", "What is included", [
        "GitHub repo: clean source, README, build plan, validation script and metadata template filled.",
        "Ranked output: CSV for the official spec and XLSX for the portal upload field.",
        "Deck PDF: this approach summary.",
        "Demo path: Streamlit-ready app skeleton can rank uploaded small samples using the same scorer.",
    ])
    c.save()
    print(out)


def slide(c: canvas.Canvas, title: str, subtitle: str, bullets: list[str]) -> None:
    width, height = PAGE
    c.setFillColor(colors.white)
    c.rect(0, 0, width, height, stroke=0, fill=1)
    c.setFillColor(LIGHT)
    c.rect(0, height - 0.55 * inch, width, 0.55 * inch, stroke=0, fill=1)
    c.setFillColor(BLUE)
    c.rect(0, 0, 0.16 * inch, height, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 34)
    c.drawString(0.75 * inch, height - 1.35 * inch, title)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 18)
    c.drawString(0.78 * inch, height - 1.78 * inch, subtitle)
    y = height - 2.55 * inch
    for bullet in bullets:
        c.setFillColor(BLUE)
        c.circle(0.95 * inch, y + 0.07 * inch, 0.055 * inch, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica", 17)
        lines = wrap(bullet, 96)
        for line in lines:
            c.drawString(1.15 * inch, y, line)
            y -= 0.31 * inch
        y -= 0.18 * inch
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 0.5 * inch, 0.35 * inch, "Redrob AI Recruiter Ranking System")
    c.showPage()


def wrap(text: str, limit: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        if sum(len(w) + 1 for w in current) + len(word) > limit and current:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines


if __name__ == "__main__":
    main()
