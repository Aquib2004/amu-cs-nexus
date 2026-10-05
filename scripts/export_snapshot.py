#!/usr/bin/env python
r"""Export the public corpus to data/seed_snapshot.json.

The SQLite database itself is gitignored (it is a local build artefact), so a
deployment cannot receive it. This writes a portable JSON snapshot of the
public AMU content instead, which `scripts/bootstrap_deploy.py` loads on first
boot.

Embeddings are deliberately NOT exported: a 3072-float vector per chunk would
make the file tens of megabytes. On a fresh deployment the app falls back to
keyword + hash scoring, which still answers correctly; running the real
ingestion later will populate embeddings.

Excluded by design: chat_uploads, chat_upload_chunks and push_subscriptions
(private student data and anonymous browser endpoints must never be shipped).

Usage (from backend/):
    .\.venv\Scripts\python.exe ..\scripts\export_snapshot.py
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
OUT = ROOT / "data" / "seed_snapshot.json"

for _p in (str(ROOT), str(BACKEND)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from app.core.database import SessionLocal  # noqa: E402
from app.models.document import Document  # noqa: E402
from app.models.exam_resource import ExamResource  # noqa: E402
from app.models.faculty import Faculty  # noqa: E402
from app.models.laboratory import Laboratory  # noqa: E402
from app.models.notice import Notice  # noqa: E402
from app.models.program import Program  # noqa: E402
from app.models.research_project import ResearchProject  # noqa: E402
from app.models.staff import StaffMember  # noqa: E402


def _json(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    payload: dict = {}

    with SessionLocal() as session:
        documents = []
        for doc in session.query(Document).all():
            documents.append({
                "title": doc.title,
                "source_url": doc.source_url,
                "source_type": doc.source_type,
                "document_type": doc.document_type,
                "department": doc.department,
                "publication_date": _json(doc.publication_date),
                "crawl_timestamp": _json(doc.crawl_timestamp),
                "content_hash": doc.content_hash,
                "version": doc.version,
                "status": doc.status,
                "chunks": [c.text for c in sorted(doc.chunks, key=lambda x: x.chunk_index)],
            })
        payload["documents"] = documents

        for key, model in [
            ("notices", Notice),
            ("faculty", Faculty),
            ("programs", Program),
            ("laboratories", Laboratory),
            ("staff_members", StaffMember),
            ("research_projects", ResearchProject),
            ("exam_resources", ExamResource),
        ]:
            rows = []
            for row in session.query(model).all():
                item = {}
                for column in model.__table__.columns:
                    if column.name == "id":
                        continue
                    item[column.name] = _json(getattr(row, column.name))
                rows.append(item)
            payload[key] = rows

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    size_mb = OUT.stat().st_size / 1_048_576
    logging.getLogger("export").info(
        "wrote %s (%.1f MB): %s", OUT, size_mb,
        {k: len(v) for k, v in payload.items()},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())