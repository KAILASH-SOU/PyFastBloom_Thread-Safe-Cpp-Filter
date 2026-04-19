from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to PyFastBloom Enterprise API"}

def test_add_and_check_key():
    test_key = "test_user_123"

    response = client.get(f"/check/{test_key}")
    assert response.status_code == 200
    assert response.json() == {"key": test_key, "exists": False}

    response = client.post(f"/add?key={test_key}")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "key": test_key, "message": "Key added to the filter."}

    response = client.get(f"/check/{test_key}")
    assert response.status_code == 200
    assert response.json() == {"key": test_key, "exists": True}

def test_get_stats():
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "size" in data
    assert "hash_count" in data
    assert data["size"] == 1000000
    assert data["hash_count"] == 7
