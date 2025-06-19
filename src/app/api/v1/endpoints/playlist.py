from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app import models
from app.schemas import playlist as schemas
from app.api import deps
from pydantic import BaseModel

router = APIRouter()

class MessageResponse(BaseModel):
    message: str

@router.get("/", response_model=List[schemas.PlaylistSummary], tags=["Playlists"])
def get_user_playlists(
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    db = Session.object_session(current_user)
    return crud.playlist.get_summaries_by_user(
        db=db, user_id=current_user.user_id, skip=skip, limit=limit
    )


@router.post("/", response_model=schemas.Playlist, status_code=status.HTTP_201_CREATED, tags=["Playlists"])
def create_user_playlist(
    playlist_in: schemas.PlaylistCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    db = Session.object_session(current_user)
    playlist = crud.playlist.create_for_user(
        db=db, obj_in=playlist_in, user_id=current_user.user_id
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

@router.delete("/{playlist_id}", response_model=schemas.PlaylistSummary, tags=["Playlists"])
def delete_user_playlist(
    playlist_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    db = Session.object_session(current_user)
    deleted_playlist_orm = crud.playlist.delete_user_playlist(
        db=db,
        playlist_id=playlist_id,
        user_id=current_user.user_id
    )
    if not deleted_playlist_orm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found or does not belong to user."
        )
    return deleted_playlist_orm

@router.post("/{playlist_id}/songs", response_model=schemas.Playlist, tags=["Playlists"])
def add_song_to_playlist_endpoint(
    playlist_id: int,
    song_in: schemas.PlaylistSongCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    db = Session.object_session(current_user)
    crud.playlist.add_song_to_playlist(
        db=db,
        playlist_id=playlist_id,
        song_id=song_in.song_id,
        user_id=current_user.user_id,
    )
    playlist = crud.playlist.get_playlist_with_songs(
        db=db, playlist_id=playlist_id, user_id=current_user.user_id
    )
    if not playlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Playlist not found or does not belong to user."
        )
    return playlist


@router.delete("/{playlist_id}/songs/{song_id}", response_model=MessageResponse, tags=["Playlists"])
def remove_song_from_playlist_endpoint(
    playlist_id: int,
    song_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
):
    db = Session.object_session(current_user)
    crud.playlist.remove_song_from_playlist(
        db=db,
        playlist_id=playlist_id,
        song_id=song_id,
        user_id=current_user.user_id,
    )
    return {"message": "Song removed permanently from playlist"}

@router.get("/info/count", response_model=int, tags=["Playlists"])
def get_user_playlist_count(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    db = Session.object_session(current_user)
    return crud.playlist.count_by_user(
        db=db, 
        user_id=current_user.user_id
    )


