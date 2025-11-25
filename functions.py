import pyodbc
import os
from tmdbv3api import TMDb, Movie, Discover, Search
import bigbookapi
from dotenv import load_dotenv

# --- FIX 1: LOAD ENV VARS CORRECTLY ---
if "WEBSITE_HOSTNAME" not in os.environ:
    # Development environment
    load_dotenv(".secret.env")

# --- CONFIGURATION ---
AZURE_CONN_STRING = os.environ.get("AZURE_SQL_CONNECTIONSTRING")
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
BIGBOOK_API_KEY = os.environ.get("BIGBOOK_API_KEY")

# --- SETUP ---
tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY
movie_api = Movie()
discover_api = Discover()
search_api = Search()

book_config = bigbookapi.Configuration(host="https://api.bigbookapi.com")
book_config.api_key['apiKey'] = BIGBOOK_API_KEY
book_config.api_key['headerApiKey'] = BIGBOOK_API_KEY


def get_db_connection():
    try:
        if not AZURE_CONN_STRING:
            print("Error: AZURE_SQL_CONNECTIONSTRING is not set.")
            return None
        return pyodbc.connect(AZURE_CONN_STRING)
    except Exception as e:
        print(f"Database Connection Error: {e}")
        return None

def format_meta_info(book_data):
    """
    Returns strictly the year (e.g. "1965") or "N/A".
    """
    pub_date = book_data.get('publish_date')
    if pub_date:
        # Convert 1965.0 -> "1965"
        return str(int(pub_date))
    return "N/A"

# ===========================================================================
# RECOMMENDATION FUNCTIONS
# ===========================================================================

def recommend_movies_from_movie(movie_title, number):
    results = []
    try:
        search_results = search_api.movies(movie_title)
        if not search_results: 
            return []
        first_movie = search_results[0]
        recs = movie_api.recommendations(first_movie.id)
        
        for m in list(recs)[:int(number)]:
            results.append({
                "id": m.id,
                "title": m.title,
                "year": m.release_date[:4] if hasattr(m, 'release_date') and m.release_date else "N/A",
                "image": f"https://image.tmdb.org/t/p/w500{m.poster_path}" if m.poster_path else "/static/images/image-not-available.jpg",
                "kind": "Movie"
            })
    except Exception as e:
        print(f"Error in Movie->Movie: {e}")
    return results

def recommend_books_from_book(book_title, number):
    results = []
    try:
        with bigbookapi.ApiClient(book_config) as api_client:
            api_instance = bigbookapi.DefaultApi(api_client)
            search_res = api_instance.search_books(query=book_title, number=1)
            
            if search_res.get('books') and len(search_res['books'][0]) > 0:
                book_id = search_res['books'][0][0].get('id')
                similar_res = api_instance.find_similar_books(book_id, number=int(number))
                
                if similar_res.get('similar_books'):
                    for b in similar_res['similar_books']:
                        # Extra call for details
                        try:
                            details = api_instance.get_book_information(b.get('id'))
                            meta_text = format_meta_info(details)
                        except Exception:
                            meta_text = "N/A"

                        results.append({
                            "id": b.get('id'),
                            "title": b.get('title'),
                            "year": meta_text,
                            "image": b.get('image') or "/static/images/image-not-available.jpg",
                            "kind": "Book"
                        })
    except Exception as e:
        print(f"Error in Book->Book: {e}")
    return results

def recommend_books_from_movie(movie_title, number):
    results = []
    conn = get_db_connection()
    if not conn: 
        return []
    try:
        search_results = search_api.movies(movie_title)
        if not search_results: 
            return []
        movie_details = movie_api.details(search_results[0].id)
        if not movie_details.genres: 
            return []
        tmdb_id = movie_details.genres[0]['id']
        
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 1 BookGenreName FROM GenreMap WHERE TMDbGenreID = ?", (tmdb_id,))
        row = cursor.fetchone()
        
        if row:
            book_genre_name = row[0]
            with bigbookapi.ApiClient(book_config) as api_client:
                api_instance = bigbookapi.DefaultApi(api_client)
                book_recs = api_instance.search_books(genres=book_genre_name, sort='rating', number=int(number))
                
                if book_recs.get('books'):
                    for group in book_recs['books']:
                        if group:
                            b = group[0]
                            results.append({
                                "id": b.get('id'),
                                "title": b.get('title'),
                                "year": format_meta_info(b),
                                "image": b.get('image') or "/static/images/image-not-available.jpg",
                                "kind": "Book"
                            })
    except Exception as e:
        print(f"Error in Movie->Book: {e}")
    finally:
        conn.close()
    return results

