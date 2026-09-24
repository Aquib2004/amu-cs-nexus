# ingestion/app/amu_ingest.py - ingest real data from the official AMU
# department API (api.amu.ac.in) into the AMUCS Nexus database.
#
# Design:
#   - Client reads from the public AMU API (free, no key required).
#   - Parsers turn JSON into plain records.
#   - Writer upserts idempotently (keyed by source URL / AMU id) so the script
#     can be re-run without duplicating rows.
#   - When a Gemini key is configured, real embeddings are computed for every
#     new chunk (semantic search). Without a key, chunks stay embeddable later.
#   - Every crawl is recorded in ingestion_log for auditability.

import hashlib
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]  # amu-cs-nexus/
BACKEND = ROOT / "backend"
for _p in (str(ROOT), str(BACKEND)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sqlalchemy.orm import Session  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402
from app.models.document import Chunk, Document  # noqa: E402
from app.models.faculty import Faculty  # noqa: E402
from app.models.ingestion_log import IngestionLog  # noqa: E402
from app.models.laboratory import Laboratory  # noqa: E402
from app.models.notice import Notice  # noqa: E402
from app.models.program import Program  # noqa: E402
from app.models.research_project import ResearchProject  # noqa: E402
from app.models.staff import StaffMember  # noqa: E402

logger = logging.getLogger("amu_ingest")

API = "https://api.amu.ac.in/api/v1"
SITE = "https://www.amu.ac.in"
CS_SLUG = "computer-science"
PAGE_URL = f"{SITE}/department/{CS_SLUG}"


# --------------------------------------------------------------------------- #
# Client
# --------------------------------------------------------------------------- #

class AmuClient:
    """Thin reader over the public AMU JSON API."""

    def __init__(self, timeout: float = 30.0) -> None:
        self._client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            verify=False,
            headers={"User-Agent": "Mozilla/5.0 (amu-cs-nexus ingest)"},
        )

    def get(self, path: str) -> dict | None:
        url = f"{API}/{path}"
        try:
            response = self._client.get(url)
        except httpx.RequestError as exc:
            logger.warning("request failed %s: %s", url, exc)
            return None
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    def list_page(self, page: str, page_no: int = 1) -> list[dict] | None:
        data = self.get(
            f"department-list-data?lang=en&slug=department/{CS_SLUG}/{page}"
            f"&page={page_no}"
        )
        if data is None:
            return None
        return _find_rows(data)

    def close(self) -> None:
        self._client.close()


def _find_rows(payload) -> list[dict] | None:
    """Locate the actual row list inside AMU's inconsistent response shapes.

    Some endpoints return rows at data.data (faculty, staff, programmes) while
    others nest a pagination wrapper first: data.data.data (notices, labs).
    Following the 'data' key until we hit a list handles both.
    """
    current = payload
    for _ in range(6):
        if isinstance(current, dict) and "data" in current:
            current = current["data"]
            continue
        break
    if isinstance(current, list):
        return current
    return None


def _strip_html(raw: str | None) -> str:
    if not raw:
        return ""
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw or "", flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _text_short(text: str, limit: int = 220) -> str:
    clean = _strip_html(text)
    return clean[:limit].rsplit(" ", 1)[0] if len(clean) > limit else clean
def parse_faculty(row: dict) -> dict:
    title = row.get("title") or ""
    first, mid, last = row.get("first_name"), row.get("middle_name"), row.get("last_name")
    name = " ".join(p for p in [title, first, mid, last] if p).strip()
    rel = row.get("url") or ""
    profile = f"{SITE}/{rel}" if str(rel).startswith("faculty/") else None
    image = row.get("image")
    if image and str(image).startswith("/"):
        image = f"https://api.amu.ac.in{image}"
    return {
        "name": name or f"{first or ''} {last or ''}".strip(),
        "designation": row.get("designation") or None,
        "department": CS_SLUG,
        "email": row.get("email") or None,
        "phone": row.get("telephone_no") or None,
        "specializations": [],
        "research_areas": [],
        "profile_url": profile,
        "image_url": image,
        "source_url": f"{PAGE_URL}/faculty-members",
    }


