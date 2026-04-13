"""add period_type to guestbook_winner

Revision ID: f3e7a8d9c4b2
Revises: e90f256c5eeb
Create Date: 2026-04-13 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3e7a8d9c4b2'
down_revision = 'e90f256c5eeb'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE guestbook_winner 
        ADD COLUMN period_type ENUM('awal', 'akhir') NOT NULL DEFAULT 'awal' AFTER period_year
        """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE guestbook_winner 
        DROP COLUMN period_type
        """
    )
