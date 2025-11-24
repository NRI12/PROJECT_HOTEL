"""Remove quantity column from rooms table

Revision ID: remove_quantity_001
Revises: 015e0e10f7d6
Create Date: 2025-01-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'remove_quantity_001'
down_revision = '015e0e10f7d6'
branch_labels = None
depends_on = None


def upgrade():
    # Remove quantity column from rooms table
    op.drop_column('rooms', 'quantity')


def downgrade():
    # Add back quantity column if needed to rollback
    op.add_column('rooms', sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'))

