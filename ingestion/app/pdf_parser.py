# PDF parsing: extract text from PDF documents.
#
# pypdf is imported lazily so the HTML-only path does not require it.

def pdf_to_text(path: str) -> str:
    """Extract text from a PDF file.

    Raises RuntimeError if pypdf is not installed, or the underlying error
    from pypdf when the file cannot be read/parsed.
    """
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("pypdf is required to parse PDFs; install ingestion deps") from exc

    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()
