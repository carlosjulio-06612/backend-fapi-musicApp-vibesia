# 🎧 Music Streaming API

Backend API for a music streaming platform built with **FastAPI**. This project includes authentication, user management, playlists, playback history, and more functionalities.

## 📁 Project Structure

```
src/
├── alembic/
│
├── app/
│   ├── api/
│   │   ├── deps.py               # Common dependencies for endpoints
│   │   └── v1/
│   │       ├── api.py            # Main router for version 1
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── artist.py     # Artist-related endpoints
│   │           ├── auth.py       # Authentication and token generation
│   │           ├── song.py       # Endpoints for song management and queries
│   │           ├── password.py   # Password management
│   │           ├── playlist.py   # Playlist endpoints
│   │           └── users.py      # User management
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # General project configuration
│   │   ├── database.py           # Database connection and configuration
│   │   ├── security.py           # Security and authentication functions
│   │   └── utils.py              # General utilities
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py               # Generic CRUD operations
│   │   ├── crud_artist.py        # Artist-specific CRUD
│   │   ├── crud_playlist.py      # Playlist-specific CRUD
│   │   ├── crud_song.py          # Song-specific CRUD
│   │   └── crud_user.py          # User-specific CRUD
│   ├── models/
│   │   ├── __init__.py
│   │   ├── Album.py
│   │   ├── Artist.py
│   │   ├── Device.py
│   │   ├── Genre.py
│   │   ├── PlaybackHistory.py
│   │   ├── Playlist.py
│   │   ├── PlaylistSong.py
│   │   ├── Song.py
│   │   ├── SongGenre.py
│   │   ├── User.py
│   │   ├── UserDevice.py
│   │   └── audit_log.py         # User actions audit log
│   ├── schemas/
│   │   ├── artist.py
│   │   ├── audit_log.py
│   │   ├── password.py
│   │   ├── playlist.py
│   │   ├── song.py
│   │   ├── token.py
│   │   └── user.py              # Pydantic schemas for user validation
│   ├── main.py                  # Main entry point for FastAPI application
│   │
│   └── __init__.py
│
├── test/
│   ├── confest.py               # Configuration for pytest testing
│   ├── test_user_audit.py       # Tests for audit log
│   └── test_users.py            # Tests for user functionalities
```

## 🚀 Technologies Used

- **FastAPI**: Modern, high-performance web framework for building APIs
- **SQLAlchemy**: ORM for defining and querying database models
- **Pydantic**: Python-based data validation
- **Alembic** (optional): Database migrations
- **Pytest**: Testing framework for automated tests
- **JWT**: Token-based authentication
- **Render**: Render is a cloud hosting platform that makes it easy to deploy web applications, APIs, databases, static services, and more.

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL/MySQL (database)
- pip or pipenv for dependency management

---

The entire project is compressed into a .zip file, available for download and local execution if you want to test the entire system.Or an even more technical and formal alternative: The entire project has been packaged into a .zip file, which can be used for testing or running the application locally.
## 🛠️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/carlosjulio-06612/backend-fapi-musicApp-vibesia.git

```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost/music_streaming_db

# JWT
SECRET_KEY=your_very_secure_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# General configuration
DEBUG=True
PROJECT_NAME=MusicApp - Vibesia
VERSION=1.0.0
```

### 5. Set up the database

```bash
# Create tables
python -c "from app.core.database import engine; from app.models import *; Base.metadata.create_all(bind=engine)"

#Use Alembic for migrations 
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 🚀 Running the Application

### Development mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## 📚 Documentation

Once the application is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🧪 Running Tests

```bash
# Run test
pytest src/test/test_user_audit.py

```

## 📡 Main Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update profile

### Artists
- `GET /api/v1/artists/` - List artists
- `GET /api/v1/artists/{id}` - Get specific artist

### Playlists
- `GET /api/v1/playlists/` - List user playlists
- `POST /api/v1/playlists/` - Create new playlist
- `PUT /api/v1/playlists/{id}` - Update playlist


---

## 🗂️ Main File Structure  

### 📦 Models  

Database model definitions using **SQLAlchemy**:  

* **`User.py`** – User model (authentication, profile data)  
* **`Artist.py`** – Artist model with biographical information  
* **`Album.py`** – Album model with metadata and artist relationships  
* **`Song.py`** – Song model with audio metadata and relationships  
* **`Genre.py`** – Music genre model for categorization  
* **`Playlist.py`** – User playlist model  
* **`PlaylistSong.py`** – Many-to-many relationship between playlists and songs  
* **`SongGenre.py`** – Many-to-many relationship between songs and genres  
* **`Device.py`** – User device model for playback tracking  
* **`UserDevice.py`** – Relationship between users and devices  
* **`PlaybackHistory.py`** – Playback history log  
* **`audit_log.py`** – User action log (audit trail)  

---  

### 🧾 Schemas  

**Pydantic** schemas for data validation and serialization:  

* **`user.py`** – Schemas for registration, login, and profile updates  
* **`artist.py`** – Schemas for artists (API input/output)  
* **`playlist.py`** – Schemas for playlist CRUD operations  
* **`token.py`** – JWT token schemas for authentication  
* **`password.py`** – Schemas for password validation and reset  
* **`audit_log.py`** – Schemas for audit log records  

---  

### ⚙️ CRUD (Database Operations)  

Database operations organized by entity:  

* **`base.py`** – Base class for generic CRUD operations  
* **`crud_user.py`** – User-specific operations  
* **`crud_artist.py`** – Artist-specific operations  
* **`crud_playlist.py`** – Playlist-specific operations

---


## 🔒 Security

- JWT Authentication
- Password hashing with bcrypt
- Data validation with Pydantic
- Endpoint protection with dependencies

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```