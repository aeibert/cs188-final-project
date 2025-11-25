import pytest
from unittest.mock import patch, MagicMock

import functions

# --- Helper Mocks ---
class FakeMovie:
    def __init__(self, id, title, release_date, poster_path):
        self.id = id
        self.title = title
        self.release_date = release_date
        self.poster_path = poster_path

class FakeGenre:
    def __init__(self, id, name):
        self.id = id
        self.name = name

@pytest.fixture
# --- recommend_books_from_book ---
def test_recommend_books_from_book_valid(monkeypatch):
    class FakeApiClient:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): pass
    class FakeDefaultApi:
        def search_books(self, query, number):
            return {"books": [[{"id": 123, "title": "Book1", "image": "img.jpg"}]]}
        def find_similar_books(self, book_id, number):
            return {"similar_books": [{"id": 124, "title": "BookRec", "image": "img2.jpg"}]}
        def get_book_information(self, bid):
            return {"publish_date": 2001}

    monkeypatch.setattr("functions.bigbookapi.ApiClient", lambda cfg: FakeApiClient())
    monkeypatch.setattr("functions.bigbookapi.DefaultApi", lambda api_client: FakeDefaultApi())

    results = functions.recommend_books_from_book("Book1", 1)
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["title"] == "BookRec"
    assert results[0]["year"] == "2001"
    assert results[0]["kind"] == "Book"

def test_recommend_books_from_book_not_found(monkeypatch):
    class FakeApiClient:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): pass
    class FakeDefaultApi:
        def search_books(self, query, number):
            return {"books": [[]]}
    monkeypatch.setattr("functions.bigbookapi.ApiClient", lambda cfg: FakeApiClient())
    monkeypatch.setattr("functions.bigbookapi.DefaultApi", lambda api_client: FakeDefaultApi())
    results = functions.recommend_books_from_book("UnknownBook", 1)
    assert results == []

# --- recommend_books_from_movie ---
def test_recommend_books_from_movie_valid(monkeypatch):
    # Mocks: search_api.movies, movie_api.details, pyodbc, bigbookapi
    monkeypatch.setattr("functions.search_api.movies", lambda title: [FakeMovie(1, "Mov", "", None)])
    monkeypatch.setattr("functions.movie_api.details", lambda mid: MagicMock(genres=[{"id": 10}], id=1))
    # Fake DB connection
    class FakeCursor:
        def execute(self, query, val): return None
        def fetchone(self): return ["Fiction"]
    class FakeConn:
        def cursor(self): return FakeCursor()
        def close(self): pass
    monkeypatch.setattr("functions.get_db_connection", lambda: FakeConn())
    class FakeApiClient:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): pass
    class FakeDefaultApi:
        def search_books(self, genres, sort, number):
            return {"books": [[{"id": 22, "title": "BookByGenre", "image": "img.jpg", "publish_date": 2020}]]}
    monkeypatch.setattr("functions.bigbookapi.ApiClient", lambda cfg: FakeApiClient())
    monkeypatch.setattr("functions.bigbookapi.DefaultApi", lambda api_client: FakeDefaultApi())
    results = functions.recommend_books_from_movie("Matrix", 1)
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["title"] == "BookByGenre"
    assert results[0]["kind"] == "Book"
    assert results[0]["year"] == "2020"

def test_recommend_books_from_movie_no_db(monkeypatch):
    monkeypatch.setattr("functions.get_db_connection", lambda: None)
    results = functions.recommend_books_from_movie("Matrix", 1)
    assert results == []

# --- recommend_movies_from_genre_dropdown ---
def test_recommend_movies_from_genre_dropdown_valid(monkeypatch):
    # Fake DB connection
    class FakeCursor:
        def execute(self, query, val): return None
        def fetchone(self): return [28]
    class FakeConn:
        def cursor(self): return FakeCursor()
        def close(self): pass
    monkeypatch.setattr("functions.get_db_connection", lambda: FakeConn())
    # Fake discover_api
    monkeypatch.setattr("functions.discover_api.discover_movies", lambda args: [
        FakeMovie(100, "GenreMovie", "2018-09-15", "/gen.jpg")
    ])
    results = functions.recommend_movies_from_genre_dropdown("Action", 1)
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["title"] == "GenreMovie"
    assert results[0]["image"].endswith("/gen.jpg")
    assert results[0]["kind"] == "Movie"
    assert results[0]["year"] == "2018"

