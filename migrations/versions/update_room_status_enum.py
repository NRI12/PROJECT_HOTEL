"""Update room status enum: unavailable -> occupied

Revision ID: update_status_002
Revises: remove_quantity_001
Create Date: 2025-01-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_status_002'
down_revision = 'remove_quantity_001'
branch_labels = None
depends_on = None


def upgrade():
    # MySQL/MariaDB: Modify ENUM to change 'unavailable' to 'occupied'
    op.execute("ALTER TABLE rooms MODIFY COLUMN status ENUM('available', 'occupied', 'maintenance') DEFAULT 'available'")


def downgrade():
    # Rollback: change 'occupied' back to 'unavailable'
    op.execute("ALTER TABLE rooms MODIFY COLUMN status ENUM('available', 'unavailable', 'maintenance') DEFAULT 'available'")

