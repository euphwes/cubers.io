"""Add FTO (Face-Turning Octahedron)

Revision ID: 050050fe0fe0
Revises: 9036ae93bb1c
Create Date: 2020-12-06 12:23:00.123969

"""
from alembic import op
from sqlalchemy.sql import table, column
from sqlalchemy import String

from cubersio.persistence.models import EventFormat, Event

# revision identifiers, used by Alembic.
revision = '050050fe0fe0'
down_revision = '9036ae93bb1c'
branch_labels = None
depends_on = None

def upgrade():
    op.bulk_insert(
        Event.__table__,
        [
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': 'FTO' },
        ]
    )
    events = table('events', column('name', String), column('description', String))
    op.execute(events.update().where(events.c.name == op.inline_literal('FTO')).values({'description': op.inline_literal('<p>FTO = Face-Turning Octahedron</p><p>BR = Back-right, BL = Back-left</p><p>Scramble using 3x3 conventions/notation.</p>')}))


def downgrade():
    pass