def test_recommend_movies_from_genre_dropdown_no_db(monkeypatch):
    monkeypatch.setattr("functions.get_db_connection", lambda: None)
    results = functions.recommend_movies_from_genre_dropdown("Action", 1)
    assert results == []

# --- get_popular_movies ---
def test_get_popular_movies_valid(monkeypatch):
    # Fake popular movies
    monkeypatch.setattr("functions.movie_api.popular", lambda: [
        FakeMovie(1, "Pop1", "1999-05-02", "/pop1.jpg"),
        FakeMovie(2, "Pop2", "2001-06-14", "/pop2.jpg"),
        FakeMovie(3, "Pop3", "2002-08-01", "/pop3.jpg"),
        FakeMovie(4, "Pop4", None, None)
    ])
    results = functions.get_popular_movies()
    assert len(results) == 4
    assert results[0]["title"] == "Pop1"
    assert results[3]["year"] == "N/A"  # No release_date

def test_get_popular_movies_apierror(monkeypatch):
    monkeypatch.setattr("functions.movie_api.popular", lambda: (_ for _ in ()).throw(Exception("fail")))
    results = functions.get_popular_movies()
    assert results == []

# --- get_movie_details ---
def test_get_movie_details_valid(monkeypatch):
    class MovieObj:
        title = "TestMov"
        release_date = "1998-04-02"
        vote_average = 8.7
        poster_path = "/det.jpg"
        overview = "A great movie!"
        genres = [{"name": "Sci-Fi"}]
    monkeypatch.setattr("functions.movie_api.details", lambda mid: MovieObj())
    result = functions.get_movie_details(42)
    assert result["title"] == "TestMov"
    assert result["year"] == "1998"
    assert "Sci-Fi" in result["tags"]

def test_get_movie_details_none(monkeypatch):
    result = functions.get_movie_details(None)
    assert result is None

def test_get_movie_details_error(monkeypatch):
    monkeypatch.setattr("functions.movie_api.details", lambda mid: (_ for _ in ()).throw(Exception("fail")))
    result = functions.get_movie_details(999)
    assert result is None

# --- get_book_details ---
def test_get_book_details_valid(monkeypatch):
    class FakeBook:
        def get(self, k, default=None):
            return {
                "title": "BookTitle",
                "publish_date": 2015,
                "rating": {"average": 4.7},
                "image": "/img.jpg",
                "description": "Great book!",
                "authors": [{"name": "Author1"}, {"name": "Author2"}],
                "id": 22,
            }.get(k, default)
    class FakeApiClient:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): pass
    class FakeDefaultApi:
        def get_book_information(self, bid): return FakeBook()
    monkeypatch.setattr("functions.bigbookapi.ApiClient", lambda cfg: FakeApiClient())
    monkeypatch.setattr("functions.bigbookapi.DefaultApi", lambda api_client: FakeDefaultApi())
    result = functions.get_book_details(22)
    assert result["title"] == "BookTitle"
    assert result["year"] == "2015"
    assert result["kind"] == "Book"
    assert "Author1" in result["tags"]

def test_get_book_details_none():
    result = functions.get_book_details(None)
    assert result is None

def test_get_book_details_error(monkeypatch):
    class FakeApiClient:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): pass
    class FakeDefaultApi:
        def get_book_information(self, bid): raise Exception("fail")
    monkeypatch.setattr("functions.bigbookapi.ApiClient", lambda cfg: FakeApiClient())
    monkeypatch.setattr("functions.bigbookapi.DefaultApi", lambda api_client: FakeDefaultApi())
    result = functions.get_book_details(99)
    assert result is None
