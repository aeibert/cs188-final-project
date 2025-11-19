from flask import Flask, request, jsonify
from services.omdb_service import get_movies_by_genre, get_movie_genres
from services.bigbook_service import get_book_genres, get_similar_books
import pyodbc
from database_search import log_search
from config import CONNECTION_STRING

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

@app.route("/api/history")
def history():
    conn = pyodbc.connect(CONNECTION_STRING)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TOP 50 title, search_type, timestamp
        FROM SearchHistory
        ORDER BY timestamp DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    history = [
        {
            "title": row[0],
            "type": row[1],
            "timestamp": row[2].isoformat()
        }
        for row in rows
    ]

    return jsonify(history)

