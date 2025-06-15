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
    new_position: int = Field(..., ge=0, description="The new position of the song (0-based)")

class SongInPlaylist(Song):
    position: int = Field(..., ge=0, description="Position of the song within the playlist")
    date_added: datetime

class PlaylistBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    status: str = Field("private", description="Visibility of the playlist: private, public, or shared")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed_statuses = {'private', 'public', 'shared'}
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

class PlaylistCreate(PlaylistBase):
    song_ids: Optional[List[int]] = Field([], description="List of song IDs to add to the playlist in order.")

class PlaylistUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    status: Optional[str] = Field(None, description="New visibility for the playlist")
    
    add_songs: Optional[List[PlaylistSongCreate]] = Field([], description="Songs to add to the playlist")
    remove_songs: Optional[List[int]] = Field([], description="List of song IDs to remove from the playlist")
    reorder_songs: Optional[List[SongReorder]] = Field([], description="List of songs to reorder")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed_statuses = {'private', 'public', 'shared'}
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

class PlaylistInDB(PlaylistBase):
    playlist_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
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
    song_count: int
    total_duration: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True