"""Update Make 15 Puzzle Ao5

Revision ID: 9036ae93bb1c
Revises: 9203bd471dg0
Create Date: 2019-06-07 13:33:00.123969

"""
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer
from alembic import op

# revision identifiers, used by Alembic.
revision = '9036ae93bb1c'
down_revision = '9203bd471dg0'
branch_labels = None
depends_on = None

def upgrade():
    events = table('events', column('name', String), column('eventFormat', String), column('totalSolves', Integer))
    op.execute(events.update().where(events.c.name == op.inline_literal('15 Puzzle')).values({'eventFormat': op.inline_literal('Ao5'), 'totalSolves': op.inline_literal(5)}))

def downgrade():
    pass
