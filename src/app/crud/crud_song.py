from typing import List, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models import Song, Album, Artist
from app.schemas.song import SongCreate, SongUpdate


class CRUDSong(CRUDBase[Song, SongCreate, SongUpdate]):
    def get_multi_with_details(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Any]:
        query = (
            select(
                Song.song_id,
                Song.title,
                Song.duration,
                Song.lyrics,
                Song.explicit_content,
                Artist.name.label("artist_name"),
            )
            .join(Album, Song.album_id == Album.album_id)
            .join(Artist, Album.artist_id == Artist.artist_id)
            .order_by(Artist.name, Album.title, Song.track_number)
            .offset(skip)
            .limit(limit)
        )
        result = db.execute(query).all()
        return [dict(row._mapping) for row in result]


song = CRUDSong(Song)