"""quitar_usuarios_unicos

Revision ID: 68def6c6b042
Revises: 589352e53f6f
Create Date: 2026-05-04 10:28:51.354871
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '68def6c6b042'
down_revision: Union[str, None] = '589352e53f6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 🔥 Evita error si el índice no existe
    op.execute("""
        DROP INDEX IF EXISTS ix_concentration_user_username;
    """)

    # Crear índice sin restricción UNIQUE
    op.create_index(
        op.f('ix_concentration_user_username'),
        'concentration_user',
        ['username'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    # 🔥 Evita error si no existe
    op.execute("""
        DROP INDEX IF EXISTS ix_concentration_user_username;
    """)

    # Restaurar índice como UNIQUE
    op.create_index(
        'ix_concentration_user_username',
        'concentration_user',
        ['username'],
        unique=True
    )