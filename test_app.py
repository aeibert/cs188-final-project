import pytest
from unittest.mock import patch
from app import app


@pytest.fixture
def client():
    """Creates a Flask test client."""
    app.testing = True
    with app.test_client() as client:
        yield client


# ------------------------------------------------------------------------------------
# TEST: GET /
# ------------------------------------------------------------------------------------
@patch("functions.get_popular_movies")
def test_index_page(mock_get_popular_movies, client):
    mock_get_popular_movies.return_value = [
        {"id": 1, "title": "Mock Movie", "year": "2020", "poster": "x.jpg"}
    ]

    response = client.get("/")
    assert response.status_code == 200
    mock_get_popular_movies.assert_called_once()
    assert b"Mock Movie" in response.data  # template should render movie title


# ------------------------------------------------------------------------------------
# TEST: /recommend (movie → movie)
# ------------------------------------------------------------------------------------
@patch("functions.recommend_movies_from_movie")
def test_recommend_movie_to_movie(mock_recommend, client):
    mock_recommend.return_value = [
        {"id": 1, "title": "Movie A", "year": "2020"}
    ]

    response = client.get(
        "/recommend?inputKind=movie&targetKind=movie&q=Inception&limit=4"
    )

    assert response.status_code == 200
    mock_recommend.assert_called_once_with("Inception", 4)
    assert b"Movie A" in response.data


# ------------------------------------------------------------------------------------
# TEST: /recommend (book → book)
# ------------------------------------------------------------------------------------
@patch("functions.recommend_books_from_book")
def test_recommend_book_to_book(mock_recommend, client):
    mock_recommend.return_value = [
        {"id": 5, "title": "Book X", "year": "1999"}
    ]

    response = client.get(
        "/recommend?inputKind=book&targetKind=book&q=Dune&limit=3"
    )

    assert response.status_code == 200
    mock_recommend.assert_called_once_with("Dune", 3)
    assert b"Book X" in response.data


# ------------------------------------------------------------------------------------
# TEST: /recommend (movie → book)
# ------------------------------------------------------------------------------------
@patch("functions.recommend_books_from_movie")
def test_recommend_movie_to_book(mock_recommend, client):
    mock_recommend.return_value = [
        {"id": 7, "title": "Novel Y", "year": "2005"}
    ]

    response = client.get(
        "/recommend?inputKind=movie&targetKind=book&q=Interstellar&limit=2"
    )

    assert response.status_code == 200
    mock_recommend.assert_called_once_with("Interstellar", 2)
    assert b"Novel Y" in response.data


# ------------------------------------------------------------------------------------
# TEST: /recommend (book → movie, with genre)
# ------------------------------------------------------------------------------------
@patch("functions.recommend_movies_from_genre_dropdown")
def test_recommend_book_to_movie(mock_recommend, client):
    mock_recommend.return_value = [
        {"id": 10, "title": "Sci-Fi Movie", "year": "2010"}
    ]

    response = client.get(
        "/recommend?inputKind=book&targetKind=movie&genre=scifi&limit=4"
    )

    assert response.status_code == 200
    mock_recommend.assert_called_once_with("scifi", 4)
    assert b"Sci-Fi Movie" in response.data


# ------------------------------------------------------------------------------------
# TEST: /recommend (book → movie WITHOUT genre = empty results)
# ------------------------------------------------------------------------------------
def test_recommend_book_to_movie_no_genre(client):
    response = client.get(
        "/recommend?inputKind=book&targetKind=movie&limit=3"
    )
    assert response.status_code == 200
    # Since no genre was passed, results = [] and template should render no results
    assert b"No results" in response.data or b"0" in response.data


# ------------------------------------------------------------------------------------
# TEST: /detail (movie)
# ------------------------------------------------------------------------------------
@patch("functions.get_movie_details")
def test_detail_movie(mock_details, client):
    mock_details.return_value = {
        "title": "Mock Movie",
        "year": "2020",
        "kind": "Movie"
    }

    response = client.get("/detail?id=123&kind=movie")

    assert response.status_code == 200
    mock_details.assert_called_once_with("123")
    assert b"Mock Movie" in response.data


# ------------------------------------------------------------------------------------
# TEST: /detail (book)
# ------------------------------------------------------------------------------------
@patch("functions.get_book_details")
def test_detail_book(mock_details, client):
    mock_details.return_value = {
        "title": "Mock Book",
        "year": "1999",
        "kind": "Book"
    }

    response = client.get("/detail?id=45&kind=book")

    assert response.status_code == 200
    mock_details.assert_called_once_with("45")
    assert b"Mock Book" in response.data


# ------------------------------------------------------------------------------------
# TEST: /detail returns 404 when item not found
# ------------------------------------------------------------------------------------
@patch("functions.get_movie_details")
def test_detail_not_found(mock_details, client):
    mock_details.return_value = None

    response = client.get("/detail?id=999&kind=movie")

    assert response.status_code == 404
    assert b"Item not found" in response.data

