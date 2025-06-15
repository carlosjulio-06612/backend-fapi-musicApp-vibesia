from typing import List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.SongDetail], tags=["Songs"])
def read_songs(
    db: Session = Depends(deps.get_db_session),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve all songs with artist details.
    """
    songs = crud.song.get_multi_with_details(db=db, skip=skip, limit=limit)
    return songs