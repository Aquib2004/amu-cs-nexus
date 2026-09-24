"""Add programs, laboratories, research_projects, staff_members, ingestion_log;
add image_url and source_url to faculties.

Revision ID: 0004
Revises: 0003
"""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "programs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("level", sa.String(length=20), nullable=True),
        sa.Column("intake_seats", sa.String(length=100), nullable=True),
        sa.Column("duration", sa.Text(), nullable=True),
        sa.Column("eligibility", sa.Text(), nullable=True),
        sa.Column("curriculum_url", sa.String(length=1000), nullable=True),
        sa.Column("syllabus_url", sa.String(length=1000), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("crawl_timestamp", sa.DateTime(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "laboratories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("file", sa.String(length=1000), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("crawl_timestamp", sa.DateTime(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "research_projects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("funding_agency", sa.String(length=500), nullable=True),
        sa.Column("amount", sa.String(length=200), nullable=True),
        sa.Column("principal_investigator", sa.String(length=300), nullable=True),
        sa.Column("co_investigators", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("crawl_timestamp", sa.DateTime(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "staff_members",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("designation", sa.String(length=200), nullable=True),
        sa.Column("email", sa.String(length=200), nullable=True),
        sa.Column("phone", sa.String(length=100), nullable=True),
        sa.Column("image_url", sa.String(length=1000), nullable=True),
        sa.Column("profile_url", sa.String(length=1000), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=False),
        sa.Column("crawl_timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "ingestion_log",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source", sa.String(length=500), nullable=False),
        sa.Column("fetched_at", sa.DateTime(), nullable=False),
        sa.Column("rows_found", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rows_written", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ok"),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "faculties",
        sa.Column("image_url", sa.String(length=1000), nullable=True),
    )
    op.add_column(
        "faculties",
        sa.Column("source_url", sa.String(length=1000), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_table("ingestion_log")
    op.drop_table("staff_members")
    op.drop_table("research_projects")
    op.drop_table("laboratories")
    op.drop_table("programs")
    op.drop_column("faculties", "source_url")
    op.drop_column("faculties", "image_url")