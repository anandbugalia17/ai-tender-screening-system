# AI-Driven Tender Screening & Automated Reporting System

An AI-powered pipeline that automates the extraction, summarization, and reporting of key information from defence procurement tender PDFs — turning raw, unstructured documents into structured, actionable business reports.

## Problem Statement

Reviewing large volumes of tender documents manually to extract critical details (Tender ID, EMD value, submission deadlines, scope of work) is slow, repetitive, and error-prone. This project automates that process end-to-end, producing ready-to-use Excel datasets and Word summary reports.

## Current Implementation

The system currently supports the following pipeline:

1. **Text Extraction** — Reads tender PDFs and extracts raw text using `PyMuPDF`.
2. **Key Field Extraction** — Uses regex pattern matching to identify structured fields like:
   - Tender ID
   - EMD (Earnest Money Deposit) value
   - Submission / due date
3. **AI Summarization** — Sends the extracted "Scope of Work" section to an LLM API to generate a concise 2–3 sentence summary of project requirements.
4. **Data Structuring** — Consolidates extracted fields into a structured format using `pandas`.
5. **Automated Reporting** — Generates two outputs per batch:
   - `Tender_Summary_Table.xlsx` — structured dataset for tracking and database integration.
   - `Tender_Summary_Document.docx` — formatted Word report with bulleted summaries, generated via `python-docx`.

### Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.9+ |
| PDF Text Extraction | PyMuPDF (fitz) |
| Field Extraction | Regex |
| Summarization | LLM API (Claude / GPT) |
| Data Processing | pandas |
| Report Generation | python-docx |

##  Workflow

```
Input: Raw tender PDFs placed in /input_tenders/
   ↓
Run: python process_tenders.py
   ↓
Processing: Text extraction → Regex field parsing → LLM summarization → Data consolidation
   ↓
Output: /output_reports/ containing Excel + Word summary reports
```

## Roadmap / Planned Enhancements

These are architectural extensions planned for future iterations, scoped out of the current MVP to prioritize a working, reliable pipeline first:

- **Computer Vision Layout Analysis** — Integrate YOLOv8 for detecting tables, headers, and complex multi-column layouts in scanned or non-standard tender formats.
- **Automated Table Extraction** — Use OpenCV + Camelot to crop and extract tabular pricing/milestone data directly from detected table regions.
- **OCR Support** — Handle scanned/image-based PDFs where no text layer is available.
- **Local NLP Summarization** — Explore lightweight local models (e.g., HuggingFace BART) as an offline alternative to the LLM API for summarization.
- **Batch Dashboard** — Simple web UI for uploading tenders and viewing processed results in real time.

## Why This Approach

The current version deliberately prioritizes a complete, working pipeline over a more complex but unproven architecture. Every component listed under "Current Implementation" is functional end-to-end; the CV/table-extraction layer is documented as a clear next phase rather than claimed as built.

## Setup

```bash
git clone https://github.com/anandbugalia17/ai-tender-screening-system.git
cd ai-tender-screening-system
pip install -r requirements.txt
```

## Usage

```bash
python process_tenders.py
```

Place your tender PDFs in `/input_tenders/` before running. Outputs will be generated in `/output_reports/`.

## Author
ANAND<br>
IIT KANPUR
---
