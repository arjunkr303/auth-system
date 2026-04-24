import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# Ensure the backend directory is in the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Synx AI Auth API is running"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("main.get_connection")
def test_register_user_success(mock_get_connection):
    # Mock the DB connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock cursor.fetchone to return None (user doesn't exist)
    mock_cursor.fetchone.return_value = None
    
    response = client.post(
        "/register",
        json={
            "customer_name": "Test User",
            "phone_number": "1234567890",
            "password": "testpassword"
        }
    )
    
    assert response.status_code == 200
    assert "User registered successfully!" in response.json()["message"]
    assert mock_cursor.execute.call_count == 2
    mock_conn.commit.assert_called_once()

@patch("main.get_connection")
def test_register_user_already_exists(mock_get_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock cursor.fetchone to return a user (user exists)
    mock_cursor.fetchone.return_value = {"id": 1}
    
    response = client.post(
        "/register",
        json={
            "customer_name": "Test User",
            "phone_number": "1234567890",
            "password": "testpassword"
        }
    )
    
    assert response.status_code == 200
    assert "Account already exists!" in response.json()["error"]
