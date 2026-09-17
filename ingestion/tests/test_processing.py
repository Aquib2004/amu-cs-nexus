# Unit tests for the ingestion processing pipeline (no network, no DB).
# Sample content only; we do not crawl live AMU sources in tests.

from app import chunker, cleaner, html_parser, metadata, url_discovery

SAMPLE_HTML = """
<html>
<head><title>Exam Schedule</title></head>
<body>
<nav><a href="/notices">Notices</a></nav>
<script>var x = 1;</script>
<p>Mid-semester exams start on <strong>1 October</strong>.</p>
<a href="https://amu.ac.in/pdfs/schedule.pdf">Schedule PDF</a>
</body>
</html>
"""


def test_html_to_text_removes_scripts_and_keeps_text() -> None:
    text = html_parser.html_to_text(SAMPLE_HTML)
    assert "Mid-semester exams" in text
    assert "var x" not in text


def test_extract_title() -> None:
    assert html_parser.extract_title(SAMPLE_HTML) == "Exam Schedule"


def test_clean_text_normalises_whitespace() -> None:
    assert cleaner.clean_text("a   b\n\n\n\n c") == "a b\n\n c"


def test_build_metadata_shape() -> None:
    item = metadata.build_metadata(source_url="https://amu.ac.in/page", title="T")
    assert item["source_url"] == "https://amu.ac.in/page"
    assert item["title"] == "T"
    assert "extracted_at" in item


def test_split_chunks_bounds() -> None:
    text = "word " * 100
    chunks = chunker.split_chunks(text, size=30, overlap=5)
    assert len(chunks) > 1
    assert all(len(c.split()) <= 30 for c in chunks)


def test_url_discovery_returns_absolute_links() -> None:
    urls = url_discovery.discover_links("https://amu.ac.in", SAMPLE_HTML)
    assert "https://amu.ac.in/pdfs/schedule.pdf" in urls
    assert "https://amu.ac.in/notices" in urls
