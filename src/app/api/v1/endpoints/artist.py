# ====== app/api/v1/endpoints/artist.py (update) ======
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models
from app.schemas import artist as schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Artist], tags=["Artists"])
def read_artists(
    db: Session = Depends(deps.get_db_session),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Read artists - available to all authenticated users."""
    artists = crud.artist.get_multi(db, skip=skip, limit=limit)
    return artists

@router.post("/", response_model=schemas.Artist, status_code=status.HTTP_201_CREATED, tags=["Artists"])
def create_artist(
    artist_in: schemas.ArtistCreate,
    # Use the new dependency to ensure only admins can access this
    current_user: models.User = Depends(deps.get_current_admin_user),
) -> Any:
    """Create artist - only for administrators."""
    db = Session.object_session(current_user)
    
    artist = crud.artist.get_by_name(db, name=artist_in.name)
    if artist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An artist with this name already exists.",
        )
    artist = crud.artist.create(db=db, obj_in=artist_in)
    return artist

@router.get("/{artist_id}", response_model=schemas.Artist, tags=["Artists"])
def read_artist_by_id(
    artist_id: int,
    db: Session = Depends(deps.get_db_session),
) -> Any:
    """Read artist by ID - available to everyone."""
    artist = crud.artist.get(db=db, id=artist_id)
    if not artist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artist not found")
    return artist

@router.put("/{artist_id}", response_model=schemas.Artist, tags=["Artists"])
def update_artist(
    artist_id: int,
    artist_in: schemas.ArtistUpdate,
    # Protect with admin dependency
    current_user: models.User = Depends(deps.get_current_admin_user),
) -> Any:
    """Update artist - only for administrators."""
    db = Session.object_session(current_user)
    
    artist = crud.artist.get(db=db, id=artist_id)
    if not artist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artist not found")
    
    artist = crud.artist.update(db=db, db_obj=artist, obj_in=artist_in)
    return artist

@router.delete("/{artist_id}", response_model=schemas.Artist, tags=["Artists"])
def delete_artist(
    artist_id: int,
    # Protect with admin dependency
    current_user: models.User = Depends(deps.get_current_admin_user),
) -> Any:
    """Delete artist - only for administrators."""
    db = Session.object_session(current_user)
    
    artist = crud.artist.get(db=db, id=artist_id)
    if not artist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artist not found")
        
    artist = crud.artist.remove(db=db, id=artist_id)
    return artist