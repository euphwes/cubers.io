"""Add Fifteen Puzzle

Revision ID: 05923bad79cf
Revises: 74b025612a81
Create Date: 2020-10-23 12:23:00.123969

"""
from alembic import op
from app.persistence.models import EventFormat, Event

# revision identifiers, used by Alembic.
revision = '05923bad79cf'
down_revision = '74b025612a81'
branch_labels = None
depends_on = None

def upgrade():
    op.bulk_insert(
        Event.__table__,
        [
            {'totalSolves': 3, 'eventFormat': EventFormat.Mo3, 'name': '15 Puzzle' },
        ]
    )

def downgrade():
    pass