def recommend_movies_from_genre_dropdown(selected_genre, number):
    results = []
    conn = get_db_connection()
    if not conn: 
        return []
    try:
        genre_clean = selected_genre.lower().strip()
        cursor = conn.cursor()
        cursor.execute("SELECT TMDbGenreID FROM GenreMap WHERE BookGenreName = ?", (genre_clean,))
        row = cursor.fetchone()
        
        if row:
            tmdb_id = row[0]
            recs = discover_api.discover_movies({'with_genres': tmdb_id, 'sort_by': 'popularity.desc'})
            for m in list(recs)[:int(number)]:
                results.append({
                    "id": m.id,
                    "title": m.title,
                    "year": m.release_date[:4] if hasattr(m, 'release_date') and m.release_date else "N/A",
                    "image": f"https://image.tmdb.org/t/p/w500{m.poster_path}" if m.poster_path else "/static/images/image-not-available.jpg",
                    "kind": "Movie"
                })
    except Exception as e:
        print(f"Error in Book->Movie: {e}")
    finally:
        conn.close()
    return results

def get_popular_movies():
    results = []
    try:
        popular = movie_api.popular()
        for p in list(popular)[:4]:
            results.append({
                "id": p.id,
                "title": p.title,
                "year": p.release_date[:4] if hasattr(p, 'release_date') and p.release_date else "N/A",
                "rating": p.vote_average,
                "poster": f"https://image.tmdb.org/t/p/w500{p.poster_path}" if p.poster_path else "/static/images/image-not-available.jpg",
                "kind": "Movie"
            })
    except Exception as e:
        print(f"Error getting popular movies: {e}")
    return results

# ===========================================================================
# DETAIL FUNCTIONS
# ===========================================================================

def get_movie_details(movie_id):
    try:
        if not movie_id: 
            return None
        m = movie_api.details(movie_id)
        return {
            "title": m.title,
            "year": m.release_date[:4] if hasattr(m, 'release_date') and m.release_date else "N/A",
            "rating": str(m.vote_average) if hasattr(m, 'vote_average') else "N/A",
            "poster": f"https://image.tmdb.org/t/p/w500{m.poster_path}" if m.poster_path else "/static/images/image-not-available.jpg",
            "desc": m.overview,
            "kind": "Movie",
            "tags": [g['name'] for g in m.genres] if m.genres else []
        }
    except Exception as e:
        print(f"Error getting movie details: {e}")
        return None

def get_book_details(book_id):
    try:
        # Ensure ID is not empty
        if not book_id: 
            return None

        with bigbookapi.ApiClient(book_config) as api_client:
            api = bigbookapi.DefaultApi(api_client)
            
            try:
                numeric_id = int(float(book_id))
            except ValueError:
                print(f"Error: ID '{book_id}' is not a valid number.")
                return None
                
            b = api.get_book_information(numeric_id)
            # -------------------
            
            year = "N/A"
            if b.get('publish_date'):
                year = str(int(b['publish_date']))
                
            rating = "N/A"
            if b.get('rating') and b['rating'].get('average'):
                rating = str(round(b['rating']['average'] * 10, 1))

            tags = [a['name'] for a in b.get('authors', [])]

            return {
                "title": b.get('title'),
                "year": year,
                "rating": rating,
                "poster": b.get('image') or "/static/images/image-not-available.jpg",
                "desc": b.get('description') or "No description available.",
                "kind": "Book",
                "tags": tags
            }
    except Exception as e:
        print(f"Error getting book details: {e}")
        return None