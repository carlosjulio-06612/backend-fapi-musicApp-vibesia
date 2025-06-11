# ====== PlaylistSong.py ======
from app.core.database import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class PlaylistSong(Base):
    __tablename__ = 'playlist_songs'
    __table_args__ = {'schema': 'vibesia_schema'}
    
    playlist_id = Column(Integer, ForeignKey('vibesia_schema.playlists.playlist_id'), primary_key=True)
    song_id = Column(Integer, ForeignKey('vibesia_schema.songs.song_id'), primary_key=True)
    position = Column(Integer, nullable=False)
    date_added = Column(DateTime, nullable=False, default=func.current_timestamp())
    
    # Relationships 
    playlist = relationship("Playlist", back_populates="song_entries")
    song = relationship("Song", back_populates="playlist_entries")