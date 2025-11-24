import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_movie_to_movie_endpoint(client):
    response = client.get("/recommend?inputKind=movie&targetKind=movie&q=Interstellar")
    assert response.status_code == 200
    # You can check the structure of returned data if you return a dict or JSON from your endpoint
    # Example: assert "recommendations" in response.get_json()

def test_book_to_book_endpoint(client):
    response = client.get("/recommend?inputKind=book&targetKind=book&q=The Hobbit")
    assert response.status_code == 200