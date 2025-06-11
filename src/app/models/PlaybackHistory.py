# ====== PlaybackHistory.py ======
from app.core.database import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class PlaybackHistory(Base):
    __tablename__ = 'playback_history'
    __table_args__ = (
        UniqueConstraint('user_id', 'song_id', 'playback_date',
                        name='playback_unique_user_song_time'),
        {'schema': 'vibesia_schema'}
    )

    playback_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('vibesia_schema.users.user_id', ondelete="CASCADE"), nullable=False)
    song_id = Column(Integer, ForeignKey('vibesia_schema.songs.song_id'), nullable=False)
    device_id = Column(Integer, ForeignKey('vibesia_schema.devices.device_id'), nullable=False)
    playback_date = Column(DateTime, nullable=False, default=func.current_timestamp())
    completed = Column(Boolean, nullable=False, default=False)
    rating = Column(Integer)

    # Relationships
    user = relationship("User", back_populates="playback_history_entries")
    song = relationship("Song", back_populates="playback_history_entries")
    device = relationship("Device", back_populates="playback_history_entries")