# ====== Album.py ======
from app.core.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Album(Base):
    __tablename__ = 'albums'
    __table_args__ = (
        CheckConstraint("release_year BETWEEN 1900 AND EXTRACT(YEAR FROM CURRENT_DATE)",
                       name='chk_release_year_valid'),
        {'schema': 'vibesia_schema'}
    )
    
    album_id = Column(Integer, primary_key=True, autoincrement=True)
    artist_id = Column(Integer, ForeignKey('vibesia_schema.artists.artist_id'), nullable=False)
    title = Column(String(150), nullable=False)
    release_year = Column(Integer)
    record_label = Column(String(100))
    album_type = Column(String(30), nullable=False) 
    cover_image = Column(String(255))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp()) 

    # Relationships
    artist = relationship("Artist", back_populates="albums")
    songs = relationship("Song", back_populates="album", cascade="all, delete-orphan")