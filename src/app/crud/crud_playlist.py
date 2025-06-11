from typing import List, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.crud.base import CRUDBase
from app.models.Playlist import Playlist
from app.schemas.playlist import PlaylistCreate, PlaylistUpdate

class CRUDPlaylist(CRUDBase[Playlist, PlaylistCreate, PlaylistUpdate]):

    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Playlist]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user_playlist(
        self, db: Session, *, playlist_id: int, user_id: int
    ) -> Optional[Playlist]:
        return (
            db.query(self.model)
            .filter(
                self.model.playlist_id == playlist_id,
                self.model.user_id == user_id
            )
            .first()
        )

    def create_for_user(
        self, db: Session, *, obj_in: PlaylistCreate, user_id: int
    ) -> Optional[Dict[str, Any]]:
        try:
            result = db.execute(
                text("CALL sp_create_playlist(:user_id, :name, :description, :status)"),
                {
                    "user_id": user_id,
                    "name": obj_in.name,
                    "description": obj_in.description,
                    "status": obj_in.status,
                },
            )
            playlist_result = result.fetchone()
            if not playlist_result:
                db.rollback()
                return None
            
            playlist_id = playlist_result[0]

            if obj_in.song_ids:
                for position, song_id in enumerate(obj_in.song_ids):
                    self.add_song_to_playlist(
                        db=db,
                        playlist_id=playlist_id,
                        song_id=song_id,
                        user_id=user_id,
                        position=position
                    )
            
            db.commit()
            return self.get_playlist_with_songs(db=db, playlist_id=playlist_id, user_id=user_id)

        except Exception as e:
            db.rollback()
            raise e

    def update_user_playlist(
        self, db: Session, *, playlist_id: int, user_id: int, obj_in: PlaylistUpdate
    ) -> Optional[Dict[str, Any]]:
        try:
            existing_playlist = self.get_user_playlist(
                db=db, playlist_id=playlist_id, user_id=user_id
            )
            if not existing_playlist:
                return None

            update_data = obj_in.model_dump(exclude_unset=True)

            if any(key in update_data for key in ['name', 'description', 'status']):
                db.execute(
                    text("CALL sp_update_playlist_info(:p_playlist_id, :p_user_id, :p_name, :p_description, :p_status)"),
                    {
                        "p_playlist_id": playlist_id,
                        "p_user_id": user_id,
                        "p_name": update_data.get("name", existing_playlist.name),
                        "p_description": update_data.get("description", existing_playlist.description),
                        "p_status": update_data.get("status", existing_playlist.status),
                    },
                )

            if obj_in.add_songs:
                for song_data in obj_in.add_songs:
                    self.add_song_to_playlist(
                        db=db, playlist_id=playlist_id, song_id=song_data.song_id, user_id=user_id
                    )

            if obj_in.remove_songs:
                for song_id in obj_in.remove_songs:
                    self.remove_song_from_playlist(
                        db=db, playlist_id=playlist_id, song_id=song_id, user_id=user_id
                    )

            if obj_in.reorder_songs:
                for reorder_data in obj_in.reorder_songs:
                    self.reorder_song_in_playlist(
                        db=db,
                        playlist_id=playlist_id,
                        song_id=reorder_data.song_id,
                        new_position=reorder_data.new_position,
                        user_id=user_id,
                    )
            
            db.commit()
            return self.get_playlist_with_songs(db=db, playlist_id=playlist_id, user_id=user_id)

        except Exception as e:
            db.rollback()
            raise e

    def delete_user_playlist(
        self, db: Session, *, playlist_id: int, user_id: int
    ) -> Optional[Playlist]:
        try:
            playlist_to_delete = self.get_user_playlist(
                db=db, playlist_id=playlist_id, user_id=user_id
            )
            if not playlist_to_delete:
                return None
            
            db.execute(
                text("CALL sp_delete_playlist(:p_playlist_id, :p_user_id)"),
                {"p_playlist_id": playlist_id, "p_user_id": user_id},
            )
            db.commit()
            return playlist_to_delete
            
        except Exception as e:
            db.rollback()
            raise e

    def add_song_to_playlist(
        self, db: Session, *, playlist_id: int, song_id: int, user_id: int, position: Optional[int] = None
    ) -> None:
        if not self.get_user_playlist(db=db, playlist_id=playlist_id, user_id=user_id):
            raise ValueError("Playlist not found or does not belong to the user")
        
        db.execute(
            text("CALL sp_add_song_to_playlist(:p_playlist_id, :p_song_id, :p_position)"),
            {
                "p_playlist_id": playlist_id,
                "p_song_id": song_id,
                "p_position": position
            },
        )

    def remove_song_from_playlist(
        self, db: Session, *, playlist_id: int, song_id: int, user_id: int
    ) -> None:
        if not self.get_user_playlist(db=db, playlist_id=playlist_id, user_id=user_id):
            raise ValueError("Playlist not found or does not belong to the user")
        
        db.execute(
            text("CALL sp_remove_song_from_playlist(:p_playlist_id, :p_song_id)"),
            {"p_playlist_id": playlist_id, "p_song_id": song_id},
        )

    def reorder_song_in_playlist(
        self, db: Session, *, playlist_id: int, song_id: int, new_position: int, user_id: int
    ) -> None:
        if not self.get_user_playlist(db=db, playlist_id=playlist_id, user_id=user_id):
            raise ValueError("Playlist not found or does not belong to the user")
        
        db.execute(
            text("CALL sp_reorder_playlist_song(:p_playlist_id, :p_song_id, :p_new_position)"),
            {
                "p_playlist_id": playlist_id,
                "p_song_id": song_id,
                "p_new_position": new_position,
            },
        )

    def get_playlist_songs(
        self, db: Session, *, playlist_id: int, user_id: int
    ) -> List[Dict[str, Any]]:
        if not self.get_user_playlist(db=db, playlist_id=playlist_id, user_id=user_id):
            return []
        
        result = db.execute(
            text("""
                SELECT s.song_id, s.title, s.artist_name, s.duration_seconds, ps.position
                FROM playlist_songs ps
                JOIN songs s ON ps.song_id = s.song_id
                WHERE ps.playlist_id = :playlist_id
                ORDER BY ps.position ASC
            """),
            {"playlist_id": playlist_id}
        )
        return [dict(row._mapping) for row in result]

    def get_playlist_stats(
        self, db: Session, *, playlist_id: int, user_id: int
    ) -> Optional[Dict[str, Any]]:
        if not self.get_user_playlist(db=db, playlist_id=playlist_id, user_id=user_id):
            return None
        
        result = db.execute(
            text("""
                SELECT 
                    COUNT(ps.song_id) as song_count,
                    COALESCE(SUM(s.duration_seconds), 0) as total_duration
                FROM playlist_songs ps
                LEFT JOIN songs s ON ps.song_id = s.song_id
                WHERE ps.playlist_id = :playlist_id
            """),
            {"playlist_id": playlist_id}
        ).fetchone()
        
        return dict(result._mapping) if result else None

    def get_playlist_with_songs(
        self, db: Session, *, playlist_id: int, user_id: int
    ) -> Optional[Dict[str, Any]]:
        playlist_orm = self.get_user_playlist(db=db, playlist_id=playlist_id, user_id=user_id)
        if not playlist_orm:
            return None
        
        songs = self.get_playlist_songs(db=db, playlist_id=playlist_id, user_id=user_id)
        stats = self.get_playlist_stats(db=db, playlist_id=playlist_id, user_id=user_id)
        
        playlist_data = {
            "playlist_id": playlist_orm.playlist_id,
            "user_id": playlist_orm.user_id,
            "name": playlist_orm.name,
            "description": playlist_orm.description,
            "status": playlist_orm.status,
            "created_at": playlist_orm.created_at,
            "updated_at": playlist_orm.updated_at,
            "songs": songs,
            "song_count": stats.get("song_count", 0) if stats else 0,
            "total_duration": stats.get("total_duration", 0) if stats else 0
        }
        
        return playlist_data

    def count_by_user(self, db: Session, *, user_id: int) -> int:
        return db.query(self.model).filter(self.model.user_id == user_id).count()


playlist = CRUDPlaylist(Playlist)