"""add owner_id to discount_codes

Revision ID: add_owner_discount
Revises: update_status_002
Create Date: 2025-11-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_owner_discount'
down_revision = 'update_status_002'
branch_labels = None
depends_on = None


def upgrade():
    # Check and add owner_id column if not exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('discount_codes')]
    
    if 'owner_id' not in columns:
        op.add_column('discount_codes', sa.Column('owner_id', sa.Integer(), nullable=True))
    
    # Check and add foreign key constraint if not exists
    foreign_keys = [fk['name'] for fk in inspector.get_foreign_keys('discount_codes')]
    if 'fk_discount_codes_owner_id' not in foreign_keys:
        op.create_foreign_key(
            'fk_discount_codes_owner_id',
            'discount_codes', 'users',
            ['owner_id'], ['user_id']
        )
    
    # Try to drop the old unique constraint on code if it exists
    try:
        op.execute("ALTER TABLE discount_codes DROP INDEX code")
    except:
        pass  # Constraint might not exist or have different name
    
    # Check and create new unique constraint on (owner_id, code) if not exists
    unique_constraints = [uc['name'] for uc in inspector.get_unique_constraints('discount_codes')]
    if 'uq_owner_code' not in unique_constraints:
        op.create_unique_constraint('uq_owner_code', 'discount_codes', ['owner_id', 'code'])
    
    # If you have existing data, you may need to set a default owner_id
    # op.execute("UPDATE discount_codes SET owner_id = 1 WHERE owner_id IS NULL")
    
    # Make owner_id not nullable after updating existing rows
    # op.alter_column('discount_codes', 'owner_id', nullable=False)


def downgrade():
    # Remove unique constraint
    op.drop_constraint('uq_owner_code', 'discount_codes', type_='unique')
    
    # Restore old unique constraint
    op.create_unique_constraint('code', 'discount_codes', ['code'])
    
    # Remove foreign key
    op.drop_constraint('fk_discount_codes_owner_id', 'discount_codes', type_='foreignkey')
    
    # Remove column
    op.drop_column('discount_codes', 'owner_id')