def parse_staff(row: dict) -> dict:
    title, first, mid, last = (
        row.get("title") or "", row.get("first_name"), row.get("middle_name"), row.get("last_name")
    )
    name = " ".join(p for p in [title, first, mid, last] if p).strip()
    while "  " in name:
        name = name.replace("  ", " ")
    image = row.get("image")
    if image and str(image).startswith("/"):
        image = f"https://api.amu.ac.in{image}"
    return {
        "name": name or f"{first or ''} {last or ''}".strip(),
        "designation": row.get("designation") or None,
        "email": row.get("email") or None,
        "phone": row.get("telephone_no") or None,
        "image_url": image,
        "profile_url": None,
        "source_url": f"{PAGE_URL}/non-teaching-staff",
    }


def parse_notice(row: dict) -> dict:
    file_path = row.get("file") or ""
    url = f"{API}{file_path}" if str(file_path).startswith("/") else (file_path or PAGE_URL)
    created = row.get("created_at")
    published = None
    if isinstance(created, str) and "T" in created:
        published = datetime.fromisoformat(created.replace("Z", "+00:00"))
    title = (row.get("title") or "").strip()
    lower = title.lower()
    category = None
    if any(k in lower for k in ("teacher", "professor", "instructor", "recruitment",
                                "advertisement", "screening", "eligible")):
        category = "recruitment"
    elif any(k in lower for k in ("ph.d", "phd", "fellowship", "research")):
        category = "research"
    elif any(k in lower for k in ("examination", "exam", "interview")):
        category = "examinations"
    elif any(k in lower for k in ("sports", "festival")):
        category = "events"
    return {
        "title": title,
        "url": url,
        "category": category,
        "body": None,
        "published_at": published,
        "pdf_url": url,
    }


def parse_program(row: dict, level: str) -> dict:
    syll = row.get("syll") or row.get("syllabus") or ""
    currl = row.get("currl") or ""
    return {
        "name": (row.get("name") or "").strip(),
        "level": level,
        "intake_seats": (row.get("nos") or None),
        "duration": _strip_html(row.get("dr")) or None,
        "eligibility": _strip_html(row.get("spec")) or None,
        "curriculum_url": (currl if str(currl).startswith("http") else None),
        "syllabus_url": (syll if str(syll).startswith("http") else None),
        "details": _strip_html(" ".join(filter(None, [row.get("cr"), row.get("acrr"),
                                                      row.get("jp"), row.get("spec"),
                                                      row.get("peo"), row.get("po")])))[:4000] or None,
        "source_url": f"{PAGE_URL}/{level}",
    }


def parse_lab(row: dict) -> dict:
    file_path = row.get("file") or ""
    file_url = f"{API}{file_path}" if str(file_path).startswith("/") else (file_path or None)
    return {
        "name": (row.get("link") or "").strip(),
        "description": _strip_html(row.get("link_description"))[:4000] or None,
        "file": file_url,
        "source_url": f"{PAGE_URL}/important-laboratories",
    }


def parse_research(row: dict, status: str) -> dict:
    description = _strip_html(row.get("about")) or ""
    title = description[:140].rsplit(" ", 1)[0] if len(description) > 140 else description
    m = re.search(r"<strong[^>]*>(.*?)</strong>", row.get("about") or "", re.S)
    if m and _strip_html(m.group(1)):
        title = _strip_html(m.group(1))[:200]
    return {
        "title": title or "(Untitled project)",
        "status": status,
        "funding_agency": _strip_html(row.get("fagency")) or None,
        "amount": _strip_html(row.get("famount")) or None,
        "principal_investigator": _strip_html(row.get("pi")) or None,
        "co_investigators": _strip_html(row.get("cpi")) or None,
        "description": description[:6000] or None,
        "source_url": f"{PAGE_URL}/completed-research-projects" if status == "completed"
        else f"{PAGE_URL}/on-going-research-projects",
    }


