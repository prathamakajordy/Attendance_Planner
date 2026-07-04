"""add plan tables

Revision ID: a1b2c3d4e5f6
Revises: 084230ad1326
Create Date: 2026-07-04 19:48:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '084230ad1326'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create plan_metadata, plan_day, and plan_block tables."""
    op.create_table(
        'plan_metadata',
        sa.Column('semester_id', sa.Integer(), sa.ForeignKey('semester_profile.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.Column('engine_version', sa.String(), nullable=False),
        sa.Column('overall_feasible', sa.Boolean(), nullable=False, server_default='1'),
    )

    op.create_table(
        'plan_day',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('semester_id', sa.Integer(), sa.ForeignKey('semester_profile.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('is_lecture_day', sa.Boolean(), nullable=False),
        sa.Column('day_explanation', sa.String(), nullable=True),
    )

    op.create_table(
        'plan_block',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('plan_day_id', sa.Integer(), sa.ForeignKey('plan_day.id', ondelete='CASCADE'), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('subject_ids', sa.String(), nullable=False),
        sa.Column('recommendation', sa.String(), nullable=False),
        sa.Column('block_explanation', sa.String(), nullable=True),
    )


def downgrade() -> None:
    """Drop plan tables."""
    op.drop_table('plan_block')
    op.drop_table('plan_day')
    op.drop_table('plan_metadata')
