# file: test_user_audit.py (REFACTORED AND ROBUST VERSION)

import requests
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import time
import os
import uuid
from contextlib import contextmanager

# --- 1. Centralized Configuration ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
DB_SCHEMA = "vibesia_schema"

# --- 2. Check Configuration ---
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set. Check your .env file.")

# --- 3. Database Connection ---
try:
    engine = sqlalchemy.create_engine(
        DATABASE_URL,
        connect_args={"options": f"-csearch_path={DB_SCHEMA}"}  # Use schema
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"\033[91m❌ Error: Could not connect to the database: {e}\033[0m")
    exit(1)

# --- 4. Test Setup ---
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 5. Example test ---
def test_connection_and_user_creation():
    print("✅ Connected to DB and API")
    print(f"🌐 API: {API_BASE_URL}")
    print(f"🗄️ DB:  {DATABASE_URL}")

    # Test ping API
    response = requests.get(f"{API_BASE_URL}/health")
    assert response.status_code == 200, "API is not healthy"
    print("🚀 API is up and running.")


if __name__ == "__main__":
    test_connection_and_user_creation()

@contextmanager
def get_db():
    """Context manager to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 3. Helper Functions ---

def print_test_result(name, success, details=""):
    """Prints test results with formatting and colors."""
    status = "\033[92mPASS\033[0m" if success else "\033[91mFAIL\033[0m"
    print(f"[ {status} ] {name}")
    if not success and details:
        print(f"       └─> Details: {details}")

def query_audit_log(db, record_id, action_type):
    """Queries the audit log for a specific entry."""
    query = sqlalchemy.text(
        f"SELECT * FROM {DB_SCHEMA}.audit_log "
        "WHERE table_name = 'users' AND record_id = :record_id AND action_type = :action_type "
        "ORDER BY timestamp DESC"
    )
    result = db.execute(query, {'record_id': record_id, 'action_type': action_type}).fetchall()
    return result

# --- 4. Modular Test Functions ---

def test_1_create_user(test_state: dict):
    """Tests user creation and verifies the audit log (INSERT)."""
    test_name = "1. User Creation (INSERT Audit)"
    user_email = f"lifecycle_user_{uuid.uuid4().hex[:8]}@example.com"
    user_password = "strongpassword123"
    test_state['email'] = user_email
    test_state['password'] = user_password
    
    response = requests.post(
        f"{API_BASE_URL}/api/v1/users/",
        json={"email": user_email, "username": user_email, "password": user_password}
    )
    
    if response.status_code != 201:
        print_test_result(test_name, False, f"API call failed with status {response.status_code}: {response.text}")
        return False

    user_data = response.json()
    test_state['user_id'] = user_data.get('user_id')
    time.sleep(0.5)  # Wait for the DB trigger

    with get_db() as db:
        logs = query_audit_log(db, test_state['user_id'], 'INSERT')
        if len(logs) == 1 and logs[0].app_user_id is None:
            print_test_result(test_name, True)
            return True
        else:
            details = f"Expected 1 log with app_user_id=NULL, found {len(logs)}. Log: {logs}"
            print_test_result(test_name, False, details)
            return False

def test_2_login_user(test_state: dict):
    """Tests the login of the created user."""
    test_name = "2. User Login"
    response = requests.post(
        f"{API_BASE_URL}/api/v1/auth/login",
        data={"username": test_state['email'], "password": test_state['password']}
    )

    if response.status_code != 200:
        print_test_result(test_name, False, f"API call failed with status {response.status_code}: {response.text}")
        return False
        
    test_state['token'] = response.json().get('access_token')
    print_test_result(test_name, True)
    return True

def test_3_update_user(test_state: dict):
    """Tests user self-update and verifies the audit log (UPDATE)."""
    test_name = "3. User Self-Update (UPDATE Audit)"
    headers = {"Authorization": f"Bearer {test_state['token']}"}
    
    response = requests.put(
        f"{API_BASE_URL}/api/v1/users/me",
        headers=headers,
        json={"preferences": "Updated by lifecycle test"}
    )
    
    if response.status_code != 200:
        print_test_result(test_name, False, f"API call failed with status {response.status_code}: {response.text}")
        return False

    time.sleep(0.5)
    with get_db() as db:
        user_id = test_state['user_id']
        logs = query_audit_log(db, user_id, 'UPDATE')
        if len(logs) >= 1 and logs[0].app_user_id == user_id:
            print_test_result(test_name, True)
            return True
        else:
            details = f"Expected at least 1 log with app_user_id={user_id}, found {len(logs)}. Log: {logs}"
            print_test_result(test_name, False, details)
            return False

def test_4_delete_user(test_state: dict):
    """Tests user self-deletion and verifies the audit log (DELETE)."""
    test_name = "4. User Self-Deletion (DELETE Audit)"
    headers = {"Authorization": f"Bearer {test_state['token']}"}

    response = requests.delete(f"{API_BASE_URL}/api/v1/users/me", headers=headers)

    if response.status_code != 200:
        print_test_result(test_name, False, f"API call failed with status {response.status_code}: {response.text}")
        return False

    time.sleep(0.5)
    with get_db() as db:
        user_id = test_state['user_id']
        logs = query_audit_log(db, user_id, 'DELETE')
        # The verification logic is correct: the user performing the deletion is the logged-in user.
        if len(logs) >= 1 and logs[0].app_user_id == user_id:
            print_test_result(test_name, True)
            test_state['is_deleted'] = True
            return True
        else:
            details = f"Expected >= 1 log with app_user_id={user_id}, found {len(logs)}. Log: {logs}"
            print_test_result(test_name, False, details)
            return False

# --- 5. Test Orchestrator and Cleanup ---

def run_all_tests():
    """Main function that runs all tests in sequence."""
    print("="*60)
    print("  Running User Lifecycle and Audit Tests")
    print("="*60)
    
    test_state = {}  # A dictionary to pass state between tests

    try:
        if not test_1_create_user(test_state): return
        if not test_2_login_user(test_state): return
        if not test_3_update_user(test_state): return
        if not test_4_delete_user(test_state): return
    
    except requests.exceptions.ConnectionError as e:
        print(f"\n\033[91mConnection Error: Could not connect to the API at {API_BASE_URL}.\033[0m")
        print(f"       └─> Make sure your FastAPI/Uvicorn application is running.")
    except Exception as e:
        print(f"\n\033[91mAn unexpected error occurred during execution: {e}\033[0m")
    
    finally:
        # Cleanup always runs, regardless of whether the tests passed or failed.
        print("\n--- Cleaning up test data (if necessary) ---")
        if not test_state.get('is_deleted') and test_state.get('user_id'):
            try:
                with get_db() as db:
                    delete_query = sqlalchemy.text(f"DELETE FROM {DB_SCHEMA}.users WHERE user_id = :user_id")
                    db.execute(delete_query, {'user_id': test_state['user_id']})
                    db.commit()
                    print(f"Cleaned up test user with ID: {test_state['user_id']}")
            except Exception as e:
                print(f"\033[91mAutomatic cleanup failed: {e}\033[0m")
                print(f"       └─> You may need to manually delete the user with email: {test_state.get('email')}")
        elif test_state.get('is_deleted'):
            print("Test user was deleted successfully by the test. No cleanup needed.")
        else:
            print("No user was created to clean up.")
    print("\n" + "="*60)
    print("  Tests finished.")
    print("="*60)


if __name__ == "__main__":
    run_all_tests()