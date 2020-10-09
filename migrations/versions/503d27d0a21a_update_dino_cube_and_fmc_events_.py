"""Update Dino Cube and FMC events descriptions

Revision ID: 503d27d0a21a
Revises: 555566667777
Create Date: 2020-10-09 13:23:54.090903

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '503d27d0a21a'
down_revision = '555566667777'
branch_labels = None
depends_on = None


def upgrade():
    events = table('events', column('name', String), column('description', String))
    op.execute(events.update().where(events.c.name == op.inline_literal('Dino Cube')).values({'description': op.inline_literal('<p>R indicates a clockwise turn of the UFR corner, and L indicates a clockwise turn of the UFL corner. Any solved state is considered solved</p>')}))
    op.execute(events.update().where(events.c.name == op.inline_literal('FMC')).values({'description': op.inline_literal('<p>To participate in FMC, please enter your solution using the "Solution" button on this page.</p><p>Your solution will be checked to see if it solves the current scramble. If it does, the move count in OBTM (Outer Block Turn Metric) will be calculated, and you will able to submit your solution.</p><p>Your solution may include comments, beginning with any of the following characters: <span style="font-style: monospace; color: grey; background-color: #fcfcf5; padding: 5px;">/, \, #, -</span>. These comments will be ignored.</p><p>Please note that we cannot interpret special notation such as skeletons, insertions, or cancellations, so your solution must be a consecutive series of moves that will solve the provided scramble. Your solution may spans multiple lines, with comments if desired.</p><p>If you wish to add additional information regarding skeletons, insertions, or cancellations, you may do so within comment lines. Remember that any cube rotation is not counted as a move.</p>')}))

def downgrade():
    events = table('events', column('name', String), column('description', String))
    op.execute(events.update().where(events.c.name == op.inline_literal('Dino Cube')).values({'description': op.inline_literal('<p>R indicates a clockwise turn of the UFR corner, and L indicates a clockwise turn of the UFL corner.</p>')}))
    op.execute(events.update().where(events.c.name == op.inline_literal('FMC')).values({'description': op.inline_literal('<p>To participate in FMC, please enter your solution using the "Solution" button on this page.</p><p>Your solution will be checked to see if it solves the current scramble. If it does, the move count in OBTM (Outer Block Turn Metric) will be calculated, and you will able to submit your solution.</p><p>Your solution may include comments, beginning with any of the following characters: <span style="font-style: monospace; color: grey; background-color: #fcfcf5; padding: 5px;">/, \, #, -</span>. These comments will be ignored.</p><p>Please note that we cannot interpret special notation such as skeletons, insertions, or cancellations, so your solution must be a consecutive series of moves that will solve the provided scramble. Your solution may spans multiple lines, with comments if desired.</p><p>If you wish to add additional information regarding skeletons, insertions, or cancellations, you may do so within comment lines.</p>')}))


