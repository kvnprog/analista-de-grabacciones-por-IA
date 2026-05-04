from sqlalchemy import Column, DateTime, Integer, String
from shared.db.base import Base
from shared.utils.utils import get_mexico_time

class ConcentrationUser(Base):
    __tablename__ = "concentration_user"

    id = Column(Integer, primary_key=True, index=True)
    id_employed = Column(Integer, index=True, nullable=True)
    username = Column(String, unique=False, index=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    client = Column(String, nullable=False)
    plataform = Column(String, nullable=False)
    role = Column(String, nullable=False)
    status = Column(Integer, default=1, nullable=False)
    id_user_create = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_mexico_time)
    updated_at = Column(DateTime(timezone=True), onupdate=get_mexico_time, default=get_mexico_time)