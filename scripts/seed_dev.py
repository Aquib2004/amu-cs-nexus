#!/usr/bin/env python
# scripts/seed_dev.py - DEV-ONLY sample data for local development.
#
# Inserts clearly-labeled example documents/chunks and notices so the local app
# has something to search and ask about. Never run against a production
# database. Requirements: run from the backend/ directory after
#   .\.venv\Scripts\activate        (or use the venv python directly)
#   .\.venv\Scripts\python.exe -m alembic upgrade head
#   .\.venv\Scripts\python.exe ..\scripts\seed_dev.py

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # amu-cs-nexus/
BACKEND = ROOT / "backend"
for _p in (str(ROOT), str(BACKEND)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sqlalchemy.orm import Session  # noqa: E402

from app.core.database import Base, engine  # noqa: E402
import app.models  # noqa: E402,F401  (register all tables on Base.metadata)
from app.models.document import Chunk, Document  # noqa: E402
from app.models.notice import Notice  # noqa: E402


DOCUMENTS = [
    {
        "title": "MCA Admission Notice",
        "source_url": "https://www.amu.ac.in/department/computer-science/notice-and-circular",
        "department": "computer-science",
        "source_type": "web",
        "document_type": "notice",
        "text": "The MCA admission notice was published in June 2024. Applications for the "
        "2024-25 session are open on the official AMU Online admissions portal.",
    },
    {
        "title": "Computer Vision Laboratory",
        "source_url": "https://www.amu.ac.in/department/computer-science/facilities",
        "department": "computer-science",
        "source_type": "web",
        "document_type": "facility",
        "text": "The computer vision laboratory contains 20 GPU workstations used for "
        "undergraduate and postgraduate research projects.",
    },
]

NOTICES = [
    {
        "title": "Mid-semester examination schedule",
        "url": "https://www.amu.ac.in/department/computer-science/notice-and-circular",
        "category": "examinations",
    },
    {
        "title": "Photographs invited for Sports Festival",
        "url": "https://www.amu.ac.in/recent-notices",
        "category": "events",
    },
]


def main() -> None:
    Base.metadata.create_all(engine)  # no-op if alembic already created tables
    with Session(engine) as session:
        if session.query(Document).count() == 0:
            for item in DOCUMENTS:
                doc = Document(
                    title=item["title"],
                    source_url=item["source_url"],
                    department=item["department"],
                    source_type=item["source_type"],
                    document_type=item["document_type"],
                )
                doc.chunks.append(Chunk(chunk_index=0, text=item["text"]))
                session.add(doc)
            print(f"Seeded {len(DOCUMENTS)} documents.")
        else:
            print("Documents already present; skipping.")

        if session.query(Notice).count() == 0:
            for item in NOTICES:
                session.add(Notice(title=item["title"], url=item["url"], category=item["category"]))
            print(f"Seeded {len(NOTICES)} notices.")
        else:
            print("Notices already present; skipping.")
        session.commit()


if __name__ == "__main__":
    main()
