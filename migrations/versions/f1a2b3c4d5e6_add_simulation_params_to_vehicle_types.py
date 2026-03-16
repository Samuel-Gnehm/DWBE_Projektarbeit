"""ADD: Simulationsparameter (meter_per_minute, battery_drain, battery_charge) zu vehicle_types

Revision ID: f1a2b3c4d5e6
Revises: e3a1b2c4d5f6
Create Date: 2026-03-16 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = 'e3a1b2c4d5f6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('vehicle_types', schema=None) as batch_op:
        batch_op.add_column(sa.Column('meter_per_minute', sa.Integer(), nullable=False, server_default='200'))
        batch_op.add_column(sa.Column('battery_drain_per_minute', sa.Numeric(5, 2), nullable=False, server_default='1.00'))
        batch_op.add_column(sa.Column('battery_charge_per_minute', sa.Numeric(5, 2), nullable=False, server_default='4.00'))


def downgrade():
    with op.batch_alter_table('vehicle_types', schema=None) as batch_op:
        batch_op.drop_column('battery_charge_per_minute')
        batch_op.drop_column('battery_drain_per_minute')
        batch_op.drop_column('meter_per_minute')
