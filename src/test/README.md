# ✅ Vibesia API - Automated Test Suite

This repository contains a comprehensive automated test suite for the **Vibesia Music App API**. It is designed to ensure the **reliability**, **security**, and **correctness** of the system's key functionalities.

---

## 🚀 Key Features

- **User Lifecycle Testing**: Registration, authentication, profile updates, and secure deletion.
- **Role-Based Access Control (RBAC)**: Ensures only administrators can perform sensitive actions (e.g., artist management).
- **Complete CRUD Verification**: Full coverage of *Create, Read, Update, and Delete* operations.
- **Database Audit Validation**: Checks entries in `audit_log` for INSERT, UPDATE, and DELETE.
- **Automated Data Cleanup**: Each test creates and removes its own data, ensuring clean environments.
- **Clear Colored Console Output**: Immediate and readable feedback when running tests.

---

## ⚙️ Requirements

- Python **3.8+**
- Active instance of the Vibesia FastAPI backend
- Access to a PostgreSQL database with the `vibesia_schema` schema
- Required tables: `users`, `artists`, `playlists`, `audit_log`

### 📦 Required Libraries

Install them with:

```bash
pip install requests sqlalchemy python-dotenv psycopg2-binary
```

---

## 🔧 Configuration

Before running the tests, ensure you have a `.env` file with the following variables:

```env
# Base URL of the backend
API_BASE_URL="https://backend-fapi-musicapp-vibesia.onrender.com"

# Database connection URL
DATABASE_URL="postgresql+psycopg2://user:password@host:port/database"
```

---

## 🧪 Test Suites

The suite is organized into modular files, each targeting a specific functionality:

---

### 1. 🧍‍♂️ User & Playlist Lifecycle

📄 File: `test_user_playlist.py`

**Coverage:**

* User creation (INSERT + audit)
* Login and token generation
* Profile updates (UPDATE + audit)
* Playlist CRUD
* Adding/removing songs from playlists
* User deletion (DELETE + audit)

**Run with:**

```bash
python test_user_playlist.py
```

🖼️ Expected result:
![user-playlist-test](./images/Terminal_3.png)

---

### 2. 🎤 Artist CRUD & Permissions

📄 File: `test_artist_crud.py`

**Coverage:**

* Login as admin
* CRUD attempts by non-admin users (expected: 403)
* Valid admin operations: Create, Read, Update, Delete
* Audit verification for each action

**Run with:**

```bash
python test_artist_crud.py
```

🖼️ Expected result:
![artist-test](./images/Terminal_2.png)

---

### 3. 🛡️ User Audit Validation

📄 File: `test_user_audit.py`

**Coverage:**

* Registration (INSERT)
* Login
* Updates (UPDATE)
* Deletion (DELETE)
* Audit verification at each step

**Run with:**

```bash
python test_user_audit.py
```

🖼️ Expected result:
![user-audit-test](./images/Terminal_1.png)

---

## � Technical Architecture

| Component         | Description                                                                 |
| ----------------- | --------------------------------------------------------------------------- |
| `requests`        | Makes HTTP calls to FastAPI endpoints                                       |
| `SQLAlchemy`      | Direct database access to verify conditions and clean data                  |
| `@contextmanager` | Manages database session lifecycle (`get_db()`)                             |
| `test_state`      | Dictionary storing tokens, IDs, and shared states between functions        |
| `finally block`   | Data cleanup even if a test fails                                           |

---

## ⚠️ Important Considerations

* **Do not run these tests in production.**
* The backend must be running and accessible at the specified URL.
* Tests modify the database and depend on audit triggers.
* Ensure endpoints `/api/v1/users/me`, `/api/v1/artists/`, etc., are correctly exposed.

---

## 📜 License

This project is licensed under the **MIT License**. You are free to use, adapt, and redistribute this test suite.

---

🚀 Powered by Team AD-ASTRA
"Testing APIs so you don't have to... unless you're an astronaut testing space APIs!"