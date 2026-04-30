from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from shared.db.base import Base
from shared.utils.utils import get_mexico_time

class LogSessions(Base):
    __tablename__ = "log_sessions"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("internal_users.id"), index=True, nullable=False)
    login_at = Column(DateTime(timezone=True), default=get_mexico_time)
    logout_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("InternalUser", back_populates="log_session")