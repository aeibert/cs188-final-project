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

    # Decide which function to call
    if input_kind == "movie" and target_kind == "movie":
        data = functions.recommend_movies_from_movie(title)

    elif input_kind == "book" and target_kind == "book":
        data = functions.recommend_books_from_book(title)

    elif input_kind == "movie" and target_kind == "book":
        data = functions.recommend_books_from_movie(title)

    elif input_kind == "book" and target_kind == "movie":
        data = functions.recommend_movies_from_genre_dropdown(title)

    else:
        data = {"error": "Unsupported request"}

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)

