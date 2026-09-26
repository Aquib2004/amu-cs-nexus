"""Ingest verified examination resources from official AMU CoE pages.

The parser stores only named links found on official Controller of Examinations
pages. It never invents an exam date, schedule, result, or question paper.
"""

import hashlib
import logging
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import httpx

from app.core.database import SessionLocal
from app.models.document import Chunk, Document
from app.models.exam_resource import ExamResource

logger = logging.getLogger(__name__)
COE = "https://www.amucontrollerexams.com"
SOURCE_PAGES = (
    f"{COE}/page/view/examinations-1550635504",
    f"{COE}/page/view/student-services-1772225714",
)
FIXED_RESOURCES = (
    ("Controller of Examinations", "Official examination notices and portal updates.", f"{COE}/"),
    ("Examinations", "Official examination information entry point.", SOURCE_PAGES[0]),
    ("Student Services", "Official transcripts, marksheets, migration, degree and re-evaluation services.", SOURCE_PAGES[1]),
    ("Examination Results", "Official public result and grade lookup portal.", "https://results.amucontrollerexams.com/"),
)
KEYWORDS = re.compile(
    r"exam|result|admit|form|transcript|marksheet|marks|degree|diploma|"
    r"certificate|migration|re-evaluation|ordinance|regulation|unfair|roll list",
    re.I,
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href is not None:
            title = re.sub(r"\s+", " ", " ".join(self._text)).strip()
            if title:
                self.links.append((title, self._href))
            self._href = None
            self._text = []


def discover(client: httpx.Client) -> list[dict]:
    resources: dict[str, dict] = {}
    for title, description, url in FIXED_RESOURCES:
        resources[url] = {"title": title, "description": description, "url": url, "source_url": url}
    for source_url in SOURCE_PAGES:
        response = client.get(source_url)
        response.raise_for_status()
        parser = LinkParser()
        parser.feed(response.text)
        for title, href in parser.links:
            if not KEYWORDS.search(title):
                continue
            url = urljoin(source_url, href)
            parsed = urlparse(url)
            allowed = parsed.hostname and (
                parsed.hostname.endswith("amucontrollerexams.com") or parsed.hostname == "amu.ac.in"
            )
            if parsed.scheme in ("http", "https") and allowed:
                resources.setdefault(url, {
                    "title": title[:500], "description": f"Official resource linked from {source_url}.",
                    "url": url[:1000], "source_url": source_url,
                })
    return list(resources.values())


def _embedder():
    try:
        from ai.providers.gemini_embed import GeminiEmbedder
        from app.core.config import settings

        key = settings.embedding_api_key or settings.gemini_api_key or settings.llm_api_key
        return GeminiEmbedder(api_key=key) if key else None
    except Exception:
        logger.warning("Exam resources will be stored without new embeddings", exc_info=True)
        return None


def run(embedding: bool = True) -> int:
    session = SessionLocal()
    embedder = _embedder() if embedding else None
    written = 0
    try:
        with httpx.Client(timeout=30, follow_redirects=True, verify=False,
                           headers={"User-Agent": "AMUCS-Nexus exam resource sync"}) as client:
            resources = discover(client)
        texts = [f"{item['title']}. {item['description']}" for item in resources]
        vectors = embedder.embed_many(texts) if embedder else []
        for index, item in enumerate(resources):
            row = session.query(ExamResource).filter_by(url=item["url"]).first()
            digest = hashlib.sha256(f"{item['title']}|{item['description']}".encode()).hexdigest()
            if row is None:
                session.add(ExamResource(**item, content_hash=digest,
                                         crawl_timestamp=datetime.now(timezone.utc)))
                written += 1
            else:
                for key, value in item.items():
                    setattr(row, key, value)
                row.content_hash = digest
                row.crawl_timestamp = datetime.now(timezone.utc)
            doc = session.query(Document).filter_by(source_url=item["url"]).first()
            if doc is None:
                doc = Document(
                    title=item["title"][:500], source_url=item["url"], source_type="web",
                    document_type="exam", department="computer-science", content_hash=digest,
                    crawl_timestamp=datetime.now(timezone.utc),
                )
                session.add(doc)
            doc.title = item["title"][:500]
            doc.content_hash = digest
            doc.chunks.clear()
            doc.chunks.append(Chunk(
                chunk_index=0,
                text=f"Official examination resource: {item['title']}. {item['description']}",
                embedding=vectors[index] if index < len(vectors) else None,
            ))
        session.commit()
    except Exception:
        session.rollback()
        logger.exception("Exam resource ingestion failed")
    finally:
        session.close()
    return written


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run(embedding=True)
