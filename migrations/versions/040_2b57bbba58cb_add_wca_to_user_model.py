"""add wca to user model

Revision ID: 2b57bbba58cb
Revises: 5de7c9b4e68c
Create Date: 2020-04-03 13:59:21.877046

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2b57bbba58cb'
down_revision = '5de7c9b4e68c'
branch_labels = None
depends_on = None


def upgrade():

    # Schema migration, part 1
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reddit_id', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('reddit_token', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('wca_token', sa.String(length=64), nullable=True))

    # Data migration: takes a few steps...
    # Declare ORM table views. Note that the view contains old and new columns!        
    t_users = sa.Table(
        'users',
        sa.MetaData(),
        sa.Column('id', sa.String(32)),
        sa.Column('refresh_token', sa.VARCHAR(length=64)), # old column
        sa.Column('username', sa.String(length=64)),       # old column

        sa.Column('reddit_id', sa.String(length=64)),      # new column
        sa.Column('reddit_token', sa.String(length=64)),   # new column
        )

    # Use Alchemy's connection and transaction to noodle over the data.
    connection = op.get_bind()

    # Select all existing users that need migrating.
    results = connection.execute(sa.select([
        t_users.c.id,
        t_users.c.refresh_token,
        t_users.c.username,
        ])).fetchall()

    # Iterate over all selected data tuples.
    for id_, refresh_token, username in results:

        # Update the new columns
        # username gets copied into reddit_id, since at the time of this migration, all accounts were Reddit
        # refresh_token gets copied to reddit_token, since we now need to distinguish WCA and Reddit OAuth tokens
        connection.execute(t_users.update().where(t_users.c.id == id_).values({
            'reddit_id': username,
            'reddit_token': refresh_token
        }))

    # Schema migration, part 2
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('refresh_token')


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('refresh_token', sa.VARCHAR(length=64), autoincrement=False, nullable=True))
        batch_op.drop_column('wca_token')
        batch_op.drop_column('reddit_token')
        batch_op.drop_column('reddit_id')
