from app.core.database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, CheckConstraint # <--- Import CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Artist(Base):
    __tablename__ = 'artists'
    __table_args__ = (
        CheckConstraint(
            "artist_type IN ('soloist', 'band', 'collective', 'duo', 'orchestra')",
            name='artists_artist_type_check'
        ),
        {'schema': 'vibesia_schema'}
    )

    artist_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    country = Column(String(50))
    formation_year = Column(Integer)
    biography = Column(Text)
    artist_type = Column(String(30), nullable=False)
    popularity = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationship
    albums = relationship("Album", back_populates="artist", cascade="all, delete-orphan")