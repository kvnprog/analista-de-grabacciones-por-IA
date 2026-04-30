from sqlalchemy.orm import declarative_base

Base = declarative_base()

try:
    from shared.models.data_user import DataUser
    from shared.models.internal_user import InternalUser
    from shared.models.internal_campaign import InternalCampaign
    from shared.models.log_sessions import LogSessions
    from shared.models.log_requests import LogRequests
    from shared.models.concentration_user import ConcentrationUser
except ImportError:
    # Esto evita errores circulares si los hubiera durante la inicialización
    pass