# ====== Song.py ======
from app.core.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Song(Base):
    __tablename__ = 'songs'
    __table_args__ = {'schema': 'vibesia_schema'}

    song_id = Column(Integer, primary_key=True, autoincrement=True)
    album_id = Column(Integer, ForeignKey('vibesia_schema.albums.album_id'), nullable=False)
    title = Column(String(150), nullable=False)
    duration = Column(Integer, nullable=False)
    track_number = Column(Integer)
    composer = Column(String(100))
    lyrics = Column(Text)
    audio_path = Column(String(255), nullable=False)
    explicit_content = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    album = relationship("Album", back_populates="songs")
    genre_associations = relationship("SongGenre", back_populates="song", cascade="all, delete-orphan")
    playlist_entries = relationship("PlaylistSong", back_populates="song", cascade="all, delete-orphan")
    playback_history_entries = relationship("PlaybackHistory", back_populates="song", cascade="all, delete-orphan")
