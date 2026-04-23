"""add guestbook_winner table

Revision ID: c1e2f4a3b2c1
Revises: bce75c931363
Create Date: 2026-04-13 07:52:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c1e2f4a3b2c1"
down_revision = "bce75c931363"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS guestbook_winner (
            winner_id INT AUTO_INCREMENT PRIMARY KEY,
            visitor_id INT NULL,
            member_name VARCHAR(255) NOT NULL,
            member_id VARCHAR(20) NULL,
            institution VARCHAR(100) NULL,
            period_month INT NOT NULL,
            period_year INT NOT NULL,
            visit_count INT DEFAULT 0,
            set_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            INDEX ix_guestbook_winner_visitor_id (visitor_id)
        )
        """
    )


def downgrade():
    op.execute("DROP TABLE IF EXISTS guestbook_winner")
