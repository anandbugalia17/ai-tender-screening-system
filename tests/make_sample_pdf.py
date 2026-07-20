"""
Generates synthetic sample tender PDFs in input_tenders/ so the pipeline
can be tested end-to-end without real procurement documents.
Not part of the production pipeline — dev/test utility only.
"""

from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

SAMPLES = [
    {
        "filename": "sample_tender_01.pdf",
        "lines": [
            "MINISTRY OF DEFENCE - PROCUREMENT NOTICE",
            "",
            "Tender ID: MOD/2026/ARTY/0451",
            "EMD: Rs. 5,00,000",
            "Submission Date: 15/08/2026",
            "",
            "Scope of Work: The contractor shall be responsible for the design,",
            "manufacture, testing, and supply of 120mm mortar shell casings",
            "in accordance with QAP-2019 standards. The scope includes factory",
            "acceptance testing, packaging for field transport, and delivery to",
            "three designated depots within Northern Command. Post-delivery",
            "support including a 24-month warranty and spare parts availability",
            "is mandatory for contract award.",
            "",
            "Compliance Requirements: ISO 9001, DGQA certification, MSME registration",
            "preferred but not mandatory.",
            "",
            "Eligibility Criteria: Bidder must have a minimum annual turnover of Rs. 2",
            "crore in the last three financial years and prior experience supplying",
            "ordnance components to defence establishments.",
            "",
            "Documents Required: Company registration certificate, GST certificate,",
            "ISO 9001 certification, last 3 years audited financial statements, and",
            "an authorization letter from the manufacturer.",
        ],
    },
    {
        "filename": "sample_tender_02.pdf",
        "lines": [
            "DEFENCE PROCUREMENT BOARD",
            "",
            "Tender No: DPB-2026-0912",
            "EMD Value: Rs. 12,50,000",
            "Due Date: 02/09/2026",
            "",
            "Scope of Work: Supply, installation, and commissioning of ruggedized",
            "communication relay units for forward operating bases, including",
            "on-site training for signal corps personnel and a 12-month",
            "annual maintenance contract. Vendor must demonstrate prior",
            "experience with similar defence communication infrastructure",
            "projects of comparable scale.",
            "",
            "Eligibility Criteria: Only OEMs or their authorized dealers with at",
            "least 5 years of experience in tactical communication systems may",
            "apply. MSME and Startup India registered entities get relaxed",
            "turnover criteria.",
            "",
            "Documents Required: PAN card, GST registration, OEM authorization",
            "certificate, EMD instrument, and technical compliance statement.",
        ],
    },
]


def make_pdf(filename: str, lines: list[str], out_dir: Path):
    path = out_dir / filename
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    y = height - 50
    c.setFont("Helvetica", 11)
    for line in lines:
        c.drawString(50, y, line)
        y -= 18
    c.save()
    print(f"Created {path}")


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent / "input_tenders"
    out_dir.mkdir(exist_ok=True)
    for sample in SAMPLES:
        make_pdf(sample["filename"], sample["lines"], out_dir)
        