def parse_about(data: dict | None) -> dict | None:
    if not data:
        return None
    about = data.get("data", {}).get("about")
    if not about:
        return None
    description = _strip_html(about.get("link_description")) or ""
    if not description:
        return None
    return {
        "title": "About the Department of Computer Science",
        "text": description,
        "source_url": f"{SITE}/department/{CS_SLUG}",
        "document_type": "web_page",
    }
# --------------------------------------------------------------------------- #
# Writer helpers (idempotent upserts)
# --------------------------------------------------------------------------- #

def _find(session: Session, model, **kwargs):
    return session.query(model).filter_by(**kwargs).first()


def _chunk_text(text: str, size: int = 900) -> list[str]:
    """Split text into <=size-character sentence-ish pieces."""
    pieces = []
    if text.strip():
        parts = re.split(r"(?<=[.!?])\s+|\n{2,}", text)
        current = ""
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if len(current) + len(part) + 1 <= size:
                current = f"{current} {part}".strip()
            else:
                if current:
                    pieces.append(current)
                current = part
        if current:
            pieces.append(current)
    if not pieces:
        pieces = [text.strip()]
    return pieces


def write_documents(session: Session, embed_many: callable, docs: list[dict]) -> tuple[int, int]:
    """Upsert documents by source_url; re-chunk + embed only when text changed."""
    found = written = 0
    for item in docs:
        found += 1
        existing = _find(session, Document, source_url=item["source_url"])
        text: str = item.get("text") or item.get("details") or ""
        new_hash = _sha(text)
        if existing is not None and existing.content_hash == new_hash:
            continue
        if existing is None:
            doc = Document(
                title=item["title"][:500],
                source_url=item["source_url"],
                source_type="web",
                document_type=item.get("document_type", "web_page"),
                department=item.get("department", CS_SLUG),
                content_hash=new_hash,
                crawl_timestamp=datetime.now(timezone.utc),
            )
        else:
            doc = existing
            doc.title = item["title"][:500]
            doc.content_hash = new_hash
            doc.crawl_timestamp = datetime.now(timezone.utc)
            doc.chunks.clear()
        pieces = _chunk_text(text)
        embedding = None
        if embed_many is not None:
            try:
                embedding = embed_many(pieces)
            except Exception as exc:  # provider outage must not kill ingestion
                logger.warning("embedding failed, storing raw chunks: %s", exc)
        for idx, piece in enumerate(pieces):
            chunk = Chunk(chunk_index=idx, text=piece)
            if embedding is not None and idx < len(embedding):
                chunk.embedding = embedding[idx]
            doc.chunks.append(chunk)
        session.add(doc)
        written += 1
    return found, written


def write_faculty(session: Session, rows) -> tuple[int, int]:
    found = written = 0
    for r in rows or []:
        item = parse_faculty(r)
        if not item["name"]:
            continue
        found += 1
        existing = _find(session, Faculty, name=item["name"])
        if existing is None:
            session.add(Faculty(**item))
            written += 1
        else:
            for key, value in item.items():
                setattr(existing, key, value)
    return found, written


def write_staff(session: Session, rows) -> tuple[int, int]:
    found = written = 0
    for r in rows or []:
        item = parse_staff(r)
        if not item["name"]:
            continue
        found += 1
        existing = _find(session, StaffMember, name=item["name"])
        if existing is None:
            session.add(StaffMember(**item))
            written += 1
        else:
            for key, value in item.items():
                setattr(existing, key, value)
    return found, written
def write_notices(session: Session, rows) -> tuple[int, int]:
    found = written = 0
    for r in rows or []:
        item = parse_notice(r)
        if not item["title"]:
            continue
        found += 1
        if _find(session, Notice, title=item["title"], url=item["url"]):
            continue
        session.add(Notice(
            title=item["title"][:500],
            url=item["url"][:1000],
            category=item["category"],
            body=item["body"],
            published_at=item["published_at"],
        ))
        written += 1
    return found, written


