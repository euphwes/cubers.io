"""Update mirror blocks event description.

Revision ID: 555566667777
Revises: 9a8860e9294c
Create Date: 2020-04-14 16:52:59.629905

"""
from sqlalchemy.sql import table, column
from sqlalchemy import String
from alembic import op


# revision identifiers, used by Alembic.
revision = '555566667777'
down_revision = '9a8860e9294c'
branch_labels = None
depends_on = None


def upgrade():
    events = table('events', column('name', String), column('description', String))
    op.execute(events.update().where(events.c.name == op.inline_literal('3x3 Mirror Blocks/Bump')).values({'description': op.inline_literal('<p>Please use a Mirror Blocks with a single color. Scramble as you would a standard 3x3, with the thinnest layer on top, and the smallest piece in that layer at the front-right of the cube.</p>')}))

def downgrade():
    events = table('events', column('name', String), column('description', String))
    op.execute(events.update().where(events.c.name == op.inline_literal('FMC')).values({'description': op.inline_literal('<p>Scramble as you would a 3x3, starting from any orientation since Mirror Blocks do not have an established standard scrambling orientation.</p>')}))
