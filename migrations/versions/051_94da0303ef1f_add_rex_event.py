"""Add Rex Cube

Revision ID: 94da0303ef1f
Revises: 050050fe0fe0
Create Date: 2021-03-30 12:23:00.123969

"""
from alembic import op
from sqlalchemy.sql import table, column
from sqlalchemy import String

from cubersio.persistence.models import EventFormat, Event

# revision identifiers, used by Alembic.
revision = '94da0303ef1f'
down_revision = '050050fe0fe0'
branch_labels = None
depends_on = None

def upgrade():
    op.bulk_insert(
        Event.__table__,
        [
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': 'Rex Cube'},
        ]
    )
    events = table('events', column('name', String), column('description', String))
    op.execute(events.update().where(events.c.name == op.inline_literal('Rex Cube')).values({'description': op.inline_literal('<p>Scramble using <a href="http://rubikskewb.web.fc2.com/skewb/notation.html">this notation</a>.</p>')}))


def downgrade():
    pass
