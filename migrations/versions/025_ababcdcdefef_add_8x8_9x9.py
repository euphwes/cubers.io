"""Add 8x8 and 9x9

Revision ID: ababcdcdefef
Revises: c92d221771c4
Create Date: 2019-03-11 16:39:00.123969

"""
from alembic import op
import sqlalchemy as sa
from app.persistence.models import EventFormat, Event

# revision identifiers, used by Alembic.
revision = 'ababcdcdefef'
down_revision = 'c92d221771c4'
branch_labels = None
depends_on = None

def upgrade():
    op.bulk_insert(
        Event.__table__,
        [
            {'totalSolves': 1, 'eventFormat': EventFormat.Bo1, 'name': '8x8' },
            {'totalSolves': 1, 'eventFormat': EventFormat.Bo1, 'name': '9x9' },
        ]
    )

def downgrade():
    pass
