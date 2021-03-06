"""add weekly gift code confirmation data model

Revision ID: 74b025612a81
Revises: 503d27d0a21a
Create Date: 2020-10-13 18:35:00.708866

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74b025612a81'
down_revision = '503d27d0a21a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('scs_gift_codes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('gift_code', sa.String(length=32), nullable=True),
    sa.Column('used', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('weekly_code_recipient_confirm_deny',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('comp_id', sa.Integer(), nullable=True),
    sa.Column('gift_code_id', sa.Integer(), nullable=True),
    sa.Column('confirm_code', sa.String(length=36), nullable=True),
    sa.Column('deny_code', sa.String(length=36), nullable=True),
    sa.Column('resolution', sa.Enum('pending', 'confirmed', 'denied', name='resolution'), nullable=True),
    sa.ForeignKeyConstraint(['comp_id'], ['competitions.id'], ),
    sa.ForeignKeyConstraint(['gift_code_id'], ['scs_gift_codes.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('weekly_code_recipient_confirm_deny', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_weekly_code_recipient_confirm_deny_comp_id'), ['comp_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_weekly_code_recipient_confirm_deny_gift_code_id'), ['gift_code_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_weekly_code_recipient_confirm_deny_user_id'), ['user_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('weekly_code_recipient_confirm_deny', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_weekly_code_recipient_confirm_deny_user_id'))
        batch_op.drop_index(batch_op.f('ix_weekly_code_recipient_confirm_deny_gift_code_id'))
        batch_op.drop_index(batch_op.f('ix_weekly_code_recipient_confirm_deny_comp_id'))

    op.drop_table('weekly_code_recipient_confirm_deny')
    op.drop_table('scs_gift_codes')
    # ### end Alembic commands ###
