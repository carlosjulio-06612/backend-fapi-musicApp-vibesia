# file: test_artist_crud_integrated.py - Artist CRUD Test with Integrated User Authentication

import requests
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import time
import os
import uuid
from contextlib import contextmanager
from typing import Dict, Any, Optional, List
from datetime import datetime

# --- 1. Centralized Configuration ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
DB_SCHEMA = "vibesia_schema"

# Admin configuration from your settings
ADMIN_USER_IDS = [27, 28]  # Updated to match your actual admin IDs
ADMIN_EMAILS = ["admin@example.com", "superuser@example.com"]
ADMIN_USERNAMES = ["admin", "superuser"]

# Use first admin by default
DEFAULT_ADMIN_ID = ADMIN_USER_IDS[0]
DEFAULT_ADMIN_EMAIL = ADMIN_EMAILS[0]
DEFAULT_ADMIN_USERNAME = ADMIN_USERNAMES[0]

# --- 2. Check Configuration ---
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set. Check your .env file.")

# --- 3. Database Connection ---
try:
    engine = sqlalchemy.create_engine(
        DATABASE_URL,
        connect_args={"options": f"-csearch_path={DB_SCHEMA}"}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"\033[91m❌ Error: Could not connect to the database: {e}\033[0m")
    exit(1)

