#!/usr/bin/env python
# scripts/seed_dev.py - DEV-ONLY sample data for local development.
#
# Inserts clearly-labeled example documents/chunks, notices, and faculty so the
# local app has something to search, browse, and ask about. Never run against a
# production database. Run from the backend/ directory after migrations:
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
from app.models.faculty import Faculty  # noqa: E402
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

RESEARCH_DOCUMENTS = [
    {
        "title": "A Survey of Vision Transformers in Medical Imaging",
        "source_url": "https://www.amu.ac.in/department/computer-science/publications",
        "document_type": "publication",
        "text": "This paper reviews vision transformer architectures applied to medical "
        "image segmentation and classification, including attention mechanisms.",
    }
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

FACULTY = [
    {
        "name": "Prof. A. Rahman",
        "title": "Professor",
        "designation": "Head of Department",
        "department": "computer-science",
        "email": "arahman@amu.ac.in",
        "specializations": ["Algorithms", "Theory of Computation"],
        "research_areas": ["Data Structures", "Computational Complexity"],
        "profile_url": "https://www.amu.ac.in/department/computer-science/faculty",
    },
    {
        "name": "Dr. S. Begum",
        "title": "Assistant Professor",
        "designation": "Faculty",
        "department": "computer-science",
        "email": "sbegum@amu.ac.in",
        "specializations": ["Machine Learning", "Computer Vision"],
        "research_areas": ["Deep Learning", "Medical Imaging"],
        "profile_url": "https://www.amu.ac.in/department/computer-science/faculty",
    },
]


def _seed_documents(session: Session) -> None:
    # Idempotent per document (so new dev docs get added on re-runs even when
    # other documents already exist).
    existing = {row.title for row in session.query(Document.title)}
    added = 0
    for item in DOCUMENTS + RESEARCH_DOCUMENTS:
        if item["title"] in existing:
            continue
        doc = Document(
            title=item["title"],
            source_url=item["source_url"],
            department=item.get("department"),
            source_type=item.get("source_type", "web"),
            document_type=item.get("document_type", "web_page"),
        )
        doc.chunks.append(Chunk(chunk_index=0, text=item["text"]))
        session.add(doc)
        added += 1
    print(f"Seeded {added} new documents." if added else "All documents already present; skipping.")


def _seed_notices(session: Session) -> None:
    if session.query(Notice).count() > 0:
        print("Notices already present; skipping.")
        return
    for item in NOTICES:
        session.add(Notice(title=item["title"], url=item["url"], category=item["category"]))
    print(f"Seeded {len(NOTICES)} notices.")


def _seed_faculty(session: Session) -> None:
    if session.query(Faculty).count() > 0:
        print("Faculty already present; skipping.")
        return
    for item in FACULTY:
        session.add(
            Faculty(
                name=item["name"],
                title=item["title"],
                designation=item["designation"],
                department=item["department"],
                email=item["email"],
                specializations=item["specializations"],
                research_areas=item["research_areas"],
                profile_url=item["profile_url"],
            )
        )
    print(f"Seeded {len(FACULTY)} faculty members.")


def main() -> None:
    Base.metadata.create_all(engine)  # no-op if alembic already created tables
    with Session(engine) as session:
        _seed_documents(session)
        _seed_notices(session)
        _seed_faculty(session)
        session.commit()


if __name__ == "__main__":
    main()