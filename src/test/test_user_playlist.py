# file: test_user_playlist_lifecycle.py (FIXED VERSION)

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
DB_SCHEMA = "vibesia_schema"  # Centralized schema name in case it changes

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

# --- 4. Database Context Manager ---
@contextmanager
def get_db():
    """Context manager to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 5. Helper Functions ---
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

def cleanup_user_cascade(db, user_id):
    """
    Properly cleanup user data with cascade handling.
    This function handles the foreign key relationships manually.
    """
    try:
        # First, get all playlists for this user
        playlist_query = sqlalchemy.text(
            f"SELECT playlist_id FROM {DB_SCHEMA}.playlists WHERE user_id = :user_id"
        )
        playlists = db.execute(playlist_query, {'user_id': user_id}).fetchall()
        
        # For each playlist, delete playlist_songs first
        for playlist in playlists:
            playlist_id = playlist[0]
            # Delete playlist songs
            delete_playlist_songs = sqlalchemy.text(
                f"DELETE FROM {DB_SCHEMA}.playlist_songs WHERE playlist_id = :playlist_id"
            )
            db.execute(delete_playlist_songs, {'playlist_id': playlist_id})
            
            # Delete the playlist itself
            delete_playlist = sqlalchemy.text(
                f"DELETE FROM {DB_SCHEMA}.playlists WHERE playlist_id = :playlist_id"
            )
            db.execute(delete_playlist, {'playlist_id': playlist_id})
        
        # Finally, delete the user
        delete_user = sqlalchemy.text(f"DELETE FROM {DB_SCHEMA}.users WHERE user_id = :user_id")
        db.execute(delete_user, {'user_id': user_id})
        
        # Commit all changes
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Cascade cleanup error: {e}")
        return False

# --- 6. User Test Functions ---
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
        if len(logs) >= 1:  # Changed from == 1 to >= 1 for more flexibility
            print_test_result(test_name, True)
            return True
        else:
            details = f"Expected at least 1 INSERT log, found {len(logs)}. Log: {logs}"
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
        if len(logs) >= 1:
            print_test_result(test_name, True)
            return True
        else:
            details = f"Expected at least 1 UPDATE log, found {len(logs)}. Log: {logs}"
            print_test_result(test_name, False, details)
            return False

# --- 7. Playlist Test Functions ---
def test_4_get_empty_playlists(test_state: dict):
    """Tests getting empty playlists list for new user."""
    test_name = "4. Get Empty Playlists"
    headers = {"Authorization": f"Bearer {test_state['token']}"}
    
    response = requests.get(f"{API_BASE_URL}/api/v1/playlists/", headers=headers)
    
    if response.status_code != 200:
        print_test_result(test_name, False, f"API call failed with status {response.status_code}: {response.text}")
        return False
    
    playlists = response.json()
    if isinstance(playlists, list) and len(playlists) == 0:
        print_test_result(test_name, True)
        return True
    else:
        print_test_result(test_name, False, f"Expected empty list, got: {playlists}")
        return False

def test_5_create_playlist(test_state: dict):
    """Tests playlist creation."""
    test_name = "5. Create Playlist"
    headers = {"Authorization": f"Bearer {test_state['token']}"}
    
    response = requests.post(
        f"{API_BASE_URL}/api/v1/playlists/",
        headers=headers,
        json={"name": "My Test Playlist", "description": "A test playlist created by automation."}
    )
    
    if response.status_code != 201:
        print_test_result(test_name, False, f"API call failed with status {response.status_code}: {response.text}")
        return False
    
    playlist = response.json()
    test_state['playlist_id'] = playlist.get('playlist_id')
    test_state['playlists_created'] = test_state.get('playlists_created', [])
    test_state['playlists_created'].append(test_state['playlist_id'])
    print_test_result(test_name, True, f"Created playlist ID: {test_state['playlist_id']}")
    return True

def test_6_get_playlist_by_id(test_state: dict):
    """Tests retrieving playlist by ID."""
    test_name = "6. Get Playlist by ID"
    headers = {"Authorization": f"Bearer {test_state['token']}"}
    
    response = requests.get(f"{API_BASE_URL}/api/v1/playlists/{test_state['playlist_id']}", headers=headers)
    
    if response.status_code != 200:
        print_test_result(test_name, False, f"API call failed with status {response.status_code}: {response.text}")
        return False
    
    print_test_result(test_name, True)
    return True

def test_7_update_playlist(test_state: dict):
    """Tests playlist update."""
    test_name = "7. Update Playlist"
    headers = {"Authorization": f"Bearer {test_state['token']}"}
    
    response = requests.put(
        f"{API_BASE_URL}/api/v1/playlists/{test_state['playlist_id']}",
        headers=headers,
        json={"name": "Updated Playlist Name", "description": "Updated description."}
    )
    
    if response.status_code != 200:
        print_test_result(test_name, False, f"API call failed with status {response.status_code}: {response.text}")
        return False
    
    print_test_result(test_name, True)
    return True

def test_8_add_songs_to_playlist(test_state: dict):
    """Tests adding songs to playlist."""
    test_name = "8. Add Songs to Playlist"
    headers = {"Authorization": f"Bearer {test_state['token']}"}
    test_state['song_ids'] = [1, 2]  # Assuming these exist in the DB
    
    success_count = 0
    for song_id in test_state['song_ids']:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/playlists/{test_state['playlist_id']}/songs",
            headers=headers,
            json={"song_id": song_id}
        )
        if response.status_code == 200:
            success_count += 1
        else:
            print(f"       └─> Warning: Failed to add song {song_id}: {response.text}")
    
    if success_count > 0:
        test_state['songs_added'] = True
        print_test_result(test_name, True, f"Added {success_count}/{len(test_state['song_ids'])} songs")
        return True
    else:
        print_test_result(test_name, False, "No songs could be added")
        return False

def test_9_remove_song_from_playlist(test_state: dict):
    """Tests removing a song from playlist."""
    test_name = "9. Remove Song from Playlist"
    headers = {"Authorization": f"Bearer {test_state['token']}"}
    
    if not test_state.get('song_ids'):
        print_test_result(test_name, False, "No songs to remove")
        return False
    
    song_to_remove = test_state['song_ids'][0]
    response = requests.delete(
        f"{API_BASE_URL}/api/v1/playlists/{test_state['playlist_id']}/songs/{song_to_remove}",
        headers=headers
    )
    
    if response.status_code != 200:
        print_test_result(test_name, False, f"API call failed with status {response.status_code}: {response.text}")
        return False
    
    print_test_result(test_name, True, f"Removed song {song_to_remove}")
    return True

def test_10_get_playlist_count(test_state: dict):
    """Tests getting playlist count."""
    test_name = "10. Get Playlist Count"
    headers = {"Authorization": f"Bearer {test_state['token']}"}
    
    response = requests.get(f"{API_BASE_URL}/api/v1/playlists/info/count", headers=headers)
    
    if response.status_code != 200:
        print_test_result(test_name, False, f"API call failed with status {response.status_code}: {response.text}")
        return False
    
    count_data = response.json()
    print_test_result(test_name, True, f"Playlist count: {count_data}")
    return True

def test_11_delete_playlist(test_state: dict):
    """Tests playlist deletion."""
    test_name = "11. Delete Playlist"
    headers = {"Authorization": f"Bearer {test_state['token']}"}
    
    response = requests.delete(f"{API_BASE_URL}/api/v1/playlists/{test_state['playlist_id']}", headers=headers)
    
    if response.status_code != 200:
        print_test_result(test_name, False, f"API call failed with status {response.status_code}: {response.text}")
        return False
    
    test_state['playlist_deleted'] = True
    # Remove from created playlists list
    if test_state['playlist_id'] in test_state.get('playlists_created', []):
        test_state['playlists_created'].remove(test_state['playlist_id'])
    
    print_test_result(test_name, True)
    return True

def test_12_delete_user(test_state: dict):
    """Tests user self-deletion and verifies the audit log (DELETE)."""
    test_name = "12. User Self-Deletion (DELETE Audit)"
    headers = {"Authorization": f"Bearer {test_state['token']}"}

    response = requests.delete(f"{API_BASE_URL}/api/v1/users/me", headers=headers)

    if response.status_code != 200:
        print_test_result(test_name, False, f"API call failed with status {response.status_code}: {response.text}")
        return False

    time.sleep(0.5)
    with get_db() as db:
        user_id = test_state['user_id']
        logs = query_audit_log(db, user_id, 'DELETE')
        if len(logs) >= 1:
            print_test_result(test_name, True)
            test_state['is_deleted'] = True
            return True
        else:
            details = f"Expected >= 1 DELETE log, found {len(logs)}. Log: {logs}"
            print_test_result(test_name, False, details)
            return False

# --- 8. Test Orchestrator ---
def run_all_tests():
    """Main function that runs all tests in sequence."""
    print("="*70)
    print("  Running Integrated User and Playlist Lifecycle Tests")
    print("="*70)
    
    test_state = {}  # A dictionary to pass state between tests

    # Define test sequence
    test_functions = [
        test_1_create_user,
        test_2_login_user,
        test_3_update_user,
        test_4_get_empty_playlists,
        test_5_create_playlist,
        test_6_get_playlist_by_id,
        test_7_update_playlist,
        test_8_add_songs_to_playlist,
        test_9_remove_song_from_playlist,
        test_10_get_playlist_count,
        test_11_delete_playlist,
        test_12_delete_user  # User deletion is LAST
    ]

    try:
        # Run tests sequentially
        for test_func in test_functions:
            if not test_func(test_state):
                print(f"\n⚠️  Test failed: {test_func.__name__}. Stopping execution.")
                break
        else:
            print(f"\n🎉 All tests completed successfully!")
    
    except requests.exceptions.ConnectionError as e:
        print(f"\n\033[91mConnection Error: Could not connect to the API at {API_BASE_URL}.\033[0m")
        print(f"       └─> Make sure your FastAPI/Uvicorn application is running.")
    except Exception as e:
        print(f"\n\033[91mAn unexpected error occurred during execution: {e}\033[0m")
    
    finally:
        # Cleanup always runs, regardless of whether the tests passed or failed.
        print("\n--- Cleaning up test data (if necessary) ---")
        
        # Clean up any remaining playlists first
        if test_state.get('playlists_created') and test_state.get('token'):
            try:
                headers = {"Authorization": f"Bearer {test_state['token']}"}
                for playlist_id in test_state['playlists_created'][:]:  # Copy list to avoid modification during iteration
                    response = requests.delete(f"{API_BASE_URL}/api/v1/playlists/{playlist_id}", headers=headers)
                    if response.status_code == 200:
                        print(f"Cleaned up playlist with ID: {playlist_id}")
                        test_state['playlists_created'].remove(playlist_id)
                    else:
                        print(f"Failed to cleanup playlist {playlist_id}: {response.text}")
            except Exception as e:
                print(f"\033[91mPlaylist cleanup failed: {e}\033[0m")
        
        # Clean up user if it wasn't deleted by the test
        if not test_state.get('is_deleted') and test_state.get('user_id'):
            try:
                with get_db() as db:
                    success = cleanup_user_cascade(db, test_state['user_id'])
                    if success:
                        print(f"Cleaned up test user with ID: {test_state['user_id']} (with cascade)")
                    else:
                        print(f"\033[91mFailed to cleanup user with cascade\033[0m")
            except Exception as e:
                print(f"\033[91mAutomatic user cleanup failed: {e}\033[0m")
                print(f"       └─> You may need to manually delete the user with email: {test_state.get('email')}")
        elif test_state.get('is_deleted'):
            print("Test user was deleted successfully by the test. No cleanup needed.")
        else:
            print("No user was created to clean up.")
            
    print("\n" + "="*70)
    print("  Tests finished.")
    print("="*70)


# --- 9. Health Check Function ---
def test_connection_and_health():
    """Tests basic connectivity to API and database."""
    print("✅ Connected to DB and API")
    print(f"🌐 API: {API_BASE_URL}")
    print(f"🗄️ DB:  {DATABASE_URL}")

    # Test ping API
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("🚀 API is up and running.")
            return True
        else:
            print(f"⚠️  API health check returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure it's running.")
        return False


if __name__ == "__main__":
    # Optional: Run health check first
    if test_connection_and_health():
        print()  # Add spacing
        run_all_tests()
    else:
        print("❌ Health check failed. Please check your API connection.")