"""Add 2x2x3

Revision ID: bbeebbee2345
Revises: bbeebbee1234
Create Date: 2019-08-23 12:23:00.123969

"""
from alembic import op
from cubersio.persistence.models import EventFormat, Event

# revision identifiers, used by Alembic.
revision = 'bbeebbee2345'
down_revision = 'bbeebbee1234'
branch_labels = None
depends_on = None

def upgrade():
    op.bulk_insert(
        Event.__table__,
        [
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': '2x2x3' },
        ]
    )

def downgrade():
    pass
