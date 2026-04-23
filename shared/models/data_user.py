from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from shared.db.base import Base
from shared.utils.utils import get_mexico_time

class DataUser(Base):
    __tablename__ = "data_users"

    id = Column(Integer, ForeignKey("internal_users.id"), primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_mexico_time)
    updated_at = Column(DateTime(timezone=True), onupdate=get_mexico_time, default=get_mexico_time)

    user = relationship("InternalUser", back_populates="data_user")
