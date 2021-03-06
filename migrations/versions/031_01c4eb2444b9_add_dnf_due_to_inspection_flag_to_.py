"""Add DNF-due-to-inspection flag to UserSolve

Revision ID: 01c4eb2444b9
Revises: aaaa0000ffff
Create Date: 2019-07-18 15:39:01.972553

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01c4eb2444b9'
down_revision = 'aaaa0000ffff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_solves', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_inspection_dnf', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_solves', schema=None) as batch_op:
        batch_op.drop_column('is_inspection_dnf')

    # ### end Alembic commands ###
