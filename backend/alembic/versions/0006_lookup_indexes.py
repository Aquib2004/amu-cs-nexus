"""Add lookup indexes for notices, documents, and faculty.

These are deliberately NON-unique. Real ingestion must never fail because two
official AMU records happen to share a URL, an email, or a title:

- `sync_notices` de-duplicates on (title, url), and AMU can legitimately
  re-point a file path, so url alone is not a safe unique key.
- `write_faculty` de-duplicates on name; two listings can share an email.

A UNIQUE constraint here would raise IntegrityError and roll back an entire
sync/ingest batch, which is a worse outcome than a duplicate row. The indexes
below still make the de-duplication lookups fast.

Revision ID: 0006
Revises: 0005
"""

from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_notices_url", "notices", ["url"])
    op.create_index("ix_notices_title", "notices", ["title"])
    op.create_index("ix_documents_source_url", "documents", ["source_url"])
    op.create_index("ix_faculties_email", "faculties", ["email"])


def downgrade() -> None:
    op.drop_index("ix_faculties_email", table_name="faculties")
    op.drop_index("ix_documents_source_url", table_name="documents")
    op.drop_index("ix_notices_title", table_name="notices")
    op.drop_index("ix_notices_url", table_name="notices")