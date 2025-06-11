# ====== Playlist.py ======
from app.core.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Playlist(Base):
    __tablename__ = 'playlists'
    __table_args__ = (
        UniqueConstraint('name', 'user_id', name='uk_playlist_user_name'),
        {'schema': 'vibesia_schema'}
    )

    playlist_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('vibesia_schema.users.user_id', ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    creation_date = Column(DateTime, nullable=False, default=func.current_timestamp())
    status = Column(String(20), nullable=False, default='private')
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    creator = relationship("User", back_populates="created_playlists")
    song_entries = relationship("PlaylistSong", back_populates="playlist", cascade="all, delete-orphan")