from sqlalchemy.orm import declarative_base

Base = declarative_base()

try:
    from shared.models.data_user import DataUser
    from shared.models.internal_user import InternalUser
except ImportError:
    # Esto evita errores circulares si los hubiera durante la inicialización
    pass