"""add fmc event description

Revision ID: 020203030404
Revises: e74ccd606cdc
Create Date: 2019-06-17 17:05:04.276404

"""
from sqlalchemy.sql import table, column
from sqlalchemy import String
from alembic import op

# revision identifiers, used by Alembic.
revision = '020203030404'
down_revision = 'e74ccd606cdc'
branch_labels = None
depends_on = None

def upgrade():
    events = table('events', column('name', String), column('description', String))
    op.execute(events.update().where(events.c.name == op.inline_literal('FMC')).values({'description': op.inline_literal('<p>To participate in FMC, please enter your solution using the "Solution" button on this page.</p><p>Your solution will be checked to see if it solves the current scramble. If it does, the move count in OBTM (Outer Block Turn Metric) will be calculated, and you will able to submit your solution.</p><p>Your solution may include comments, beginning with any of the following characters: <span style="font-style: monospace; color: grey; background-color: #fcfcf5; padding: 5px;">/, \, #, -</span>. These comments will be ignored.</p><p>Please note that we cannot interpret special notation such as skeletons, insertions, or cancellations, so your solution must be a consecutive series of moves that will solve the provided scramble. Your solution may spans multiple lines, with comments if desired.</p><p>If you wish to add additional information regarding skeletons, insertions, or cancellations, you may do so within comment lines.</p>')}))

def downgrade():
    events = table('events', column('name', String), column('description', String))
    op.execute(events.update().where(events.c.name == op.inline_literal('FMC')).values({'description': op.inline_literal('')}))
