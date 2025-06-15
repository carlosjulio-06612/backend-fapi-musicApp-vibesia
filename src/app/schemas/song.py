from pydantic import BaseModel, Field
from typing import Optional

class SongBase(BaseModel):
    title: str
    duration: int
    album_id: int

class SongCreate(SongBase):
    pass

class SongUpdate(SongBase):
    pass

class SongDetail(BaseModel):
    song_id: int
    title: str
    artist_name: str
    duration: int
    lyrics: Optional[str] = None
    explicit_content: bool = False

    class Config:
        from_attributes = True