"""
extractor.py
------------
Phase 1 of the pipeline: read a tender PDF and pull out clean text.

Two paths:
  1. Native text extraction (PyMuPDF) - fast, used when the PDF has a
     real text layer (most digitally-generated tenders).
  2. OCR fallback (Tesseract via pytesseract) - used automatically when
     native extraction returns little/no text, which means the PDF is
     scanned (just page images, e.g. photocopied/signed documents).

OCR requires the Tesseract engine to be installed on your system
separately from the Python packages. If Tesseract isn't installed, OCR
is skipped and a clear error message is returned instead of crashing.
"""

from pathlib import Path
import fitz

MIN_NATIVE_CHARS = 20


def _ocr_page(page, zoom=2.0):
    """Render one PDF page to an image and run Tesseract OCR on it.
    Numeric values inside complex tables can occasionally misread;
    always spot-check financial figures (EMD, Tender Value) against
    the source PDF before relying on them."""
    import pytesseract
    from PIL import Image
    import io

    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img)


def extract_text_from_pdf(pdf_path):
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError("PDF not found: " + str(pdf_path))

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise ValueError("Could not open " + pdf_path.name + " as a PDF: " + str(e))

    pages = [page.get_text("text") for page in doc]
    native_text = "\n\n".join(pages).strip()

    if len(native_text) >= MIN_NATIVE_CHARS:
        doc.close()
        return native_text

    try:
        ocr_pages = []
        for page in doc:
            ocr_pages.append(_ocr_page(page))
        doc.close()
        ocr_text = "\n\n".join(ocr_pages).strip()
        return ocr_text
    except ImportError:
        doc.close()
        raise RuntimeError(
            "This PDF appears to be scanned (no text layer) and OCR "
            "dependencies aren't installed. Run: pip install pytesseract Pillow "
            "and install the Tesseract engine."
        )
    except Exception as e:
        doc.close()
        raise RuntimeError(
            "This PDF appears to be scanned and OCR failed: " + str(e) + ". "
            "Make sure Tesseract OCR is installed on your system."
        )


def extract_text_per_page(pdf_path):
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError("PDF not found: " + str(pdf_path))

    doc = fitz.open(pdf_path)
    pages = [page.get_text("text") for page in doc]
    doc.close()
    return pages