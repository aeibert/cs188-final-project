import pytest
from unittest.mock import patch, MagicMock
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# -------------------------------------------------------------------
# TEST: index route "/"
# -------------------------------------------------------------------
@patch("app.functions.get_popular_movies")
def test_index(mock_get_popular, client):
    mock_get_popular.return_value = [
        {"id": 1, "title": "Test Movie", "year": "2020"}
    ]

    response = client.get("/")

    assert response.status_code == 200
    mock_get_popular.assert_called_once()


# -------------------------------------------------------------------
# TEST: /recommend route - movie->movie
# -------------------------------------------------------------------
@patch("app.functions.recommend_movies_from_movie")
def test_recommend_movie_to_movie(mock_reco, client):

    mock_reco.return_value = [
        {"id": 1, "title": "Test Movie", "kind": "Movie"}
    ]

    response = client.get("/recommend?inputKind=movie&targetKind=movie&q=Inception&limit=1")

    assert response.status_code == 200
    mock_reco.assert_called_once_with("Inception", 1)


# -------------------------------------------------------------------
# TEST: /recommend route - book->book
# -------------------------------------------------------------------
@patch("app.functions.recommend_books_from_book")
def test_recommend_book_to_book(mock_reco, client):

    mock_reco.return_value = [
        {"id": 55, "title": "Test Book", "kind": "Book"}
    ]

    response = client.get("/recommend?inputKind=book&targetKind=book&q=Dune&limit=1")

    assert response.status_code == 200
    mock_reco.assert_called_once_with("Dune", 1)


# -------------------------------------------------------------------
# TEST: /recommend route - movie->book
# -------------------------------------------------------------------
@patch("app.functions.recommend_books_from_movie")
def test_recommend_movie_to_book(mock_reco, client):

    mock_reco.return_value = [
        {"id": 88, "title": "Book", "kind": "Book"}
    ]

    response = client.get("/recommend?inputKind=movie&targetKind=book&q=Avatar&limit=2")

    assert response.status_code == 200
    mock_reco.assert_called_once_with("Avatar", 2)


# -------------------------------------------------------------------
# TEST: /recommend route - book->movie (with genre)
# -------------------------------------------------------------------
@patch("app.functions.recommend_movies_from_genre_dropdown")
def test_recommend_book_to_movie_with_genre(mock_reco, client):

    mock_reco.return_value = [
        {"id": 44, "title": "Action Movie", "kind": "Movie"}
    ]

    response = client.get("/recommend?inputKind=book&targetKind=movie&genre=action&q=Dune&limit=1")

    assert response.status_code == 200
    mock_reco.assert_called_once_with("action", 1)


# -------------------------------------------------------------------
# TEST: /recommend route - book->movie (NO genre → empty list)
# -------------------------------------------------------------------
@patch("app.functions.recommend_movies_from_genre_dropdown")
def test_recommend_book_to_movie_without_genre(mock_reco, client):

    response = client.get("/recommend?inputKind=book&targetKind=movie&q=Dune&limit=1")

    # Should NOT call the recommender
    mock_reco.assert_not_called()
    assert response.status_code == 200


# -------------------------------------------------------------------
# TEST: /detail route - movie
# -------------------------------------------------------------------
@patch("app.functions.get_movie_details")
def test_detail_movie(mock_details, client):

    mock_details.return_value = {
        "title": "Inception",
        "year": "2010",
        "kind": "Movie"
    }

    response = client.get("/detail?id=1&kind=movie")

    assert response.status_code == 200
    mock_details.assert_called_once_with("1")


# -------------------------------------------------------------------
# TEST: /detail route - book
# -------------------------------------------------------------------
@patch("app.functions.get_book_details")
def test_detail_book(mock_details, client):

    mock_details.return_value = {
        "title": "Dune",
        "year": "1965",
        "kind": "Book"
    }

    response = client.get("/detail?id=5&kind=book")

    assert response.status_code == 200
    mock_details.assert_called_once_with("5")


# -------------------------------------------------------------------
# TEST: /detail route - returns 404 when item not found
# -------------------------------------------------------------------
@patch("app.functions.get_movie_details")
def test_detail_not_found(mock_details, client):

    mock_details.return_value = None

    response = client.get("/detail?id=999&kind=movie")

    assert response.status_code == 404
