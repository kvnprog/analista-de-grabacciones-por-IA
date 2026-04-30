from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from shared.db.base import Base
from shared.models.enums import InternalUserRole
from shared.utils.utils import get_mexico_time

class InternalUser(Base):
    __tablename__ = "internal_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(InternalUserRole), default=InternalUserRole.administrativo, nullable=False)
    campaign_id = Column(Integer, ForeignKey("internal_campaign.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_mexico_time)
    updated_at = Column(DateTime(timezone=True), onupdate=get_mexico_time, default=get_mexico_time)
    status = Column(Integer, default=1, nullable=False)
    id_user_create = Column(Integer, default=0, nullable=False)

    data_user = relationship("DataUser", back_populates="user", uselist=False)
    campaign = relationship("InternalCampaign", back_populates="users")
    log_session = relationship("LogSessions", back_populates="user")
    log_requests = relationship("LogRequests", back_populates="user")