"""Add dino cube

Revision ID: bbeebbee1234
Revises: 01c4eb2444b9
Create Date: 2019-08-20 12:23:00.123969

"""
from alembic import op
from cubersio.persistence.models import EventFormat, Event

# revision identifiers, used by Alembic.
revision = 'bbeebbee1234'
down_revision = '01c4eb2444b9'
branch_labels = None
depends_on = None

def upgrade():
    op.bulk_insert(
        Event.__table__,
        [
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': 'Dino Cube' },
        ]
    )

def downgrade():
    pass
