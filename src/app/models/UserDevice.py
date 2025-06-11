# ====== UserDevice.py ======
from app.core.database import Base
from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class UserDevice(Base):
    __tablename__ = 'user_device'
    __table_args__ = {'schema': 'vibesia_schema'}


    user_id = Column(Integer, ForeignKey('vibesia_schema.users.user_id', ondelete="CASCADE"), primary_key=True)
    device_id = Column(Integer, ForeignKey('vibesia_schema.devices.device_id'), primary_key=True)
    registration_date = Column(Date, nullable=False, default=func.current_date())
    last_access = Column(DateTime, nullable=False, default=func.current_timestamp())
    last_reproduction_date = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="device_associations")
    device = relationship("Device", back_populates="user_associations")