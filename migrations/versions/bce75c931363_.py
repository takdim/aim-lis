"""safe minimal migration

Revision ID: bce75c931363
Revises: 8de3c81c3c0d
Create Date: 2026-03-15 23:35:47.612721
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "bce75c931363"
down_revision = "8de3c81c3c0d"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS holiday (
            holiday_id INT AUTO_INCREMENT PRIMARY KEY,
            holiday_date DATE NOT NULL,
            holiday_name VARCHAR(100) NOT NULL,
            note TEXT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            INDEX ix_holiday_holiday_date (holiday_date)
        )
        """
    )
    op.execute(
        """
        ALTER TABLE user_group ADD COLUMN privileges TEXT NULL
        """
    )


def downgrade():
    op.execute("ALTER TABLE user_group DROP COLUMN privileges")
    op.execute("DROP TABLE IF EXISTS holiday")
