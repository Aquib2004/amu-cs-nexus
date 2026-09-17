# Tests for the crawler and PDF parser, using injected HTTP transport and
# missing files so no network or real documents are needed.

import pytest
import httpx

from app import pdf_parser
from app.crawler import fetch_html


def test_fetch_html_with_mock_transport() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<html><title>Hello</title></html>")

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    html = fetch_html("https://example.com/page", client=client)
    assert "Hello" in html


def test_fetch_html_raises_on_error_status() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, text="not found")

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    with pytest.raises(httpx.HTTPStatusError):
        fetch_html("https://example.com/missing", client=client)


def test_pdf_parser_missing_file_raises() -> None:
    with pytest.raises(Exception):
        pdf_parser.pdf_to_text("does_not_exist.pdf")
