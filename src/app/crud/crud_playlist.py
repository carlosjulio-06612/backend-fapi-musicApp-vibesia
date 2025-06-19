from typing import List, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import text, exc, Integer, Boolean, String
from sqlalchemy.sql import outparam
from fastapi import HTTPException, status

from app.crud.base import CRUDBase
from app.models.Playlist import Playlist
from app.schemas.playlist import PlaylistCreate, PlaylistUpdate, PlaylistSongCreate

class CRUDPlaylist(CRUDBase[Playlist, PlaylistCreate, PlaylistUpdate]):

    def get_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[Playlist]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_summaries_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene resúmenes de playlists del usuario (sin las canciones completas)
        """
        result = db.execute(
            text("""
                SELECT 
                    p.playlist_id,
                    p.user_id,
                    p.name,
                    p.description,
                    p.status,
                    p.created_at,
                    p.updated_at,
                    COALESCE(COUNT(ps.song_id), 0) as song_count,
                    COALESCE(SUM(s.duration), 0) as total_duration
                FROM vibesia_schema.playlists p
                LEFT JOIN vibesia_schema.playlist_songs ps ON p.playlist_id = ps.playlist_id
                LEFT JOIN vibesia_schema.songs s ON ps.song_id = s.song_id
                WHERE p.user_id = :user_id
                GROUP BY p.playlist_id, p.user_id, p.name, p.description, p.status, p.created_at, p.updated_at
                ORDER BY p.created_at DESC
                OFFSET :skip LIMIT :limit
            """),
            {"user_id": user_id, "skip": skip, "limit": limit}
        ).fetchall()
    
        summaries = []
        for row in result:
            summary = {
                "playlist_id": row.playlist_id,
                "user_id": row.user_id,
                "name": row.name,
                "description": row.description,
                "status": row.status,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "song_count": row.song_count,
                "total_duration": row.total_duration
            }
            summaries.append(summary)
    
        return summaries
    

    def get_playlist_songs(self, db: Session, *, playlist_id: int, user_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves the songs from a specific user's playlist.
        """
        # Verify that the playlist belongs to the user
        if not self.get_user_playlist(db=db, playlist_id=playlist_id, user_id=user_id):
            return []

        try:
            result = db.execute(
                text("""
                    SELECT 
                        s.song_id,
                        s.title,
                        s.duration,
                        s.track_number,
                        s.composer,
                        s.audio_path,
                        s.explicit_content,
                        a.title AS album_title,
                        ar.name AS artist_name,
                        ps.position,
                        ps.date_added
                    FROM vibesia_schema.playlist_songs ps
                    JOIN vibesia_schema.songs s ON ps.song_id = s.song_id
                    JOIN vibesia_schema.albums a ON s.album_id = a.album_id
                    JOIN vibesia_schema.artists ar ON a.artist_id = ar.artist_id
                    WHERE ps.playlist_id = :playlist_id
                    ORDER BY ps.position ASC, ps.date_added ASC
                """),
                {"playlist_id": playlist_id}
            ).fetchall()

            return [dict(row._mapping) for row in result]

        except Exception as e:
            # Optionally log this error if logging is enabled
            print(f"Error retrieving playlist songs: {e}")
            return []


    def get_user_playlist(self, db: Session, *, playlist_id: int, user_id: int) -> Optional[Playlist]:
        return (
            db.query(self.model)
            .filter(
                self.model.playlist_id == playlist_id,
                self.model.user_id == user_id
            )
            .first()
        )
    
    def create_for_user(self, db: Session, *, obj_in: PlaylistCreate, user_id: int) -> Optional[Dict[str, Any]]:
        try:
            stmt = text("""
                SELECT * FROM vibesia_schema.sp_create_playlist(
                    p_user_id => :p_user_id,
                    p_name => :p_name,
                    p_description => :p_description,
                    p_status => :p_status
                )
            """)

            result = db.execute(
                stmt,
                {
                    "p_user_id": user_id,
                    "p_name": obj_in.name,
                    "p_description": obj_in.description,
                    "p_status": obj_in.status,
                }
            ).first()
        
            if not result or not result.p_success:
                db.rollback()
                error_message = result.p_message if result else "Failed to create playlist."
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message
                )

            new_playlist_id = result.p_playlist_id
            db.commit()
            
            return self.get_playlist_with_songs(db=db, playlist_id=new_playlist_id, user_id=user_id)

        except exc.SQLAlchemyError as e:
            db.rollback()
            self._handle_db_error(e)
        except Exception as e:
            db.rollback()
            raise e

    def update_user_playlist(
        self, db: Session, *, playlist_id: int, user_id: int, obj_in: PlaylistUpdate
    ) -> Optional[Dict[str, Any]]:
        try:
            if not self.get_user_playlist(db=db, playlist_id=playlist_id, user_id=user_id):
                return None

            update_data = obj_in.dict(exclude_unset=True)
            
            # CORRECTED: Use CALL with NULLs for OUT parameters
            db.execute(
                text("""
                    CALL vibesia_schema.sp_update_playlist(
                        p_success => NULL,
                        p_message => NULL,
                        p_playlist_id => :p_playlist_id,
                        p_user_id => :p_user_id,
                        p_new_name => :p_new_name,
                        p_new_description => :p_new_description,
                        p_new_status => :p_new_status
                    )
                """),
                {
                    "p_playlist_id": playlist_id,
                    "p_user_id": user_id,
                    "p_new_name": update_data.get("name"),
                    "p_new_description": update_data.get("description"),
                    "p_new_status": update_data.get("status"),
                },
            )

            db.commit()
            return self.get_playlist_with_songs(db=db, playlist_id=playlist_id, user_id=user_id)

        except exc.SQLAlchemyError as e:
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
            
            # CORRECTED: Use CALL with NULLs for OUT parameters
            db.execute(
                text("""
                    CALL vibesia_schema.sp_delete_playlist(
                        p_success => NULL,
                        p_message => NULL,
                        p_songs_removed => NULL,
                        p_playlist_id => :p_playlist_id,
                        p_user_id => :p_user_id
                    )
                """),
                {"p_playlist_id": playlist_id, "p_user_id": user_id},
            )

            db.commit()
            return playlist_to_delete
            
        except exc.SQLAlchemyError as e:
            db.rollback()
            raise e

    def add_song_to_playlist(
        self, db: Session, *, playlist_id: int, song_id: int, user_id: int, position: Optional[int] = None
    ) -> None:
        # CORRECTED: Use CALL with NULLs for OUT parameters
        db.execute(
            text("""
                CALL vibesia_schema.sp_add_song_to_playlist(
                    p_success => NULL,
                    p_message => NULL,
                    p_playlist_id => :p_playlist_id,
                    p_song_id => :p_song_id,
                    p_user_id => :p_user_id,
                    p_position => :p_position
                )
            """),
            {
                "p_playlist_id": playlist_id,
                "p_song_id": song_id,
                "p_user_id": user_id,
                "p_position": position,
            },
        )

    def remove_song_from_playlist(
        self, db: Session, *, playlist_id: int, song_id: int, user_id: int
    ) -> None:
        try:
            # CORRECTED: Use CALL with NULLs for OUT parameters
            db.execute(
                text("""
                    CALL vibesia_schema.sp_remove_song_from_playlist(
                        p_success => NULL,
                        p_message => NULL,
                        p_playlist_id => :p_playlist_id,
                        p_song_id => :p_song_id,
                        p_user_id => :p_user_id
                    )
                """),
                {
                    "p_playlist_id": playlist_id,
                    "p_song_id": song_id,
                    "p_user_id": user_id,
                },
            )
            
            db.commit()

        except exc.SQLAlchemyError as e:
            db.rollback()
            raise e

    def get_playlist_stats(
        self, db: Session, *, playlist_id: int, user_id: int
    ) -> Optional[Dict[str, Any]]:
        if not self.get_user_playlist(db=db, playlist_id=playlist_id, user_id=user_id):
            return None
        
        result = db.execute(
            text("""
                SELECT 
                    COUNT(ps.song_id) as song_count,
                    COALESCE(SUM(s.duration), 0) as total_duration
                FROM vibesia_schema.playlist_songs ps
                LEFT JOIN vibesia_schema.songs s ON ps.song_id = s.song_id
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

    
    def _handle_db_error(self, e: exc.SQLAlchemyError):
        # Start with a generic message as the absolute last resort
        detail = "An internal database error occurred."

        # The best way is to get the message from the original DBAPI exception
        if e.orig:
            if hasattr(e.orig, 'pgerror') and e.orig.pgerror:
                error_message = str(e.orig.pgerror)
                # Try to clean up the message from PostgreSQL
                if 'ERROR:' in error_message:
                    detail = error_message.split('ERROR:')[1].strip()
                else:
                    detail = error_message
            elif hasattr(e.orig, 'diag') and e.orig.diag.message_primary:
                detail = e.orig.diag.message_primary
            else:
                # A more robust fallback: convert the original exception to a string.
                # This usually contains the full error message from the database.
                detail = str(e.orig)
        else:
             # If there's no original exception, use the SQLAlchemy exception string
             detail = str(e)
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


playlist = CRUDPlaylist(Playlist)