# ====== User.py (Corrected Version) ======
from app.core.database import Base
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'vibesia_schema'}

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    registration_date = Column(Date, nullable=False, default=func.current_date())
    preferences = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    password_changed_at = Column(DateTime(timezone=True), nullable=True)

    @validates('email')
    def validate_email_spaces(self, key, address):
        """Asegura que el email no contenga espacios antes de asignarlo al modelo."""
        if ' ' in address:
            raise ValueError("El correo electrónico no debe contener espacios")
        return address.lower()
    
    created_playlists = relationship(
        "Playlist",
        back_populates="creator",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    playback_history_entries = relationship(
        "PlaybackHistory",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    device_associations = relationship(
        "UserDevice",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )