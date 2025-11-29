"""Add paypal to payment_method enum

Revision ID: fa7076c38616
Revises: add_owner_discount
Create Date: 2025-11-29 19:20:48.568354

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa7076c38616'
down_revision = 'add_owner_discount'
branch_labels = None
depends_on = None


def upgrade():
    # MySQL/MariaDB: Add 'paypal' to payment_method enum
    op.execute("ALTER TABLE payments MODIFY COLUMN payment_method ENUM('credit_card', 'bank_transfer', 'momo', 'zalopay', 'vnpay', 'cash', 'paypal') NOT NULL")


def downgrade():
    # Rollback: Remove 'paypal' from payment_method enum
    op.execute("ALTER TABLE payments MODIFY COLUMN payment_method ENUM('credit_card', 'bank_transfer', 'momo', 'zalopay', 'vnpay', 'cash') NOT NULL")