def write_programs(session: Session, rows, level: str) -> tuple[int, int]:
    found = written = 0
    for r in rows or []:
        item = parse_program(r, level)
        if not item["name"]:
            continue
        found += 1
        existing = _find(session, Program, name=item["name"])
        if existing is None:
            session.add(Program(**item))
            written += 1
        else:
            for key, value in item.items():
                setattr(existing, key, value)
    return found, written


def write_labs(session: Session, rows) -> tuple[int, int]:
    found = written = 0
    for r in rows or []:
        item = parse_lab(r)
        if not item["name"]:
            continue
        found += 1
        existing = _find(session, Laboratory, name=item["name"])
        if existing is None:
            session.add(Laboratory(**item))
            written += 1
        else:
            for key, value in item.items():
                setattr(existing, key, value)
    return found, written


def write_research(session: Session, rows, status: str) -> tuple[int, int]:
    found = written = 0
    for r in rows or []:
        item = parse_research(r, status)
        if not item["title"]:
            continue
        found += 1
        existing = _find(session, ResearchProject, title=item["title"])
        if existing is None:
            session.add(ResearchProject(**item))
            written += 1
        else:
            for key, value in item.items():
                setattr(existing, key, value)
    return found, written


def log_run(session: Session, source: str, found: int, written: int,
            status: str = "ok", detail: str = "") -> None:
    session.add(IngestionLog(source=source, rows_found=found, rows_written=written,
                             status=status, detail=detail[:2000] or None))
    session.flush()
# --------------------------------------------------------------------------- #
# Orchestrator
# --------------------------------------------------------------------------- #

class _BatchedEmbedder:
    """Lazy batch embedder; created only when a Gemini key is configured."""

    def __init__(self) -> None:
        self._embedder = None

    def _lazy(self):
        if self._embedder is None:
            from ai.providers import ProviderError
            from ai.providers.gemini_embed import GeminiEmbedder
            from app.core.config import settings

            key = settings.llm_api_key or settings.gemini_api_key
            if not key:
                raise ProviderError("no key")
            self._embedder = GeminiEmbedder(api_key=key)
        return self._embedder

    def invoke(self, texts: list[str]) -> list[list[float]]:
        emb = self._lazy()
        batch = 64
        vectors: list[list[float]] = []
        for i in range(0, len(texts), batch):
            vectors.extend(emb.embed_many(texts[i:i + batch]))
        return vectors


