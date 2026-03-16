"""Deactivate legacy tariffs without vehicle_type_uid

Revision ID: e3a1b2c4d5f6
Revises: d1ff2c63e714
Create Date: 2026-03-16 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3a1b2c4d5f6'
down_revision = 'd1ff2c63e714'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "UPDATE tariffs SET is_active = 0 WHERE vehicle_type_uid IS NULL"
    )


def downgrade():
    pass
