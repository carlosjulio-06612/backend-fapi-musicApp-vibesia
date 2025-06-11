from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, playlist, artist, password

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

api_router.include_router(users.router, prefix="/users")

api_router.include_router(playlist.router, prefix="/playlists", tags=["playlists"])
api_router.include_router(artist.router, prefix="/artists", tags=["artists"])

api_router.include_router(password.router, prefix="/password")