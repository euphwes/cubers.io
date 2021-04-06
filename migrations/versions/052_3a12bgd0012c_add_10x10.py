"""Add 10x10

Revision ID: 3a12bgd0012c
Revises: 94da0303ef1f
Create Date: 2021-04-06 12:23:00.123969

"""
from alembic import op
from sqlalchemy.sql import table, column
from sqlalchemy import String

from cubersio.persistence.models import EventFormat, Event

# revision identifiers, used by Alembic.
revision = '3a12bgd0012c'
down_revision = '94da0303ef1f'
branch_labels = None
depends_on = None

def upgrade():
    op.bulk_insert(
        Event.__table__,
        [
            {'totalSolves': 1, 'eventFormat': EventFormat.Bo1, 'name': '10x10'},
        ]
    )
    events = table('events', column('name', String), column('description', String))
    op.execute(events.update().where(events.c.name == op.inline_literal('10x10')).values({'description': op.inline_literal('<p>OmG iZ tHAt A 10x10. But for real though, no more bigger NxNs.</p>')}))


def downgrade():
    pass
