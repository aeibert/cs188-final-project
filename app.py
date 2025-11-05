from flask import Flask, request, jsonify
from services.omdb_service import get_movies_by_genre, get_movie_genres
from services.bigbook_service import get_book_genres, get_similar_books
from database import log_search

app = Flask(__name__)

@app.route("/api/recommend")
def recommend():
    title = request.args.get("title")
    rec_type = request.args.get("type")
    log_search(title, rec_type)  # log into SQL history table

    if rec_type == "book-to-movie":
        genres = get_book_genres(title)
        results = get_movies_by_genre(genres)

    elif rec_type == "movie-to-book":
        genres = get_movie_genres(title)
        results = get_similar_books(genres)

    elif rec_type == "book-to-book":
        results = get_similar_books(title)

    elif rec_type == "movie-to-movie":
        genres = get_movie_genres(title)
        results = get_movies_by_genre(genres)

    else:
        results = []

    return jsonify(results)
