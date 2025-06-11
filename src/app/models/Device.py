# ====== Device.py ======
from app.core.database import Base
from sqlalchemy import Column, Integer, String, CheckConstraint
from sqlalchemy.orm import relationship

class Device(Base):
    __tablename__ = 'devices'
    __table_args__ = (
        {'schema': 'vibesia_schema'}
    )
    device_id = Column(Integer, primary_key=True, autoincrement=True)
    device_type = Column(String(30), nullable=False)
    operating_system = Column(String(50))
    
    # Relationships
    user_associations = relationship("UserDevice", back_populates="device", cascade="all, delete-orphan")
    playback_history_entries = relationship("PlaybackHistory", back_populates="device")