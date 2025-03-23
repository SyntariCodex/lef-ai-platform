"""
Create user and permission tables
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create enum types
    op.execute("CREATE TYPE user_role AS ENUM ('admin', 'manager', 'user', 'viewer')")
    op.execute("CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended', 'deleted')")

    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=False, default=False),
        sa.Column('approval_level', sa.Integer(), nullable=False, default=1),
        sa.Column('parent_id', postgresql.UUID(), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['permissions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', postgresql.ENUM('admin', 'manager', 'user', 'viewer', name='user_role'), nullable=False),
        sa.Column('status', postgresql.ENUM('active', 'inactive', 'suspended', 'deleted', name='user_status'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('last_activity', sa.DateTime(), nullable=True),
        sa.Column('last_password_change', sa.DateTime(), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, default=False),
        sa.Column('two_factor_secret', sa.String(), nullable=True),
        sa.Column('password_reset_token', sa.String(), nullable=True),
        sa.Column('password_reset_expires', sa.DateTime(), nullable=True),
        sa.Column('api_keys', postgresql.JSON(), nullable=True),
        sa.Column('session_tokens', postgresql.JSON(), nullable=True),
        sa.Column('audit_log', postgresql.JSON(), nullable=True),
        sa.Column('custom_fields', postgresql.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )

    # Create user_permissions association table
    op.create_table(
        'user_permissions',
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('permission', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'permission')
    )

    # Create indexes
    op.create_index('ix_permissions_category', 'permissions', ['category'])
    op.create_index('ix_permissions_parent_id', 'permissions', ['parent_id'])
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_status', 'users', ['status'])
    op.create_index('ix_user_permissions_user_id', 'user_permissions', ['user_id'])

def downgrade():
    # Drop indexes
    op.drop_index('ix_user_permissions_user_id')
    op.drop_index('ix_users_status')
    op.drop_index('ix_users_username')
    op.drop_index('ix_users_email')
    op.drop_index('ix_permissions_parent_id')
    op.drop_index('ix_permissions_category')

    # Drop tables
    op.drop_table('user_permissions')
    op.drop_table('users')
    op.drop_table('permissions')

    # Drop enum types
    op.execute('DROP TYPE user_status')
    op.execute('DROP TYPE user_role') 