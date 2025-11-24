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

@app.route("/recommend", methods=["GET"])
def recommend():
    input_kind = request.args.get("inputKind")
    target_kind = request.args.get("targetKind")
    title = request.args.get("q")
    # Get 'number' from query args, default to 5 if not supplied or invalid
    try:
        number = int(request.args.get("number", 5))
        if number < 1:
            number = 5
    except (TypeError, ValueError):
        number = 5

    # Decide which function to call
    if input_kind == "movie" and target_kind == "movie":
        data = functions.recommend_movies_from_movie(title, number)
    elif input_kind == "book" and target_kind == "book":
        data = functions.recommend_books_from_book(title, number)
    elif input_kind == "movie" and target_kind == "book":
        data = functions.recommend_books_from_movie(title, number)
    elif input_kind == "book" and target_kind == "movie":
        # This matches functions.py def recommend_movies_from_book(selected_genre, number)
        data = functions.recommend_movies_from_book(title, number)
    else:
        data = {"error": "Unsupported request"}

    # Ensure response is JSON serializable
    return jsonify(data if data is not None else {})

if __name__ == "__main__":
    app.run(debug=True)

