from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

# --- Schemas para las Canciones (Dependencias que faltaban) ---
# Estos esquemas definen cómo se representa una canción en diferentes contextos.

class SongBase(BaseModel):
    """Schema base para una canción con sus datos esenciales."""
    title: str = Field(..., min_length=1, description="Título de la canción")
    artist_name: str = Field(..., min_length=1, description="Nombre del artista")
    duration_seconds: int = Field(..., gt=0, description="Duración en segundos")

class Song(SongBase):
    """Schema público para una canción, incluyendo su ID."""
    song_id: int

    class Config:
        from_attributes = True

# --- Schemas para la Asociación Canción-Playlist ---

class PlaylistSongCreate(BaseModel):
    """Schema para añadir una canción a una playlist."""
    song_id: int

class SongReorder(BaseModel):
    """Define la estructura para reordenar una canción dentro de una playlist."""
    song_id: int
    new_position: int = Field(..., ge=0, description="La nueva posición de la canción (basada en 0)")
    
class SongInPlaylist(Song):
    """
    Representa una canción dentro de una playlist, incluyendo su posición específica.
    Este schema enriquece los datos de la canción con su contexto en la playlist.
    """
    position: int = Field(..., ge=0, description="Posición de la canción en la playlist")


# --- Schemas para las Playlists (Corregidos y Refactorizados) ---

class PlaylistBase(BaseModel):
    """Schema base para una playlist con los campos comunes."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    status: str = Field("private", description="Visibilidad de la playlist: private, public, o shared")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Valida que el estado sea uno de los valores permitidos."""
        allowed_statuses = {'private', 'public', 'shared'}
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

class PlaylistCreate(PlaylistBase):
    """Schema para crear una nueva playlist. Opcionalmente se pueden añadir canciones iniciales."""
    # Al crear, se puede pasar una lista de IDs de canciones para poblarla inicialmente.
    # El orden en esta lista determinará su posición inicial.
    song_ids: Optional[List[int]] = Field([], description="Lista de IDs de canciones para añadir a la playlist en orden.")

class PlaylistUpdate(BaseModel):
    """
    Schema para actualizar una playlist existente.
    Permite modificar metadatos y gestionar las canciones en una sola operación.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    status: Optional[str] = Field(None, description="Nueva visibilidad de la playlist")
    
    # Operaciones sobre las canciones
    add_songs: Optional[List[PlaylistSongCreate]] = Field([], description="Canciones para añadir a la playlist")
    remove_songs: Optional[List[int]] = Field([], description="Lista de IDs de canciones para eliminar de la playlist")
    reorder_songs: Optional[List[SongReorder]] = Field([], description="Lista de canciones para cambiar de posición")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Valida el estado si se proporciona."""
        if v is not None:
            allowed_statuses = {'private', 'public', 'shared'}
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

class PlaylistInDB(PlaylistBase):
    """Schema que representa la playlist tal como está en la base de datos."""
    playlist_id: int
    user_id: int
    created_at: datetime  # Unificado desde creation_date y created_at
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Playlist(PlaylistInDB):
    """
    Schema completo de la playlist para ser devuelto por la API.
    Incluye la lista de canciones y metadatos calculados.
    """
    songs: List[SongInPlaylist] = []
    
    # Estos campos son calculados y no se almacenan directamente en la tabla de playlists
    song_count: int = Field(0, description="Número total de canciones en la playlist")
    total_duration: int = Field(0, description="Duración total de la playlist en segundos")

class PlaylistSummary(BaseModel):
    """Schema ligero para listar múltiples playlists de forma eficiente."""
    playlist_id: int
    name: str
    description: Optional[str] = None
    status: str
    song_count: int
    total_duration: int
    created_at: datetime # Consistente con PlaylistInDB
    updated_at: datetime
    
    class Config:
        from_attributes = True