from flask import Flask, render_template, request
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
    # 1. Get all data from the form
    input_kind = request.args.get("inputKind")
    target_kind = request.args.get("targetKind")
    title = request.args.get("q")
    genre = request.args.get("genre")
    
    # --- FIX IS HERE: Get the 'limit' (show) value ---
    # We convert it to an int so we can pass it to your function
    limit = int(request.args.get("limit", 4)) 

    results = []

    # 2. Call the functions, PASSING THE LIMIT
    if input_kind == "movie" and target_kind == "movie":
        # Pass 'limit' as the second argument here!
        results = functions.recommend_movies_from_movie(title, limit)

    elif input_kind == "book" and target_kind == "book":
        results = functions.recommend_books_from_book(title, limit)

    elif input_kind == "movie" and target_kind == "book":
        results = functions.recommend_books_from_movie(title, limit)

    elif input_kind == "book" and target_kind == "movie":
        if genre:
            results = functions.recommend_movies_from_book(genre, limit)
        else:
            results = []

    return render_template(
        "results.html", 
        recommendations=results,
        q=title,
        genre=genre,
        input_kind=input_kind,
        target_kind=target_kind,
        limit=limit
    )

if __name__ == "__main__":
    app.run(debug=True)

