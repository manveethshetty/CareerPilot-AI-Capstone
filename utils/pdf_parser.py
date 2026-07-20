"""
PDF text extraction utility.
Uses pdfplumber for robust text extraction from resume PDFs.
"""
import pdfplumber
import io


def extract_text_from_pdf(file) -> str:
    """
    Extract raw text from an uploaded PDF file (Streamlit UploadedFile or path).
    Returns a single cleaned string with page breaks preserved as newlines.
    """
    text_chunks = []

    # Streamlit's UploadedFile behaves like a file-like object already
    if hasattr(file, "read"):
        file_bytes = file.read()
        pdf_stream = io.BytesIO(file_bytes)
    else:
        pdf_stream = file

    with pdfplumber.open(pdf_stream) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)

    full_text = "\n".join(text_chunks)
    # Basic cleanup: collapse excessive blank lines
    lines = [ln.strip() for ln in full_text.split("\n")]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)


def basic_resume_stats(text: str) -> dict:
    """Cheap heuristic stats used to sanity-check extraction quality."""
    word_count = len(text.split())
    has_email = "@" in text
    has_phone = any(ch.isdigit() for ch in text)
    return {
        "word_count": word_count,
        "has_email": has_email,
        "has_phone_digits": has_phone,
    }
