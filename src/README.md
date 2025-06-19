# 🎵 MusicApp - Vibesia (Backend API)

Backend developed with **FastAPI** for Vibesia, a music platform that allows managing artists, songs, playlists, playback history, devices and more.

---

## 🚀 Description

This backend exposes a RESTful API to manage the musical information of the **Vibesia** system, including:

- CRUD operations for users, artists, songs and playlists.
- Playback history and device management.
- Audit logging.
- Authentication and authorization with JWT.
- Support for complex relationships (many-to-many) like songs ↔ genres and playlists ↔ songs.

---

## 🛠️ Technologies

- **Python 3.11+**
- **FastAPI**
- **SQLAlchemy**
- **PostgreSQL**
- **Alembic**
- **Pydantic**
- **Uvicorn**
- **JWT (Auth)**
- **psycopg2**

---

## 📦 Project Structure

```
BACKEND-FAPI-MUSICAPP-VIBESIA/
├── src/
│   ├── alembic/               # Database migrations
│   └── app/
│       ├── api/               # Routing and controllers
│       ├── core/              # Configuration, security, database
│       ├── crud/              # CRUD logic per entity
│       ├── models/            # SQLAlchemy model definitions
│       ├── schemas/           # Pydantic input/output schemas
│       ├── utils/             # Helper functions
│       └── main.py            # Main entry point
```

---

## ⚙️ Installation and Setup

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/musicapp-vibesia-backend.git
cd musicapp-vibesia-backend
```

2. **Create and activate virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**

Create a `.env` file in `src/` with the following content:

```env
DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/musicdb
SECRET_KEY=a-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PROJECT_NAME="MusicApp - Vibesia"
API_V1_STR="/api/v1"
```

---

## 🏁 Running the Project

```bash
cd src
uvicorn app.main:app --reload
```

API available at: [http://localhost:8000](http://localhost:8000)

Interactive documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔐 Authentication

* Uses JWT.
* Login via `/api/v1/auth/login`.
* Tokens must be sent in the header:

```http
Authorization: Bearer <token>
```

---

## 📤 Main Endpoints

* `POST /auth/login`: User login.
* `POST /auth/register`: User registration.
* `GET /users/me`: Authenticated user profile.
* `GET /artists/`: List of artists.
* `GET /songs/`: List of songs.
* `GET /playlists/`: List and CRUD operations for playlists.
* `POST /playlists/{id}/songs`: Add songs to playlist.

---

## 📄 License

This project is licensed under the **MIT** License. See the [LICENSE](LICENSE) file for more information.

---