def run_ingestion(embedding: bool = True) -> int:
    """Fetch real AMU data and upsert it into the database.

    Real content is written BOTH to dedicated directory tables (faculties,
    programs, laboratories, research_projects, notices) AND to the searchable
    documents/chunks corpus so search + chat are grounded in real data too.

    Returns the total number of rows written.
    """
    client = AmuClient()
    session: Session = SessionLocal()
    total_written = 0
    embed_fn = (_BatchedEmbedder().invoke if embedding else None)
    doc_items: list[dict] = []

    def slugify(text: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:60]

    def counts(source, found, written, status="ok", detail=""):
        nonlocal total_written
        total_written += written
        log_run(session, source, found, written, status, detail)
        logger.info("%s: found=%d written=%d %s", source, found, written, status)

    try:
        # --- department detail (about text) ---
        detail = client.get(f"department-detail?lang=en&slug={CS_SLUG}")
        about = parse_about(detail)
        if about:
            doc_items.append(about)
            counts("department-detail/about", 1, 0)  # written with corpus below

        # --- faculty ---
        rows = client.list_page("faculty-members")
        f, w = write_faculty(session, rows or [])
        counts("faculty-members", f, w)
        session.flush()

        # --- non-teaching staff ---
        rows = client.list_page("non-teaching-staff")
        f, w = write_staff(session, rows or [])
        counts("non-teaching-staff", f, w)
        session.flush()

        # --- notices (paginated, hard cap 12 pages) ---
        found = written = 0
        page = 1
        while page <= 12:
            rows = client.list_page("notice-and-circular", page_no=page)
            if not rows:
                break
            f, w = write_notices(session, rows)
            found += f
            written += w
            for r in rows:
                item = parse_notice(r)
                if item["title"]:
                    doc_items.append({
                        "title": item["title"],
                        "text": item["title"],
                        "source_url": item["pdf_url"],
                        "document_type": "notice",
                    })
            if len(rows) < 10:
                break
            page += 1
        session.flush()
        counts("notice-and-circular", found, written)

        # --- programs ---
        for level, pagepath in [("ug", "under-graduate"), ("pg", "post-graduate"), ("phd", "phd")]:
            rows = client.list_page(pagepath)
            if not rows:
                logger.info("programs/%s: no data (endpoint returned nothing)", pagepath)
                continue
            f, w = write_programs(session, rows, level)
            counts(f"programs/{pagepath}", f, w)
            for r in rows:
                item = parse_program(r, level)
                if not item["name"]:
                    continue
                doc_items.append({
                    "title": f"{item['name']} ({level.upper()})",
                    "text": " ".join(filter(None, [
                        f"Programme: {item['name']}",
                        f"Level: {level.upper()}",
                        f"Intake: {item['intake_seats']}" if item["intake_seats"] else "",
                        item["duration"],
                        item["eligibility"],
                        item["details"],
                    ])),
                    "source_url": f"{PAGE_URL}/{pagepath}#{slugify(item['name'])}",
                    "document_type": "program",
                })
            session.flush()

        # --- laboratories ---
        rows = client.list_page("important-laboratories")
        if rows:
            f, w = write_labs(session, rows)
            counts("important-laboratories", f, w)
            for r in rows:
                item = parse_lab(r)
                if item["name"]:
                    doc_items.append({
                        "title": item["name"],
                        "text": " ".join(filter(None, [f"Laboratory: {item['name']}", item["description"]])),
                        "source_url": f"{PAGE_URL}/important-laboratories#{slugify(item['name'])}",
                        "document_type": "facility",
                    })
            session.flush()

        # --- research projects ---
        for status, pagepath in [("completed", "completed-research-projects"),
                                 ("ongoing", "on-going-research-projects")]:
            rows = client.list_page(pagepath)
            if not rows:
                logger.info("research/%s: no data (endpoint returned nothing)", status)
                continue
            f, w = write_research(session, rows, status)
            counts(f"research/{status}", f, w)
            for r in rows:
                item = parse_research(r, status)
                if item["title"]:
                    doc_items.append({
                        "title": item["title"],
                        "text": " ".join(filter(None, [
                            f"Research project ({status}): {item['title']}",
                            f"Funding agency: {item['funding_agency']}" if item["funding_agency"] else "",
                            f"Amount: {item['amount']}" if item["amount"] else "",
                            f"Principal investigator: {item['principal_investigator']}" if item["principal_investigator"] else "",
                            item["description"],
                        ])),
                        "source_url": f"{item['source_url']}#{slugify(item['title'])}",
                        "document_type": "research",
                    })
            session.flush()

        # --- write the whole RAG corpus (dedup by source_url, embed new) ---
        f, w = write_documents(session, embed_fn, doc_items)
        counts("documents/corpus (about+notices+programs+labs+research)", f, w)
        session.flush()

        session.commit()

    except Exception as exc:  # keep the audit trail even on failure
        logger.exception("ingestion failed")
        session.rollback()
        try:
            log_run(session, "ingestion/run", 0, 0, "error", str(exc))
            session.commit()
        except Exception:
            session.rollback()
    finally:
        client.close()
        session.close()

    logger.info("total rows written: %d", total_written)
    return total_written


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    run_ingestion(embedding=True)