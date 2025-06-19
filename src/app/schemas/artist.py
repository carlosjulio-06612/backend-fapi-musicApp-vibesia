import enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ArtistTypeEnum(str, enum.Enum):
    BAND = "band"
    SOLOIST = "soloist"
    COLLECTIVE = "collective"
    DUO = "duo"
    ORCHESTRA = "orchestra"

# Shared properties for an artist
class ArtistBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    country: Optional[str] = Field(None, max_length=50)
    formation_year: Optional[int] = Field(None, gt=1700, lt=datetime.now().year + 1)
    biography: Optional[str] = None
    artist_type: ArtistTypeEnum

# Properties to receive on item creation
class ArtistCreate(ArtistBase):
    pass

# Properties to receive on item update
class ArtistUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    country: Optional[str] = Field(None, max_length=50)
    formation_year: Optional[int] = Field(None, gt=1700, lt=datetime.now().year + 1)
    biography: Optional[str] = None
    artist_type: Optional[ArtistTypeEnum] = None
    popularity: Optional[int] = Field(None, ge=1, le=100)

# Properties shared by models stored in DB
class ArtistInDBBase(ArtistBase):
    artist_id: int
    popularity: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Properties to return to the client (public-facing)
class Artist(ArtistInDBBase):
    pass

# Properties stored in DB
class ArtistInDB(ArtistInDBBase):
    pass