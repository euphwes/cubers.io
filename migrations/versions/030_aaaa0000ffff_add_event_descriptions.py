"""add event descriptions

Revision ID: aaaa0000ffff
Revises: adad00000000
Create Date: 2019-06-17 17:05:04.276404

"""
from sqlalchemy.sql import table, column
from sqlalchemy import String
from alembic import op

# revision identifiers, used by Alembic.
revision = 'aaaa0000ffff'
down_revision = 'adad00000000'
branch_labels = None
depends_on = None

def upgrade():
    events = table('events', column('name', String), column('description', String))
    op.execute(events.update().where(events.c.name == op.inline_literal('2-3-4 Relay')).values({'description': op.inline_literal('<p>Scramble a 2x2, 3x3, and 4x4 with the provided scrambles. You may solve the puzzles in any order.</p><p>If you are using inspection time, there is only one inspection period for all three puzzles.</p>')}))
    op.execute(events.update().where(events.c.name == op.inline_literal('3x3 Relay of 3')).values({'description': op.inline_literal('<p>Scramble three 3x3s with the provided scrambles. You may solve the puzzles in any order.</p><p>If you are using inspection time, there is only one inspection period for all three puzzles.</p>')}))
    op.execute(events.update().where(events.c.name == op.inline_literal('2GEN')).values({'description': op.inline_literal("<p>For this event, the scramble only uses &#60;R,U&#62; moves, and your solution may only use &#60;R,U&#62; moves: (R, R', R2, U, U', U2).</p>")}))
    op.execute(events.update().where(events.c.name == op.inline_literal('LSE')).values({'description': op.inline_literal("<p>For this event, the scramble only uses &#60;M,U&#62; moves, and so your solution may only use &#60;M,U&#62; moves: (M, M', M2, U, U', U2).</p>")}))
    op.execute(events.update().where(events.c.name == op.inline_literal('2BLD')).values({'description': op.inline_literal("<p>Like WCA BLD events, your inspection time is counted towards the solve.</p><p>Please do not inspect the puzzle before starting the timer!</p>")}))
    op.execute(events.update().where(events.c.name == op.inline_literal('Kilominx')).values({'description': op.inline_literal("<p>Scramble as you would a Megaminx, held in standard orientation (white on U, green on F).</p>")}))
    op.execute(events.update().where(events.c.name == op.inline_literal('3x3 Mirror Blocks/Bump')).values({'description': op.inline_literal("<p>Scramble as you would a 3x3, starting from any orientation since Mirror Blocks do not have an established standard scrambling orientation.</p>")}))
    op.execute(events.update().where(events.c.name == op.inline_literal('PLL Time Attack')).values({'description': op.inline_literal("<p>Do all the PLLs!</p><p>PLL order doesn't matter, and your cube may not be fully solved when complete.</p><p>Solved, or unsolved with OLL complete is ok. If F2L and/or OLL are not complete, the solve is a DNF.</p>")}))
    op.execute(events.update().where(events.c.name == op.inline_literal('F2L')).values({'description': op.inline_literal("<p>Scramble as you would a 3x3, but stop the timer after you complete F2L.</p>")}))

def downgrade():
    events = table('events', column('name', String), column('description', String))
    op.execute(events.update().where(events.c.name == op.inline_literal('2-3-4 Relay')).values({'description': op.inline_literal('')}))
    op.execute(events.update().where(events.c.name == op.inline_literal('3x3 Relay of 3')).values({'description': op.inline_literal('')}))
    op.execute(events.update().where(events.c.name == op.inline_literal('2GEN')).values({'description': op.inline_literal('')}))
    op.execute(events.update().where(events.c.name == op.inline_literal('LSE')).values({'description': op.inline_literal('')}))
    op.execute(events.update().where(events.c.name == op.inline_literal('2BLD')).values({'description': op.inline_literal('')}))
    op.execute(events.update().where(events.c.name == op.inline_literal('Kilominx')).values({'description': op.inline_literal('')}))
    op.execute(events.update().where(events.c.name == op.inline_literal('3x3 Mirror Blocks/Bump')).values({'description': op.inline_literal('')}))
    op.execute(events.update().where(events.c.name == op.inline_literal('PLL Time Attack')).values({'description': op.inline_literal('')}))
    op.execute(events.update().where(events.c.name == op.inline_literal('F2L')).values({'description': op.inline_literal('')}))

