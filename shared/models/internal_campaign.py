from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from shared.db.base import Base
from shared.utils.utils import get_mexico_time

class InternalCampaign(Base):
    __tablename__ = "internal_campaign"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), default=get_mexico_time)
    updated_at = Column(DateTime(timezone=True), onupdate=get_mexico_time, default=get_mexico_time)
    
    users = relationship("InternalUser", back_populates="campaign")
