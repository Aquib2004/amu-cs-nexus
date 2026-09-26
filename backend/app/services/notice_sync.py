"""Live, notices-only AMU synchronization and Web Push delivery trigger."""

import hashlib
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from app.models.document import Chunk, Document
from app.models.notice import Notice
from app.services.push import send_notice_notifications
from app.services.uploads import purge_expired_uploads

logger = logging.getLogger(__name__)
AMU_API = "https://api.amu.ac.in/api/v1"
NOTICE_PATH = "department-list-data?lang=en&slug=department/computer-science/notice-and-circular"


def _rows(payload) -> list[dict]:
    current = payload
    for _ in range(6):
        if isinstance(current, dict) and "data" in current:
            current = current["data"]
        else:
            break
    return current if isinstance(current, list) else []


def _parse(row: dict) -> dict | None:
    title = str(row.get("title") or "").strip()
    file_path = str(row.get("file") or "")
    if not title or not file_path:
        return None
    url = f"{AMU_API}{file_path}" if file_path.startswith("/") else file_path
    created = row.get("created_at")
    published = None
    if isinstance(created, str) and "T" in created:
        try:
            published = datetime.fromisoformat(created.replace("Z", "+00:00"))
        except ValueError:
            pass
    lower = title.lower()
    category = "general"
    if any(word in lower for word in ("exam", "examination", "interview")):
        category = "examinations"
    elif any(word in lower for word in ("ph.d", "phd", "fellowship", "research")):
        category = "research"
    elif any(word in lower for word in ("sports", "festival", "event")):
        category = "events"
    return {"title": title[:500], "url": url[:1000], "category": category, "published_at": published}


def sync_notices(session: Session, client: httpx.Client | None = None) -> list[Notice]:
    """Upsert the first notice page and return only newly-created notices."""
    owns_client = client is None
    client = client or httpx.Client(timeout=30, verify=False, follow_redirects=True,
                                   headers={"User-Agent": "AMUCS-Nexus notice sync"})
    created: list[Notice] = []
    try:
        response = client.get(f"{AMU_API}/{NOTICE_PATH}&page=1")
        response.raise_for_status()
        for raw in _rows(response.json()):
            item = _parse(raw)
            if not item:
                continue
            exists = session.query(Notice).filter_by(title=item["title"], url=item["url"]).first()
            if exists:
                continue
            notice = Notice(**item, crawl_timestamp=datetime.now(timezone.utc))
            session.add(notice)
            session.flush()
            doc = Document(
                title=item["title"],
                source_url=item["url"],
                source_type="web",
                document_type="notice",
                department="computer-science",
                content_hash=hashlib.sha256(item["title"].encode("utf-8")).hexdigest(),
                crawl_timestamp=datetime.now(timezone.utc),
            )
            doc.chunks.append(Chunk(chunk_index=0, text=item["title"]))
            session.add(doc)
            created.append(notice)
        session.commit()
    except Exception:
        session.rollback()
        logger.exception("Live notice sync failed")
    finally:
        if owns_client:
            client.close()
    return created


def run_notice_cycle(session: Session) -> int:
    created = sync_notices(session)
    purge_expired_uploads(session)
    if created:
        send_notice_notifications(session, created)
    return len(created)