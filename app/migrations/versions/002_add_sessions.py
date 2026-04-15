"""Add sessions and refresh tokens tables

Revision ID: 002_add_sessions
Revises: 001_initial
Create Date: 2024-04-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '002_add_sessions'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Sessions table for tracking active user sessions
    op.create_table(
        'sessions',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('device_info', sa.String(255)),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('ix_sessions_expires_at', 'sessions', ['expires_at'])

    # Refresh tokens table for OAuth-like flow
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('is_revoked', sa.Boolean, default=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('ix_refresh_tokens_expires_at', 'refresh_tokens', ['expires_at'])


def downgrade() -> None:
    op.drop_table('refresh_tokens')
    op.drop_table('sessions')