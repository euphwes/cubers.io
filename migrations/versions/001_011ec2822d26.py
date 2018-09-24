"""initial

Revision ID: 011ec2822d26
Revises: 
Create Date: 2018-08-29 20:49:39.499554

"""
from alembic import op
import sqlalchemy as sa
from app.persistence.models import EventFormat

# revision identifiers, used by Alembic.
revision = '011ec2822d26'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('competitions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=128), nullable=True),
    sa.Column('reddit_thread_id', sa.String(length=10), nullable=True),
    sa.Column('start_timestamp', sa.DateTime(timezone=True), nullable=True),
    sa.Column('end_timestamp', sa.DateTime(timezone=True), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('userPointResults', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('competitions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_competitions_reddit_thread_id'), ['reddit_thread_id'], unique=True)
        batch_op.create_index(batch_op.f('ix_competitions_title'), ['title'], unique=True)

    event_table = op.create_table('events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('totalSolves', sa.Integer(), nullable=True),
    sa.Column('eventFormat', sa.Enum('Ao5', 'Mo3', 'Bo3', 'Bo1', name='eventFormat'), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_events_name'), ['name'], unique=True)

    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('wca_id', sa.String(length=10), nullable=True),
    sa.Column('refresh_token', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

    op.create_table('competition_event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('competition_id', sa.Integer(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['competition_id'], ['competitions.id'], ),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('scrambles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('scramble', sa.Text(), nullable=True),
    sa.Column('competition_event_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['competition_event_id'], ['competition_event.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_event_results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('comp_event_id', sa.Integer(), nullable=True),
    sa.Column('single', sa.String(length=10), nullable=True),
    sa.Column('average', sa.String(length=10), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['comp_event_id'], ['competition_event.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_solves',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time', sa.Integer(), nullable=True),
    sa.Column('is_dnf', sa.Boolean(), nullable=True),
    sa.Column('is_plus_two', sa.Boolean(), nullable=True),
    sa.Column('scramble_id', sa.Integer(), nullable=True),
    sa.Column('user_event_results_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['scramble_id'], ['scrambles.id'], ),
    sa.ForeignKeyConstraint(['user_event_results_id'], ['user_event_results.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###

    op.bulk_insert(
        event_table,
        [
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': '3x3'                   },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': '2x2'                   },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': '4x4'                   },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': '5x5'                   },
            {'totalSolves': 3, 'eventFormat': EventFormat.Mo3, 'name': '6x6'                   },
            {'totalSolves': 3, 'eventFormat': EventFormat.Mo3, 'name': '7x7'                   },
            {'totalSolves': 3, 'eventFormat': EventFormat.Bo3, 'name': '3BLD'                  },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': 'Square-1'              },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': 'Clock'                 },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': '3x3OH'                 },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': 'Pyraminx'              },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': 'Megaminx'              },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': 'Kilominx'              },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': 'Skewb'                 },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': '2GEN'                  },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': 'F2L'                   },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': 'LSE'                   },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': 'COLL'                  },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': '3x3 Mirror Blocks/Bump'},
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': '4x4 OH'                },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': '3x3x4'                 },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': '3x3x5'                 },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': '3x3x2'                 },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': 'Void Cube'             },
            {'totalSolves': 1, 'eventFormat': EventFormat.Bo1, 'name': '2-3-4 Relay'           },
            {'totalSolves': 3, 'eventFormat': EventFormat.Mo3, 'name': 'FMC'                   },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': '3x3 With Feet'         },
            {'totalSolves': 1, 'eventFormat': EventFormat.Bo1, 'name': '3x3 Relay of 3'        },
            {'totalSolves': 1, 'eventFormat': EventFormat.Bo1, 'name': 'PLL Time Attack'       },
        ]
    )

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_solves')
    op.drop_table('user_event_results')
    op.drop_table('scrambles')
    op.drop_table('competition_event')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))

    op.drop_table('users')
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_events_name'))

    op.drop_table('events')
    with op.batch_alter_table('competitions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_competitions_title'))
        batch_op.drop_index(batch_op.f('ix_competitions_reddit_thread_id'))

    op.drop_table('competitions')
    # ### end Alembic commands ###