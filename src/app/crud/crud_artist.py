from sqlalchemy.orm import Session
from typing import Optional

from app.crud.base import CRUDBase
from app.models.Artist import Artist as ArtistModel
from app.schemas.artist import ArtistCreate, ArtistUpdate

class CRUDArtist(CRUDBase[ArtistModel, ArtistCreate, ArtistUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[ArtistModel]:
        """
        Get an artist by their exact name.
        """
        return db.query(self.model).filter(self.model.name == name).first()

artist = CRUDArtist(ArtistModel)