"""add_trigger_usuarios_to_usuarios_ctn

Revision ID: 589352e53f6f
Revises: 1c89cb655f49
Create Date: 2026-04-30 16:57:08.628931
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '589352e53f6f'
down_revision: Union[str, None] = '1c89cb655f49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Creamos o reemplazamos la función
    op.execute("""
        CREATE OR REPLACE FUNCTION funcion_replicar_insert()
        RETURNS TRIGGER AS $$
        DECLARE 
            v_username VARCHAR;
            v_client VARCHAR;
            v_role VARCHAR;
            v_id_user_create INT;
            v_campaign_id INT;
        BEGIN
            SELECT username, id_user_create, campaign_id, "role"
            INTO v_username, v_id_user_create, v_campaign_id, v_role
            FROM public.internal_users 
            WHERE id = NEW.id;

            SELECT name INTO v_client 
            FROM public.internal_campaign 
            WHERE id = v_campaign_id;

            INSERT INTO public.concentration_user
            (id_employed, username, "password", "name", client, plataform, "role", status, id_user_create, created_at)
            VALUES(
                NEW.id, 
                v_username, 
                '********', 
                CONCAT(NEW.name, ' ', NEW.last_name),
                v_client, 
                'MCA-Admin', 
                v_role, 
                1, 
                v_id_user_create, 
                NOW()
            );
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # 2. 🔥 IMPORTANTE: eliminamos el trigger si ya existe
    op.execute("""
        DROP TRIGGER IF EXISTS tr_despues_de_insertar_usuario ON public.data_users;
    """)

    # 3. Creamos el trigger
    op.execute("""
        CREATE TRIGGER tr_despues_de_insertar_usuario
        AFTER INSERT ON public.data_users
        FOR EACH ROW
        EXECUTE FUNCTION funcion_replicar_insert();
    """)


def downgrade():
    op.execute("""
        DROP TRIGGER IF EXISTS tr_despues_de_insertar_usuario ON public.data_users;
    """)
    op.execute("""
        DROP FUNCTION IF EXISTS funcion_replicar_insert();
    """)