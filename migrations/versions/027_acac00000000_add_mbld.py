"""Add MBLD

Revision ID: acac00000000
Revises: 347361bd5358
Create Date: 2019-06-06 12:23:00.123969

"""
from alembic import op
from app.persistence.models import EventFormat, Event

# revision identifiers, used by Alembic.
revision = 'acac00000000'
down_revision = '347361bd5358'
branch_labels = None
depends_on = None

def upgrade():
    op.bulk_insert(
        Event.__table__,
        [
            {'totalSolves': 3, 'eventFormat': EventFormat.Bo3, 'name': 'MBLD' },
        ]
    )

def downgrade():
    pass
