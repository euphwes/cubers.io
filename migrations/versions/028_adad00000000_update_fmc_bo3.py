"""Update FMC to Bo3

Revision ID: adad00000000
Revises: acac00000000
Create Date: 2019-06-07 13:33:00.123969

"""
from sqlalchemy.sql import table, column
from sqlalchemy import String
from alembic import op

# revision identifiers, used by Alembic.
revision = 'adad00000000'
down_revision = 'acac00000000'
branch_labels = None
depends_on = None

def upgrade():
    events = table('events', column('name', String), column('eventFormat', String))
    op.execute(events.update().where(events.c.name == op.inline_literal('FMC')).values({'eventFormat': op.inline_literal('Bo3')}))

def downgrade():
    pass
