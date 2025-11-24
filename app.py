from flask import Flask, render_template, request, jsonify
import pyodbc
import functions  # <-- logic file
from functions import AZURE_CONN_STRING

app = Flask(__name__)

def get_db_connection():
    connection = pyodbc.connect(AZURE_CONN_STRING)
    return connection

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recommend")
def recommend():
    # 1. Get data from the form
    input_kind = request.args.get("inputKind")   # "book" or "movie"
    target_kind = request.args.get("targetKind") # "book" or "movie"
    title = request.args.get("q")                # e.g., "Dune"
    genre = request.args.get("genre")            # e.g., "fantasy"
    limit = int(request.args.get("limit", 4))    # Default to 4 if missing

    results = []

    # 2. Call the correct function based on inputs
    if input_kind == "movie" and target_kind == "movie":
        results = functions.recommend_movies_from_movie(title)

    elif input_kind == "book" and target_kind == "book":
        results = functions.recommend_books_from_book(title)

    elif input_kind == "movie" and target_kind == "book":
        results = functions.recommend_books_from_movie(title)

    elif input_kind == "book" and target_kind == "movie":
        # In this mode, we use the genre dropdown, NOT the title input
        if genre:
            results = functions.recommend_movies_from_genre_dropdown(genre)
        else:
            # Fallback if they didn't pick a genre
            results = []

    # 3. Apply the limit (slice the list)
    final_results = results[:limit]

    # 4. Render the results page with the data
    return render_template("results.html", recommendations=final_results)

if __name__ == "__main__":
    app.run(debug=True)

