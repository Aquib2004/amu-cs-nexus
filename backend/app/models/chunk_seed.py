"""Load a JSON data snapshot into the database.

Used by `scripts/bootstrap_deploy.py` so a fresh deployment is populated
without depending on the AMU API being reachable, and by the tests.

Only public, already-published AMU content is stored here: documents, chunks,
notices, faculty, programmes, laboratories, staff, research projects and exam
resources. Private student uploads and push subscriptions are NEVER included.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.document import Chunk, Document
from app.models.exam_resource import ExamResource
from app.models.faculty import Faculty
from app.models.laboratory import Laboratory
from app.models.notice import Notice
from app.models.program import Program
from app.models.research_project import ResearchProject
from app.models.staff import StaffMember

# Keys written by scripts/export_snapshot.py, in dependency order.
_ORDER = [
    "documents",
    "notices",
    "faculty",
    "programs",
    "laboratories",
    "staff_members",
    "research_projects",
    "exam_resources",
]

# Explicit dedupe column per table. Guessing this from the first row silently
# dropped research_projects, whose key is `title` (it has neither url nor name).
_MODELS = {
    "notices": (Notice, "url"),
    "faculty": (Faculty, "name"),
    "programs": (Program, "name"),
    "laboratories": (Laboratory, "name"),
    "staff_members": (StaffMember, "name"),
    "research_projects": (ResearchProject, "title"),
    "exam_resources": (ExamResource, "url"),
}


def _coerce(value: Any, column_type: str) -> Any:
    """Turn ISO strings from JSON back into date/datetime objects."""
    if value in (None, ""):
        return None
    if column_type.startswith("DATETIME") and isinstance(value, str):
        return datetime.fromisoformat(value)
    if column_type.startswith("DATE") and isinstance(value, str):
        return date.fromisoformat(value)
    return value


def load_snapshot(session: Session, payload: dict) -> dict[str, int]:
    """Insert a snapshot, skipping rows that already exist by source URL/title."""
    counts: dict[str, int] = {}

    for row in payload.get("documents", []):
        doc = session.query(Document).filter_by(source_url=row["source_url"]).first()
        if doc is not None:
            continue
        doc = Document(
            title=row["title"],
            source_url=row["source_url"],
            source_type=row.get("source_type"),
            document_type=row.get("document_type"),
            department=row.get("department"),
            publication_date=_coerce(row.get("publication_date"), "DATE"),
            crawl_timestamp=_coerce(row.get("crawl_timestamp"), "DATETIME")
            or datetime.utcnow(),
            content_hash=row.get("content_hash"),
            version=row.get("version", 1),
            status=row.get("status", "active"),
        )
        for index, text in enumerate(row.get("chunks", [])):
            doc.chunks.append(Chunk(chunk_index=index, text=text))
        session.add(doc)
        counts["documents"] = counts.get("documents", 0) + 1

    for key, (model, id_column) in _MODELS.items():
        rows = payload.get(key, [])
        if not rows:
            continue
        added = 0
        for row in rows:
            value = row.get(id_column)
            if value is None:
                continue
            if session.query(model).filter(getattr(model, id_column) == value).first():
                continue
            fields: dict[str, Any] = {}
            for column in model.__table__.columns:
                if column.name == "id" or column.name not in row:
                    continue
                fields[column.name] = _coerce(row[column.name], str(column.type))
            session.add(model(**fields))
            added += 1
        if added:
            counts[key] = added
        session.flush()

    return counts