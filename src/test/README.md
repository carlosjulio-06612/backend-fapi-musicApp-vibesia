# 🧪 User Lifecycle and Audit Log Test Suite

This project provides an automated test suite to verify the **user lifecycle** (creation, authentication, updating, and deletion) and validate the corresponding **audit logs** in a PostgreSQL database with `vibesia_schema`.

---

## 🚀 Features

- Creates a new user and verifies the `INSERT` in the audit log.
- Performs authentication (login) and stores the JWT token.
- Modifies user preferences and checks the audited `UPDATE`.
- Deletes the user and verifies the `DELETE` in the log.
- Automatic cleanup of the test environment.
- Colored result messages for better readability.

---

## ⚙️ Requirements

- Python 3.8 or higher
- FastAPI backend running locally (`/api/v1`)
- PostgreSQL database with `vibesia_schema` schema and `audit_log` table
- Environment variables configured:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/your_db
API_BASE_URL=http://127.0.0.1:8000/api/v1  # optional
```

---

## 📦 Installation

1. Clone this repository or copy the `test_user_audit.py` file.
2. Install the necessary dependencies:

```bash
pip install requests sqlalchemy python-dotenv
```

3. Make sure the API is running and the database is accessible.

---

## 🧪 Execution

```bash
python test_user_audit.py
```

The script will automatically execute:

1. User creation
2. Login
3. Data update
4. User deletion
5. Verification of each action in the audit log

---
![Terminal 1](./images/Terminal_1.png)

## 🧠 Internal Structure

| Section                    | Description                                                      |
|----------------------------|------------------------------------------------------------------|
| Configuration              | Reading environment variables and database connection             |
| Helper functions           | Output coloring, SQL queries to `audit_log`                     |
| Test functions             | `test_1_create_user`, `test_2_login_user`, `test_3_update_user`, `test_4_delete_user` |
| `run_all_tests` orchestrator| Runs all tests and manages post-test cleanup                    |

---

## 🛑 Important Notes

- The tests manipulate real data (create and delete users).
- The `audit_log` table must be properly configured with triggers.
- The API must expose the endpoints:
  - `POST /users/`
  - `POST /auth/login`
  - `PUT /users/me`
  - `DELETE /users/me`

---

## 📜 License

MIT. You can freely use, adapt, and redistribute this script.

---

## 🤝 Credits

Inspired by best practices from [Organization-DevXP/Guia-para-crear-READMEs-Profesionales](https://github.com/Organization-DevXP/Guia-para-crear-READMEs-Profesionales)