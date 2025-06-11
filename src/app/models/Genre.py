# ====== Genre.py ======
from app.core.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date, DateTime, Boolean, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

class Genre(Base):
    __tablename__ = 'genres'
    __table_args__ = {'schema': 'vibesia_schema'}

    genre_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)

    # Relationships
    song_associations = relationship("SongGenre", back_populates="genre")