@contextmanager
def get_db():
    """Context manager to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 4. Integrated User Management Functions ---

class UserManager:
    """Integrated user management using database queries."""
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID from database."""
        try:
            with get_db() as db:
                query = sqlalchemy.text(
                    f"SELECT user_id, email, username, is_active FROM {DB_SCHEMA}.users WHERE user_id = :user_id"
                )
                result = db.execute(query, {'user_id': user_id}).fetchone()
                if result:
                    return {
                        'user_id': result.user_id,
                        'email': result.email,
                        'username': result.username,
                        'is_active': result.is_active
                    }
            return None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email from database."""
        try:
            with get_db() as db:
                query = sqlalchemy.text(
                    f"SELECT user_id, email, username, is_active FROM {DB_SCHEMA}.users WHERE email = :email"
                )
                result = db.execute(query, {'email': email}).fetchone()
                if result:
                    return {
                        'user_id': result.user_id,
                        'email': result.email,
                        'username': result.username,
                        'is_active': result.is_active
                    }
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
        """Get user by username from database."""
        try:
            with get_db() as db:
                query = sqlalchemy.text(
                    f"SELECT user_id, email, username, is_active FROM {DB_SCHEMA}.users WHERE username = :username"
                )
                result = db.execute(query, {'username': username}).fetchone()
                if result:
                    return {
                        'user_id': result.user_id,
                        'email': result.email,
                        'username': result.username,
                        'is_active': result.is_active
                    }
            return None
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None
    
    @staticmethod
    def verify_admin_users() -> List[Dict[str, Any]]:
        """Verify which admin users exist in the database."""
        existing_admins = []
        
        for user_id in ADMIN_USER_IDS:
            user = UserManager.get_user_by_id(user_id)
            if user:
                existing_admins.append(user)
        
        # Also check by email and username
        for email in ADMIN_EMAILS:
            user = UserManager.get_user_by_email(email)
            if user and user['user_id'] not in [admin['user_id'] for admin in existing_admins]:
                existing_admins.append(user)
        
        for username in ADMIN_USERNAMES:
            user = UserManager.get_user_by_username(username)
            if user and user['user_id'] not in [admin['user_id'] for admin in existing_admins]:
                existing_admins.append(user)
        
        return existing_admins
    
    @staticmethod
    def create_test_user() -> Optional[Dict[str, Any]]:
        """Creates a regular test user for permission testing."""
        user_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
        user_username = f"testuser_{uuid.uuid4().hex[:8]}"
        user_password = "testpassword123"
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/users/",
            json={
                "email": user_email,
                "username": user_username,
                "password": user_password
            }
        )
        
        if response.status_code == 201:
            user_data = response.json()
            return {
                'email': user_email,
                'username': user_username,
                'password': user_password,
                'user_id': user_data.get('user_id')
            }
        else:
            print(f"Failed to create test user: {response.status_code} - {response.text}")
        return None

# --- 5. Helper Functions ---

def print_test_result(name: str, success: bool, details: str = ""):
    """Prints test results with formatting and colors."""
    status = "\033[92mPASS\033[0m" if success else "\033[91mFAIL\033[0m"
    print(f"[ {status} ] {name}")
    if not success and details:
        print(f"       └─> Details: {details}")
    elif success and details:
        print(f"       └─> {details}")

def login_user(identifier: str, password: str) -> Optional[str]:
    """Logs in a user using email or username and returns the access token."""
    response = requests.post(
        f"{API_BASE_URL}/api/v1/auth/login",
        data={"username": identifier, "password": password}
    )
    
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"Login failed for {identifier}: {response.status_code} - {response.text}")
    return None

def query_audit_log(db, record_id: int, action_type: str, table_name: str = 'artists'):
    """Queries the audit log for a specific entry."""
    try:
        query = sqlalchemy.text(
            f"SELECT * FROM {DB_SCHEMA}.audit_log "
            "WHERE table_name = :table_name AND record_id = :record_id AND action_type = :action_type "
            "ORDER BY timestamp DESC LIMIT 1"
        )
        result = db.execute(query, {
            'table_name': table_name, 
            'record_id': record_id, 
            'action_type': action_type
        }).fetchall()
        return result
    except Exception as e:
        print(f"Audit log query failed: {e}")
        return []

def cleanup_test_user(user_id: int):
    """Cleans up a test user from the database."""
    try:
        with get_db() as db:
            delete_query = sqlalchemy.text(f"DELETE FROM {DB_SCHEMA}.users WHERE user_id = :user_id")
            db.execute(delete_query, {'user_id': user_id})
            db.commit()
            print(f"✅ Cleaned up test user with ID: {user_id}")
    except Exception as e:
        print(f"\033[91m❌ Cleanup failed for user {user_id}: {e}\033[0m")

def cleanup_test_artist(artist_id: int):
    """Cleans up a test artist from the database."""
    try:
        with get_db() as db:
            delete_query = sqlalchemy.text(f"DELETE FROM {DB_SCHEMA}.artists WHERE artist_id = :artist_id")
            db.execute(delete_query, {'artist_id': artist_id})
            db.commit()
            print(f"✅ Cleaned up test artist with ID: {artist_id}")
    except Exception as e:
        print(f"\033[91m❌ Cleanup failed for artist {artist_id}: {e}\033[0m")

# --- 6. Test Functions ---

def test_1_verify_admin_users_exist(test_state: Dict[str, Any]) -> bool:
    """Verifies that admin users exist in the database."""
    test_name = "1. Verify Admin Users Exist in Database"
    
    existing_admins = UserManager.verify_admin_users()
    
    if not existing_admins:
        print_test_result(test_name, False, "No admin users found in database")
        return False
    
    test_state['available_admins'] = existing_admins
    admin_details = ", ".join([f"ID:{admin['user_id']}({admin['email']})" for admin in existing_admins])
    print_test_result(test_name, True, f"Found {len(existing_admins)} admin users: {admin_details}")
    return True

def test_2_admin_login_attempt(test_state: Dict[str, Any]) -> bool:
    """Attempts to login with available admin users."""
    test_name = "2. Admin Login Attempt"
    
    # Try different password combinations
    possible_passwords = [
        os.getenv("ADMIN_TEST_PASSWORD", "Admin1234"),
        "admin123",
        "password",
        "admin",
        "123456",
        "vibesia123",
        "superuser123"
    ]
    
    for admin in test_state['available_admins']:
        print(f"   Trying to login admin: {admin['email']} (ID: {admin['user_id']})")
        
        for password in possible_passwords:
            # Try with email
            token = login_user(admin['email'], password)
            if token:
                test_state['admin_token'] = token
                test_state['admin_user'] = admin
                print_test_result(test_name, True, f"Logged in as {admin['email']} with password")
                return True
            
            # Try with username
            token = login_user(admin['username'], password)
            if token:
                test_state['admin_token'] = token
                test_state['admin_user'] = admin
                print_test_result(test_name, True, f"Logged in as {admin['username']} with password")
                return True
    
    print_test_result(test_name, False, "Could not login any admin user. Please check admin passwords or create a test admin.")
    print("   💡 Hint: Set ADMIN_TEST_PASSWORD environment variable or ensure admin users have known passwords")
    return False

def test_3_create_test_user(test_state: Dict[str, Any]) -> bool:
    """Creates a regular test user for permission testing."""
    test_name = "3. Create Regular Test User"
    
    test_user = UserManager.create_test_user()
    if not test_user:
        print_test_result(test_name, False, "Failed to create test user")
        return False
    
    test_state['test_user'] = test_user
    print_test_result(test_name, True, f"Created user: {test_user['email']}")
    return True

def test_4_regular_user_login(test_state: Dict[str, Any]) -> bool:
    """Tests regular user login."""
    test_name = "4. Regular User Login"
    
    test_user = test_state['test_user']
    token = login_user(test_user['email'], test_user['password'])
    
    if token:
        test_state['regular_token'] = token
        print_test_result(test_name, True)
        return True
    else:
        print_test_result(test_name, False, "Failed to login regular user")
        return False

def test_5_regular_user_cannot_create_artist(test_state: Dict[str, Any]) -> bool:
    """Tests that regular users cannot create artists."""
    test_name = "5. Regular User Cannot Create Artist (Permission Check)"
    
    artist_data = {
        "name": f"Unauthorized Band {uuid.uuid4().hex[:8]}",
        "country": "Colombia",
        "formation_year": 2020,
        "biography": "This should not be created by regular user",
        "artist_type": "band"
    }
    
    headers = {"Authorization": f"Bearer {test_state['regular_token']}"}
    response = requests.post(
        f"{API_BASE_URL}/api/v1/artists/",
        headers=headers,
        json=artist_data
    )
    
    if response.status_code in [401, 403]:
        print_test_result(test_name, True, f"Correctly denied with status {response.status_code}")
        return True
    else:
        print_test_result(test_name, False, f"Expected 401/403, got {response.status_code}: {response.text}")
        return False

def test_6_admin_can_create_artist(test_state: Dict[str, Any]) -> bool:
    """Tests that admin users can create artists."""
    test_name = "6. Admin Can Create Artist"
    
    if 'admin_token' not in test_state:
        print_test_result(test_name, False, "No admin token available")
        return False
    
    artist_data = {
        "name": f"Admin Test Band {uuid.uuid4().hex[:8]}",
        "country": "Colombia",
        "formation_year": 2023,
        "biography": "Test band created by admin user",
        "artist_type": "band"
    }
    
    test_state['artist_data'] = artist_data
    
    headers = {"Authorization": f"Bearer {test_state['admin_token']}"}
    response = requests.post(
        f"{API_BASE_URL}/api/v1/artists/",
        headers=headers,
        json=artist_data
    )
    
    if response.status_code != 201:
        print_test_result(test_name, False, f"Failed to create artist: {response.status_code} - {response.text}")
        return False
    
    artist_response = response.json()
    test_state['artist_id'] = artist_response.get('artist_id')
    
    # Check audit log
    time.sleep(0.5)
    try:
        with get_db() as db:
            logs = query_audit_log(db, test_state['artist_id'], 'INSERT', 'artists')
            if logs:
                admin_user_id = test_state['admin_user']['user_id']
                print_test_result(test_name, True, f"Artist created (ID: {test_state['artist_id']}) with audit by admin {admin_user_id}")
            else:
                print_test_result(test_name, True, f"Artist created (ID: {test_state['artist_id']})")
    except Exception as e:
        print_test_result(test_name, True, f"Artist created, audit check failed: {e}")
    
    return True

def test_7_read_created_artist(test_state: Dict[str, Any]) -> bool:
    """Tests reading the created artist."""
    test_name = "7. Read Created Artist"
    
    response = requests.get(f"{API_BASE_URL}/api/v1/artists/{test_state['artist_id']}")
    
    if response.status_code != 200:
        print_test_result(test_name, False, f"Failed to read artist: {response.status_code}")
        return False
    
    artist_data = response.json()
    expected_name = test_state['artist_data']['name']
    
    if artist_data.get('name') == expected_name:
        print_test_result(test_name, True, f"Artist retrieved: {expected_name}")
        return True
    else:
        print_test_result(test_name, False, f"Name mismatch: expected {expected_name}, got {artist_data.get('name')}")
        return False

def test_8_regular_user_cannot_update_artist(test_state: Dict[str, Any]) -> bool:
    """Tests that regular users cannot update artists."""
    test_name = "8. Regular User Cannot Update Artist"
    
    update_data = {
        "biography": "Unauthorized update attempt",
        "popularity": 99
    }
    
    headers = {"Authorization": f"Bearer {test_state['regular_token']}"}
    response = requests.put(
        f"{API_BASE_URL}/api/v1/artists/{test_state['artist_id']}",
        headers=headers,
        json=update_data
    )
    
    if response.status_code in [401, 403]:
        print_test_result(test_name, True, f"Correctly denied with status {response.status_code}")
        return True
    else:
        print_test_result(test_name, False, f"Expected 401/403, got {response.status_code}")
        return False

def test_9_admin_can_update_artist(test_state: Dict[str, Any]) -> bool:
    """Tests that admin users can update artists."""
    test_name = "9. Admin Can Update Artist"
    
    update_data = {
        "biography": "Updated by admin - test successful",
        "popularity": 75
    }
    
    headers = {"Authorization": f"Bearer {test_state['admin_token']}"}
    response = requests.put(
        f"{API_BASE_URL}/api/v1/artists/{test_state['artist_id']}",
        headers=headers,
        json=update_data
    )
    
    if response.status_code != 200:
        print_test_result(test_name, False, f"Update failed: {response.status_code}: {response.text}")
        return False
    
    time.sleep(0.5)
    try:
        with get_db() as db:
            logs = query_audit_log(db, test_state['artist_id'], 'UPDATE', 'artists')
            if logs:
                admin_user_id = test_state['admin_user']['user_id']
                print_test_result(test_name, True, f"Artist updated with audit by admin {admin_user_id}")
            else:
                print_test_result(test_name, True, "Artist updated successfully")
    except Exception as e:
        print_test_result(test_name, True, f"Artist updated, audit check failed: {e}")
    
    return True

def test_10_regular_user_cannot_delete_artist(test_state: Dict[str, Any]) -> bool:
    """Tests that regular users cannot delete artists."""
    test_name = "10. Regular User Cannot Delete Artist"
    
    headers = {"Authorization": f"Bearer {test_state['regular_token']}"}
    response = requests.delete(
        f"{API_BASE_URL}/api/v1/artists/{test_state['artist_id']}",
        headers=headers
    )
    
    if response.status_code in [401, 403]:
        print_test_result(test_name, True, f"Correctly denied with status {response.status_code}")
        return True
    else:
        print_test_result(test_name, False, f"Expected 401/403, got {response.status_code}")
        return False

def test_11_admin_can_delete_artist(test_state: Dict[str, Any]) -> bool:
    """Tests that admin users can delete artists."""
    test_name = "11. Admin Can Delete Artist"
    
    headers = {"Authorization": f"Bearer {test_state['admin_token']}"}
    response = requests.delete(
        f"{API_BASE_URL}/api/v1/artists/{test_state['artist_id']}",
        headers=headers
    )
    
    if response.status_code != 200:
        print_test_result(test_name, False, f"Delete failed: {response.status_code}: {response.text}")
        return False
    
    test_state['artist_deleted'] = True
    
    time.sleep(0.5)
    try:
        with get_db() as db:
            logs = query_audit_log(db, test_state['artist_id'], 'DELETE', 'artists')
            if logs:
                admin_user_id = test_state['admin_user']['user_id']
                print_test_result(test_name, True, f"Artist deleted with audit by admin {admin_user_id}")
            else:
                print_test_result(test_name, True, "Artist deleted successfully")
    except Exception as e:
        print_test_result(test_name, True, f"Artist deleted, audit check failed: {e}")
    
    return True

def test_12_verify_artist_deleted(test_state: Dict[str, Any]) -> bool:
    """Verifies that the artist was actually deleted."""
    test_name = "12. Verify Artist Deletion"
    
    response = requests.get(f"{API_BASE_URL}/api/v1/artists/{test_state['artist_id']}")
    
    if response.status_code == 404:
        print_test_result(test_name, True, "Artist successfully removed from database")
        return True
    else:
        print_test_result(test_name, False, f"Expected 404, got {response.status_code}")
        return False

# --- 7. Test Orchestrator ---

def run_all_tests():
    """Main function that runs all integrated artist CRUD tests."""
    print("="*80)
    print("  🎵 Running Integrated Artist CRUD Tests with User Authentication 🎵")
    print("="*80)
    
    test_state = {}
    
    try:
        # Test sequence
        tests = [
            test_1_verify_admin_users_exist,
            test_2_admin_login_attempt,
            test_3_create_test_user,
            test_4_regular_user_login,
            test_5_regular_user_cannot_create_artist,
            test_6_admin_can_create_artist,
            test_7_read_created_artist,
            test_8_regular_user_cannot_update_artist,
            test_9_admin_can_update_artist,
            test_10_regular_user_cannot_delete_artist,
            test_11_admin_can_delete_artist,
            test_12_verify_artist_deleted
        ]
        
        for test_func in tests:
            if not test_func(test_state):
                print(f"\n\033[91m❌ Test sequence stopped at: {test_func.__name__}\033[0m")
                break
        else:
            print("\n\033[92m🎉 All tests passed successfully! 🎉\033[0m")
        
    except requests.exceptions.ConnectionError:
        print(f"\n\033[91m❌ Connection Error: Could not connect to the API at {API_BASE_URL}.\033[0m")
        print("       └─> Make sure your FastAPI application is running.")
    except Exception as e:
        print(f"\n\033[91m❌ An unexpected error occurred: {e}\033[0m")
    
    finally:
        # Cleanup
        print("\n--- 🧹 Cleaning up test data ---")
        
        # Clean up artist if not deleted by test
        if not test_state.get('artist_deleted') and test_state.get('artist_id'):
            cleanup_test_artist(test_state['artist_id'])
        
        # Clean up regular test user
        if test_state.get('test_user', {}).get('user_id'):
            cleanup_test_user(test_state['test_user']['user_id'])
        
        print("\n" + "="*80)
        print("  ✅ Artist CRUD Tests Completed")
        print("="*80)

def test_api_health():
    """Tests if the API is responding."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API Health Check: PASSED")
            return True
        else:
            print(f"❌ API Health Check: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API Health Check: FAILED (Error: {e})")
        return False

if __name__ == "__main__":
    print("🚀 Starting Integrated Artist CRUD Tests...")
    print(f"🌐 API Base URL: {API_BASE_URL}")
    print(f"👤 Admin Usernames: {ADMIN_USERNAMES}")
    print()
    
    # Check API health first
    if test_api_health():
        print()
        run_all_tests()
    else:
        print("\n❌ API is not responding. Please check your server and try again.")
        print("💡 Make sure your FastAPI server is running and accessible.")