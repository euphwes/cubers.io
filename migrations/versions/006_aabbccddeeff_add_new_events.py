"""Add new events

Revision ID: aabbccddeeff
Revises: a929c366aeef
Create Date: 2018-10-26 15:41:00.257969

"""
from alembic import op
import sqlalchemy as sa
from app.persistence.models import EventFormat, Event

# revision identifiers, used by Alembic.
revision = 'aabbccddeeff'
down_revision = 'a929c366aeef'
branch_labels = None
depends_on = None

def upgrade():
    op.bulk_insert(
        Event.__table__,
        [
            {'totalSolves': 3, 'eventFormat': EventFormat.Bo3, 'name': '2BLD'      },
            {'totalSolves': 3, 'eventFormat': EventFormat.Bo3, 'name': '4BLD'      },
            {'totalSolves': 3, 'eventFormat': EventFormat.Bo3, 'name': '5BLD'      },
            {'totalSolves': 5, 'eventFormat': EventFormat.Ao5, 'name': 'Redi Cube' },
        ]
    )

def downgrade():
    pass
