"""add more event descriptions

Revision ID: bbeebbee3456
Revises: bbeebbee2345
Create Date: 2019-06-17 17:05:04.276404

"""
from sqlalchemy.sql import table, column
from sqlalchemy import String
from alembic import op

# revision identifiers, used by Alembic.
revision = 'bbeebbee3456'
down_revision = 'bbeebbee2345'
branch_labels = None
depends_on = None

def upgrade():
    events = table('events', column('name', String), column('description', String))
    op.execute(events.update().where(events.c.name == op.inline_literal('Dino Cube')).values({'description': op.inline_literal('<p>R indicates a clockwise turn of the UFR corner, and L indicates a clockwise turn of the UFL corner.</p>')}))
    op.execute(events.update().where(events.c.name == op.inline_literal('Redi Cube')).values({'description': op.inline_literal('<p>R indicates a clockwise turn of the UFR corner, and L indicates a clockwise turn of the UFL corner.</p>')}))

def downgrade():
    events = table('events', column('name', String), column('description', String))
    op.execute(events.update().where(events.c.name == op.inline_literal('Dino Cube')).values({'description': op.inline_literal('')}))
    op.execute(events.update().where(events.c.name == op.inline_literal('Redi Cube')).values({'description': op.inline_literal('')}))
