import pytest
import requests
import time

def test_api_health():
    response = requests.get("http://localhost:8000/docs")
    assert response.status_code == 200

def test_user_creation():
    response = requests.post("http://localhost:8000/api/users", params={"name": "Test User"})
    assert response.status_code == 200
    assert "user_id" in response.json()

def test_chat_functionality():
    # Create user first
    user_response = requests.post("http://localhost:8000/api/users", params={"name": "Test User"})
    user_id = user_response.json()["user_id"]
    
    # Send chat message
    chat_response = requests.post(
        "http://localhost:8000/api/chat",
        json={"message": "What is a variable in C?", "user_id": user_id}
    )
    assert chat_response.status_code == 200
    assert "response" in chat_response.json()