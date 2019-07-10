"""lengthen desc

Revision ID: 50644721ac4e
Revises: adad00000000
Create Date: 2019-06-17 17:05:04.276404

"""
from alembic import op
import sqlalchemy as sa

# NOTE: this migration has been skipped.
# ---------------------------------------
# The ALTER COLUMN SQL statement generated seems to have table-lock issues
# and I'm not enough of a database wizard to work around it the right way.
# The modification from 128 -> 2048 characters was manually added in
# revision 001, and the the subsequent revision 030 was edited to follow 028,
# effectively skipping this revision.

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
