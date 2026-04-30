from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from shared.db.base import Base
from shared.utils.utils import get_mexico_time

class LogRequests(Base):
    __tablename__ = "log_requests"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("internal_users.id"), index=True, nullable=False)
    path_requests = Column(String, nullable=False)
    type_requests = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_mexico_time)
    
    user = relationship("InternalUser", back_populates="log_requests")