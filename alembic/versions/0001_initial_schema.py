"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-06 14:06:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=False),
    )
    op.create_index("ix_books_id", "books", ["id"], unique=False)

    op.create_table(
        "document_embeddings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", sa.JSON(), nullable=False),
    )
    op.create_index("ix_document_embeddings_id", "document_embeddings", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_document_embeddings_id", table_name="document_embeddings")
    op.drop_table("document_embeddings")
    op.drop_index("ix_books_id", table_name="books")
    op.drop_table("books")
