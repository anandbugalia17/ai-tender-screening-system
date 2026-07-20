"""
process_tenders.py
-------------------
Main entry point for the AI-Driven Tender Screening pipeline.

Usage:
    python process_tenders.py
    python process_tenders.py --input /path/to/pdfs --output /path/to/reports

Reads every PDF in the input directory, extracts + parses + enriches it,
and writes a consolidated Excel + Word report to the output directory.
"""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.extractor import extract_text_from_pdf
from src.parser import extract_fields, detect_source_website
from src.enrichment import enrich_tender
from src.report_generator import build_excel, build_docx

load_dotenv()


def process_single_pdf(pdf_path: Path) -> dict:
    """Run one PDF through the full pipeline and return its record dict.
    Never raises — failures are captured in the 'status' field so one bad
    PDF doesn't stop the batch."""
    record = {
        "source_file": pdf_path.name,
        "tender_id": None,
        "organization": None,
        "country": None,
        "tender_title": None,
        "category": None,
        "product_service": None,
        "tender_value": None,
        "emd_value": None,
        "submission_date": None,
        "eligibility_criteria": None,
        "documents_required": None,
        "source_website": None,
        "scope_summary": None,
        "remarks": None,
        "status": "ok",
    }

    try:
        text = extract_text_from_pdf(pdf_path)
    except Exception as e:
        record["status"] = f"extraction_failed: {e}"
        return record

    if not text.strip():
        record["status"] = "no_text_extracted (may be a scanned PDF — OCR not yet supported)"
        return record

    fields = extract_fields(text)
    record["tender_id"] = fields["tender_id"]
    record["emd_value"] = fields["emd_value"]
    record["tender_value"] = fields["tender_value"] or "To be extracted from tender document"
    record["submission_date"] = fields["submission_date"]
    record["eligibility_criteria"] = fields["eligibility_criteria"]
    record["documents_required"] = fields["documents_required"]
    record["source_website"] = detect_source_website(text) or "Not specified"

    try:
        enrichment = enrich_tender(text, fields["scope_of_work_raw"])
        record["organization"] = enrichment["organization"]
        record["country"] = enrichment["country"]
        record["tender_title"] = enrichment["tender_title"]
        record["category"] = enrichment["category"]
        record["product_service"] = enrichment["product_service"]
        record["scope_summary"] = enrichment["scope_summary"]
        record["remarks"] = enrichment["remarks"]
    except Exception as e:
        record["status"] = f"enrichment_failed: {e}"

    if not any([record["tender_id"], record["emd_value"], record["submission_date"]]):
        record["status"] = "no_fields_matched (check regex patterns for this tender format)"

    return record


def run_batch(input_dir: Path, output_dir: Path) -> list[dict]:
    pdf_files = sorted(input_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {input_dir.resolve()}")
        return []

    print(f"Found {len(pdf_files)} tender PDF(s). Processing...\n")

    records = []
    for i, pdf_path in enumerate(pdf_files, start=1):
        print(f"[{i}/{len(pdf_files)}] {pdf_path.name} ... ", end="", flush=True)
        record = process_single_pdf(pdf_path)
        record["s_no"] = i
        print(record["status"])
        records.append(record)

    excel_path = build_excel(records, output_dir / "Tender_Summary_Table.xlsx")
    docx_path = build_docx(records, output_dir / "Tender_Summary_Document.docx")

    print(f"\nDone. Reports written to:\n  {excel_path}\n  {docx_path}")
    return records


def main():
    parser = argparse.ArgumentParser(description="AI-Driven Tender Screening pipeline")
    parser.add_argument("--input", default="input_tenders", help="Directory of input PDFs")
    parser.add_argument("--output", default="output_reports", help="Directory for output reports")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.exists():
        print(f"Input directory not found: {input_dir}")
        sys.exit(1)

    run_batch(input_dir, output_dir)


if __name__ == "__main__":
    main()