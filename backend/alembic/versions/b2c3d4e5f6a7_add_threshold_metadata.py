"""add threshold metadata

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-04 19:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add thresholds to plan_metadata."""
    op.add_column('plan_metadata', sa.Column('overall_attendance_threshold', sa.Float(), nullable=False, server_default='75.0'))
    op.add_column('plan_metadata', sa.Column('subject_attendance_threshold', sa.Float(), nullable=False, server_default='75.0'))


def downgrade() -> None:
    """Drop thresholds from plan_metadata."""
    op.drop_column('plan_metadata', 'subject_attendance_threshold')
    op.drop_column('plan_metadata', 'overall_attendance_threshold')
