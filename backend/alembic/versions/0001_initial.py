"""Initial schema: documents, chunks, notices.

Revision ID: 0001
Revises:
Create Date: 2026-09-16
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=False),
        sa.Column("source_type", sa.String(length=100), nullable=True),
        sa.Column("document_type", sa.String(length=100), nullable=True),
        sa.Column("department", sa.String(length=200), nullable=True),
        sa.Column("publication_date", sa.Date(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("crawl_timestamp", sa.DateTime(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "chunks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("extra_metadata", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chunks_document_id", "chunks", ["document_id"])
    op.create_table(
        "notices",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("crawl_timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("notices")
    op.drop_index("ix_chunks_document_id", table_name="chunks")
    op.drop_table("chunks")
    op.drop_table("documents")