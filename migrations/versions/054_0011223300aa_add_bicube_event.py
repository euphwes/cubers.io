"""Add BiCube

Revision ID: 0011223300aa
Revises: 01d403b3c85d
Create Date: 2024-04-16 09:13:10.123332

"""
from alembic import op
from sqlalchemy.sql import table, column
from sqlalchemy import String

from cubersio.persistence.models import EventFormat, Event

# revision identifiers, used by Alembic.
revision = '0011223300aa'
down_revision = '01d403b3c85d'
branch_labels = None
depends_on = None

def upgrade():
    op.bulk_insert(
        Event.__table__,
        [
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': 'BiCube'},
        ]
    )
    events = table('events', column('name', String), column('description', String))
    op.execute(events.update().where(events.c.name == op.inline_literal('BiCube')).values({'description': op.inline_literal("<p>BiCube, aka Meffert's Bandaged Cube.</p>")}))


def downgrade():
    pass
