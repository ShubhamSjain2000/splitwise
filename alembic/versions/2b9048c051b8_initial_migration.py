"""Initial migration

Revision ID: 2b9048c051b8
Revises: 
Create Date: 2023-09-30 20:55:40.377446

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2b9048c051b8"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("user_id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=128), nullable=False),
        sa.Column("mobile_number", sa.String(length=10), nullable=True),
    )
    op.create_unique_constraint("unique_email_constraint", "user", ["email"])

    op.create_table(
        "expense",
        sa.Column(
            "expense_id",
            sa.Integer(),
            nullable=True,
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column(
            "total_amount", sa.Float(precision=2, asdecimal=True), nullable=False
        ),
        sa.Column("split_type", sa.String(length=128), nullable=False),
        sa.Column("paid_by", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["paid_by"], ["user.user_id"]),
    )

    op.create_table(
        "share",
        sa.Column(
            "share_id",
            sa.Integer(),
            nullable=True,
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column("expense_id", sa.Integer(), nullable=False),
        sa.Column("debtor_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(precision=2, asdecimal=True), nullable=False),
        sa.ForeignKeyConstraint(["expense_id"], ["expense.expense_id"]),
        sa.ForeignKeyConstraint(["debtor_id"], ["user.user_id"]),
    )

    op.create_table(
        "balance",
        sa.Column(
            "balance_id",
            sa.Integer(),
            nullable=True,
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column("owed_to", sa.Integer(), nullable=False),
        sa.Column("owed_by", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(precision=2, asdecimal=True), nullable=True),
        sa.ForeignKeyConstraint(["owed_to"], ["user.user_id"]),
        sa.ForeignKeyConstraint(["owed_by"], ["user.user_id"]),
    )


def downgrade() -> None:
    op.drop_table("user")
    op.drop_table("expense")
    op.drop_table("share")
    op.drop_table("balance")
