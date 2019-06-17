"""lengthen desc

Revision ID: 50644721ac4e
Revises: adad00000000
Create Date: 2019-06-17 17:05:04.276404

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50644721ac4e'
down_revision = 'adad00000000'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('events', 'description',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(length=2048),
               existing_nullable=False)


def downgrade():
    op.alter_column('events', 'description',
               existing_type=sa.String(length=2048),
               type_=sa.VARCHAR(length=128),
               existing_nullable=False)
