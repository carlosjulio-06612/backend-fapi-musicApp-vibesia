import pytest
from fastapi.testclient import TestClient

def test_create_user(client: TestClient):
    response = client.post(
        f"/api/v1/users/", 
        json={
            "email": "test@example.com",
            "username": "testuser", 
            "password": "testpassword123", 
        }
    )
    assert response.status_code == 201, response.text 
    
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser" 
    assert "user_id" in data 
    assert "hashed_password" not in data 