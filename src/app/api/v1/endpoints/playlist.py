# --- START OF FILE playlist.py (CORRECTED) ---

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud
from app import models
from app.schemas import playlist as schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.PlaylistSummary], tags=["Playlists"])
def get_user_playlists(
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    db = Session.object_session(current_user)
    
    playlists_orm = crud.playlist.get_by_user(
        db=db, user_id=current_user.user_id, skip=skip, limit=limit
    )
    
    results = []
    for p in playlists_orm:
        stats = crud.playlist.get_playlist_stats(
            db=db, playlist_id=p.playlist_id, user_id=current_user.user_id
        )
        summary = schemas.PlaylistSummary(
            playlist_id=p.playlist_id,
            name=p.name,
            description=p.description,
            status=p.status,
            song_count=stats.get("song_count", 0) if stats else 0,
            total_duration=stats.get("total_duration", 0) if stats else 0,
            created_at=p.created_at,
            updated_at=p.updated_at
        )
        results.append(summary)
    return results


@router.post("/", response_model=schemas.Playlist, status_code=status.HTTP_201_CREATED, tags=["Playlists"])
def create_user_playlist(
    playlist_in: schemas.PlaylistCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    db = Session.object_session(current_user)
    
    playlist = crud.playlist.create_for_user(
        db=db, obj_in=playlist_in, user_id=current_user.user_id
    )
    if not playlist:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create playlist."
        )
    return playlist

@router.get("/{playlist_id}", response_model=schemas.Playlist, tags=["Playlists"])
def get_user_playlist(
    playlist_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    db = Session.object_session(current_user)

    playlist = crud.playlist.get_playlist_with_songs(
        db=db, playlist_id=playlist_id, user_id=current_user.user_id
    )
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found or does not belong to user."
        )
    return playlist

@router.put("/{playlist_id}", response_model=schemas.Playlist, tags=["Playlists"])
def update_user_playlist(
    playlist_id: int,
    playlist_in: schemas.PlaylistUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    db = Session.object_session(current_user)
    
    playlist = crud.playlist.update_user_playlist(
        db=db,
        playlist_id=playlist_id,
        user_id=current_user.user_id,
        obj_in=playlist_in
    )
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found or does not belong to user."
        )
    return playlist

@router.delete("/{playlist_id}", response_model=schemas.Playlist, tags=["Playlists"])
def delete_user_playlist(
    playlist_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    db = Session.object_session(current_user)
    
    playlist = crud.playlist.delete_user_playlist(
        db=db,
        playlist_id=playlist_id,
        user_id=current_user.user_id
    )
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found or does not belong to user."
        )
    return playlist

@router.get("/info/count", response_model=int, tags=["Playlists"])
def get_user_playlist_count(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    db = Session.object_session(current_user)
    
    return crud.playlist.count_by_user(
        db=db, 
        user_id=current_user.user_id
    )