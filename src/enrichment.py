"""
enrichment.py
--------------
Phase 3 (rule-based, no paid API / no LLM calls):
fills in the "fuzzy" fields using keyword matching and simple heuristics
instead of an AI model. This keeps the whole pipeline free to run.
"""

import os
import re

DEFAULT_COMPANY_PROFILE = (
    "Bandiz Technoz - a data privacy service provider in India, "
    "specializing in data privacy, data protection, and information "
    "security compliance services."
)

ORG_PATTERNS = [
    r"((?:Ministry|Department)\s+of\s+[A-Za-z &,]+)",
    r"([A-Za-z]+(?:\s+[A-Za-z]+){0,3}\s+(?:Board|Corporation|Authority|Command|Directorate))",
]

# Ordered most-specific-first. Single ambiguous words (e.g. "mortar" also
# means a construction material, not just a weapon) are avoided in favor
# of specific multi-word phrases, to prevent false category matches.
CATEGORY_KEYWORDS = [
    (["mortar shell", "artillery shell", "supply of ammunition", "small arms ammunition", "ordnance factory"], "Defence Hardware", "Ammunition/Ordnance Supply"),
    (["health unit", "primary health", "hospital building", "medical facility"], "Healthcare Infrastructure", "Healthcare Facility Construction"),
    (["operation and maintenance", "facility management", "housekeeping", "amc of", "camc of"], "Facility Management", "O&M / AMC Services"),
    (["security service", "security guard", "24x7 security"], "Security Services", "Manned Security Services"),
    (["communication", "relay", "signal", "radio"], "Communication Systems", "Comms Equipment & Installation"),
    (["cyber", "data privacy", "data protection", "information security", "encryption"], "IT / Cybersecurity", "Data Security Services"),
    (["software", "application development", "it system", "database"], "Information Technology", "Software Development/Services"),
    (["vehicle", "transport", "logistics"], "Logistics & Transport", "Vehicle/Transport Supply"),
    (["construction", "civil work", "building work"], "Civil Works", "Construction/Infrastructure"),
    (["training", "personnel"], "Training & Services", "Training Services"),
]

COUNTRY_HINTS = [
    (["india", "rs.", "inr", "₹", "mod", "drdo", "gem", "cppp"], "India"),
    (["nato"], "NATO Member States"),
    (["usd", "$", "united states"], "United States"),
    (["eur", "€"], "European Union"),
]


def _guess_organization(text):
    for pattern in ORG_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip().rstrip(",.")
    for line in text.splitlines():
        line = line.strip()
        if line and len(line) < 80 and line.isupper():
            return line.title()
    return "Not specified"


def _guess_country(text):
    lowered = text.lower()
    for keywords, country in COUNTRY_HINTS:
        if any(k in lowered for k in keywords):
            return country
    return "Not specified"


def _guess_title(text):
    match = re.search(r"(?:Tender|NIT|Notice Inviting Tender)\s+for\s+(.{10,150}?)(?:\n\n|\n[A-Z]{4,}|\Z)", text, re.IGNORECASE | re.DOTALL)
    if match:
        return re.sub(r"\s+", " ", match.group(1)).strip()

    for line in text.splitlines():
        line = line.strip()
        if line and 5 < len(line) < 100:
            return line.title() if line.isupper() else line
    return "Not specified"


def _guess_category(text):
    lowered = text.lower()
    for keywords, category, product in CATEGORY_KEYWORDS:
        if any(k in lowered for k in keywords):
            return category, product
    return "Not specified", "Not specified"


def _fallback_summary(text, max_sentences=3):
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    summary = " ".join(sentences[:max_sentences])
    return summary or "No scope of work text could be extracted from this document."


def _relevance_remarks(text, company_profile):
    profile_keywords = re.findall(r"[a-zA-Z]{4,}", company_profile.lower())
    stopwords = {"with", "that", "this", "from", "your", "company", "provider", "india", "service", "services"}
    profile_keywords = [w for w in set(profile_keywords) if w not in stopwords]

    lowered = text.lower()
    matched = [kw for kw in profile_keywords if kw in lowered]

    if matched:
        return "Possible relevance - tender text mentions: " + ", ".join(matched[:5]) + ". Manual review recommended."
    return "No obvious keyword overlap with your company profile found. Likely low relevance - manual review recommended if unsure."


def enrich_tender(full_text, scope_of_work_raw, company_profile=None):
    company_profile = company_profile or os.environ.get("COMPANY_PROFILE", DEFAULT_COMPANY_PROFILE)

    category, product_service = _guess_category(full_text)

    return {
        "organization": _guess_organization(full_text),
        "country": _guess_country(full_text),
        "tender_title": _guess_title(full_text),
        "category": category,
        "product_service": product_service,
        "scope_summary": (
            _fallback_summary(scope_of_work_raw)
            if scope_of_work_raw
            else "Scope of work not found in document - manual review recommended."
        ),
        "remarks": _relevance_remarks(full_text, company_profile),
    }