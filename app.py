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
    # Get the data before loading the page
    popular_movies = functions.get_popular_movies()
    return render_template("index.html", featured_movies=popular_movies)

@app.route("/recommend")
def recommend():
    #Get all data from the form
    input_kind = request.args.get("inputKind")
    target_kind = request.args.get("targetKind")
    title = request.args.get("q")
    genre = request.args.get("genre")
    limit = int(request.args.get("limit", 4)) # convert to int so we can pass it to the functions

    results = []
    error = None

    if input_kind == "movie" and target_kind == "movie":
        results = functions.recommend_movies_from_movie(title, limit)

    elif input_kind == "book" and target_kind == "book":
        results = functions.recommend_books_from_book(title, limit)

    elif input_kind == "movie" and target_kind == "book":
        results = functions.recommend_books_from_movie(title, limit)

    elif input_kind == "book" and target_kind == "movie":
        if genre:
            results = functions.recommend_movies_from_genre_dropdown(genre, limit)
        else:
            results = []

    final_results = results[:limit] if results else []

    return render_template(
        "results.html", 
        recommendations=final_results,
        error=error,
        q=title,
        genre=genre,
        input_kind=input_kind,
        target_kind=target_kind,
        limit=limit
    )

@app.route("/detail")
def detail():
    item_id = request.args.get("id")
    kind = request.args.get("kind") # "movie" or "book"
    
    data = None
    if kind and kind.lower() == "movie":
        data = functions.get_movie_details(item_id)
    elif kind and kind.lower() == "book":
        data = functions.get_book_details(item_id)
        
    if not data:
        return "Item not found", 404

    return render_template("detail.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)

