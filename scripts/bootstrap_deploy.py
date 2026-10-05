#!/usr/bin/env python
r"""Prepare a database for a fresh deployment.

A clone has no database file: *.db is gitignored, so a freshly deployed
container would start with an empty schema and every page would read as
"No data indexed yet". This script makes that first boot useful.

Order of operations:
  1. Apply migrations so the schema matches the models (idempotent).
  2. Load a bundled JSON snapshot if one exists, so the deployment is
     immediately populated and does NOT depend on the AMU API being up.
  3. Otherwise leave the schema empty and let background sync fill it.

It never overwrites an existing populated database, so it is safe to run on
every container start.

Usage (from backend/):
    .\.venv\Scripts\python.exe ..\scripts\bootstrap_deploy.py
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
SNAPSHOT = ROOT / "data" / "seed_snapshot.json"

for _p in (str(ROOT), str(BACKEND)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sqlalchemy import func, select  # noqa: E402

from app.core.database import Base, SessionLocal, engine  # noqa: E402
import app.models  # noqa: E402,F401
from app.models.chunk_seed import load_snapshot  # noqa: E402

logger = logging.getLogger("bootstrap")


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    # 1. Schema. create_all is a no-op when Alembic has already run.
    Base.metadata.create_all(engine)
    logger.info("schema ready")

    with SessionLocal() as session:
        documents = session.scalar(select(func.count()).select_from(app.models.document.Document)) or 0

        if documents:
            logger.info("database already has %d documents; leaving it untouched", documents)
            return 0

        if not SNAPSHOT.exists():
            logger.warning(
                "no snapshot at %s; the deployment will start empty and rely on "
                "background notice sync", SNAPSHOT,
            )
            return 0

        logger.info("loading bundled snapshot from %s", SNAPSHOT)
        counts = load_snapshot(session, json.loads(SNAPSHOT.read_text(encoding="utf-8")))
        session.commit()
        logger.info("snapshot loaded: %s", counts)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())