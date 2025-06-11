# ====== SongGenre.py ======
from app.core.database import Base
from sqlalchemy import Column, Integer, ForeignKey 
from sqlalchemy.orm import relationship

class SongGenre(Base): 
    __tablename__ = 'song_genres'
    __table_args__ = {'schema': 'vibesia_schema'} 
    
    song_id = Column(Integer, ForeignKey('vibesia_schema.songs.song_id'), primary_key=True)
    genre_id = Column(Integer, ForeignKey('vibesia_schema.genres.genre_id'), primary_key=True)
    
    # Relationships
    song = relationship("Song", back_populates="genre_associations")
    genre = relationship("Genre", back_populates="song_associations") 

