from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class SongBase(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the song")
    artist_name: str = Field(..., min_length=1, description="Name of the artist")
    duration: int = Field(..., gt=0, description="Duration in seconds")

class Song(SongBase):
    song_id: int
    lyrics: Optional[str] = Field(None, description="A snippet of the song's lyrics")

    class Config:
        from_attributes = True

class PlaylistSongCreate(BaseModel):
    song_id: int

class SongReorder(BaseModel):
    song_id: int
    new_position: int = Field(..., ge=1, description="The new position of the song (1-based)")

class SongInPlaylist(Song):
    position: int = Field(..., ge=1, description="Position of the song within the playlist")
    date_added: datetime

class PlaylistBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    status: str = Field("private", description="Visibility of the playlist: private or public")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed_statuses = {'private', 'public'}
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

class PlaylistCreate(PlaylistBase):
    pass

class PlaylistUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    status: Optional[str] = Field(None, description="New visibility for the playlist")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed_statuses = {'private', 'public'}
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

class PlaylistInDB(PlaylistBase):
    playlist_id: int
    user_id: int
    
    class Config:
        from_attributes = True

class Playlist(PlaylistInDB):
    songs: List[SongInPlaylist] = []
    song_count: int = Field(0, description="Total number of songs in the playlist")
    total_duration: int = Field(0, description="Total duration of the playlist in seconds")

class PlaylistSummary(BaseModel):
    playlist_id: int
    name: str
    description: Optional[str] = None
    status: str
    song_count: Optional[int] = None
    total_duration: Optional[float] = None
    
    class Config:
        from_attributes = True