"""
parser.py
---------
Phase 1/3: pull structured key-value fields out of raw tender text using
regex. Real tenders vary a lot in formatting, so each field has several
fallback patterns, tried in order until one matches.

Fields extracted here (objective/structured - regex is reliable for these):
    - tender_id
    - emd_value
    - tender_value
    - submission_date
    - eligibility_criteria
    - documents_required
    - scope_of_work_raw (passed on to the enrichment step)

Fuzzy fields (organization, country, category, product/service, remarks)
are handled by src/enrichment.py using keyword-based heuristics.
"""

import re

TENDER_ID_PATTERNS = [
    r"Tender\s*(?:ID|No\.?|Number)\s*[:\-]\s*([A-Za-z0-9\/\-_.]+)",
    r"RFP\s*(?:ID|No\.?|Number)\s*[:\-]\s*([A-Za-z0-9\/\-_.]+)",
    r"Bid\s*(?:ID|No\.?|Number)\s*[:\-]\s*([A-Za-z0-9\/\-_.]+)",
    r"Tender\s*Document\s*No\.?\s*[:\-]?\s*(?:No\.?\s*)?([A-Za-z0-9][A-Za-z0-9\/\-_.]{4,})",
]

EMD_PATTERNS = [
    r"EMD(?:\s*\(Earnest Money Deposit\))?\s*[:\-]?\s*(?:Value|Amount)?\s*[:\-]?\s*(?:Rs\.?|INR|₹)\s*([\d,]+(?:\.\d+)?)",
    r"Earnest Money Deposit\s*[:\-]\s*(?:Rs\.?|INR|₹)\s*([\d,]+(?:\.\d+)?)",
]

TENDER_VALUE_PATTERNS = [
    r"(?:Tender|Contract|Estimated|Approximate)\s*Value\s*[:\-]\s*(?:Rs\.?|INR|₹|€|\$|USD|EUR)?\s*([\d,]+(?:\.\d+)?)",
    r"Total\s*(?:Project|Contract)\s*(?:Cost|Value)\s*[:\-]\s*(?:Rs\.?|INR|₹|€|\$|USD|EUR)?\s*([\d,]+(?:\.\d+)?)",
    r"Estimated\s*Cost\s*[:\-]\s*((?:Rs\.?|INR|₹)?\s*[\d,]+(?:\.\d+)?\s*(?:Crore|Lakh|Lac)?)",
]

DATE_PATTERNS = [
    r"(?:Submission|Due|Closing|Last)\s*Date\s*[:\-]\s*([\d]{1,2}[\/\-.][\d]{1,2}[\/\-.][\d]{2,4})",
    r"(?:Submission|Due|Closing|Last)\s*Date\s*[:\-]\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
    r"Bid\s*submission\s*closing\s*date\s*&?\s*time\s*[:\-]?\s*([\d]{1,2}[\/\-.][\d]{1,2}[\/\-.][\d]{2,4})",
]

SCOPE_PATTERNS = [
    r"Scope\s*of\s*Work\s*[:\-]?\s*(.+?)(?=\n[A-Z][A-Za-z ]{2,40}\s*[:\-]|\Z)",
    r"Description\s*of\s*Requirement\s*[:\-]?\s*(.+?)(?=\n[A-Z][A-Za-z ]{2,40}\s*[:\-]|\Z)",
]

ELIGIBILITY_PATTERNS = [
    r"Minimum\s*Eligibility\s*Criteria\s*[:\-]?\s*(.+?)(?=\n\s*\d+\.\s+[A-Z]|\n\s*Annexure|\Z)",
    r"Eligibility\s*Criteria\s*[:\-]?\s*(.+?)(?=\n[A-Z][A-Za-z ]{2,40}\s*[:\-]|\Z)",
    r"Eligibility\s*Requirements\s*[:\-]?\s*(.+?)(?=\n[A-Z][A-Za-z ]{2,40}\s*[:\-]|\Z)",
    r"Bidder\s*Eligibility\s*[:\-]?\s*(.+?)(?=\n[A-Z][A-Za-z ]{2,40}\s*[:\-]|\Z)",
]

DOCUMENTS_PATTERNS = [
    r"List\s*of\s*Documents?\s*to\s*be\s*submitted[^:]*[:\-]\s*(.+?)(?=\n\s*NOTE|\n\s*\d+\.\s+[A-Z][a-z]+\s+[a-z]|\Z)",
    r"Documents?\s*Required\s*[:\-]?\s*(.+?)(?=\n[A-Z][A-Za-z ]{2,40}\s*[:\-]|\Z)",
    r"Required\s*Documents?\s*[:\-]?\s*(.+?)(?=\n[A-Z][A-Za-z ]{2,40}\s*[:\-]|\Z)",
    r"List\s*of\s*Documents?\s*[:\-]?\s*(.+?)(?=\n[A-Z][A-Za-z ]{2,40}\s*[:\-]|\Z)",
]


def _first_match(patterns, text):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
    return None


KNOWN_PORTALS = {
    "GeM": r"\bGeM\b|Government\s*e-?Marketplace",
    "CPPP": r"\bCPPP\b|Central\s*Public\s*Procurement\s*Portal",
    "NATO Procurement Portal": r"\bNATO\b.{0,40}(?:Procurement|Acquisition)",
    "DRDO Portal": r"\bDRDO\b",
    "IREPS": r"\bIREPS\b",
}


def detect_source_website(text):
    for portal_name, pattern in KNOWN_PORTALS.items():
        if re.search(pattern, text, re.IGNORECASE):
            return portal_name
    return None


def extract_fields(text):
    scope_raw = _first_match(SCOPE_PATTERNS, text)
    if scope_raw:
        scope_raw = re.sub(r"\s+", " ", scope_raw).strip()
        scope_raw = scope_raw[:3000]

    eligibility = _first_match(ELIGIBILITY_PATTERNS, text)
    if eligibility:
        eligibility = re.sub(r"\s+", " ", eligibility).strip()[:1000]

    documents = _first_match(DOCUMENTS_PATTERNS, text)
    if documents:
        documents = re.sub(r"\s+", " ", documents).strip()[:1000]

    return {
        "tender_id": _first_match(TENDER_ID_PATTERNS, text),
        "emd_value": _first_match(EMD_PATTERNS, text),
        "tender_value": _first_match(TENDER_VALUE_PATTERNS, text),
        "submission_date": _first_match(DATE_PATTERNS, text),
        "scope_of_work_raw": scope_raw,
        "eligibility_criteria": eligibility,
        "documents_required": documents,
    }