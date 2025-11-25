import pyodbc
import os
from tmdbv3api import TMDb, Movie, Discover, Search
import bigbookapi
from dotenv import load_dotenv

if "WEBSITE_HOSTNAME" not in os.environ:
    # Development
    load_dotenv(".secret.env")

# --- CONFIGURATION ---------------------------------------------------------
# Azure SQL Connection String
AZURE_CONN_STRING = os.environ.get("AZURE_SQL_CONNECTIONSTRING")


# --- SETUP -----------------------------------------------------------------
# TMDb Setup
tmdb = TMDb()
tmdb.api_key = os.environ.get("TMDB_API_KEY")
movie_api = Movie()
discover_api = Discover()
search_api = Search()

# Big Book API Setup
book_config = bigbookapi.Configuration(host="https://api.bigbookapi.com")
book_config.api_key['apiKey'] = os.environ.get("BIGBOOK_API_KEY")
book_config.api_key['headerApiKey'] = os.environ.get("BIGBOOK_API_KEY")
# ---------------------------------------------------------------------------

def get_db_connection():
    """Helper function to connect to Azure SQL"""
    try:
        return pyodbc.connect(AZURE_CONN_STRING)
    except Exception as e:
        print(f"Database Connection Error: {e}")
        return None

# ===========================================================================
# FLOW 1: MOVIE -> MOVIE (Using TMDb Built-in)
# ===========================================================================
def recommend_movies_from_movie(movie_title,number):
    results = []
    try:
        search_results = search_api.movies(movie_title)
        if not search_results: return []

        first_movie = search_results[0]
        recs = movie_api.recommendations(first_movie.id)
        
        target_list = list(recs)[:int(number)]
        for m in target_list: # removed slicing here to handle it in app.py
            results.append({
                "title": m.title,
                "year": m.release_date[:4] if hasattr(m, 'release_date') and m.release_date else "N/A",
                "image": f"https://image.tmdb.org/t/p/w500{m.poster_path}" if m.poster_path else "/static/images/image-not-available.jpg",
                "kind": "Movie"
            })
    except Exception as e:
        print(f"Error: {e}")
    return results

# ===========================================================================
# FLOW 2: BOOK -> BOOK (Using Big Book API Built-in)
# ===========================================================================
def recommend_books_from_book(book_title, number):
    results = []
    try:
        with bigbookapi.ApiClient(book_config) as api_client:
            api_instance = bigbookapi.DefaultApi(api_client)
            # 1. Find the source book ID
            search_res = api_instance.search_books(query=book_title, number=1)
            
            if search_res.get('books') and len(search_res['books'][0]) > 0:
                book_id = search_res['books'][0][0].get('id')
                
                # 2. Get similar books (Returns minimal data: ID, Title, Image)
                similar_res = api_instance.find_similar_books(book_id, number=int(number))
                
                if similar_res.get('similar_books'):
                    for b in similar_res['similar_books']:
                        
                        # --- CRITICAL: EXTRA API CALL ---
                        # Since find_similar_books DOESN'T give us rating/year,
                        # we MUST ask for it specifically for each book.
                        try:
                            details = api_instance.get_book_information(b.get('id'))
                            meta_text = format_year(details) # Use the detailed info
                        except:
                            meta_text = "Similar Book" # Fallback if call fails
                        # -------------------------------

                        results.append({
                            "title": b.get('title'),
                            "year": meta_text,
                            "image": b.get('image') or "/static/images/image-not-available.jpg",
                            "kind": "Book"
                        })
    except Exception as e:
        print(f"Error: {e}")
    return results
# ===========================================================================
# FLOW 3: MOVIE -> BOOK (The "Reverse" Logic)
# 1. Get Movie Genre -> 2. Find matching Book Genre in SQL -> 3. Search Books
# ===========================================================================
def recommend_books_from_movie(movie_title, number):
    results = []
    conn = get_db_connection()
    if not conn: return []

    try:
        search_results = search_api.movies(movie_title)
        if not search_results: return []
        
        movie_details = movie_api.details(search_results[0].id)
        if not movie_details.genres: return []
            
        tmdb_id = movie_details.genres[0]['id']
        
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 1 BookGenreName FROM GenreMap WHERE TMDbGenreID = ?", (tmdb_id,))
        row = cursor.fetchone()
        
        if row:
            book_genre_name = row[0]
            with bigbookapi.ApiClient(book_config) as api_client:
                api_instance = bigbookapi.DefaultApi(api_client)
                
                # Search for books by genre (Returns RICH data: ID, Title, Image, Rating, Year!)
                book_recs = api_instance.search_books(
                    genres=book_genre_name, 
                    sort='rating', 
                    number=int(number)
                )
                
                if book_recs.get('books'):
                    for group in book_recs['books']:
                        if group:
                            b = group[0]
                            
                            # --- NO EXTRA CALL NEEDED! ---
                            # The 'search_books' endpoint already gave us the rating/year!
                            meta_text = format_year(b)
                            # -----------------------------

                            results.append({
                                "title": b.get('title'),
                                "year": meta_text,
                                "image": b.get('image') or "/static/images/image-not-available.jpg",
                                "kind": "Book"
                            })
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
    return results

# ===========================================================================
# FLOW 4: BOOK (Genre) -> MOVIE (The "Dropdown" Logic)
# 1. User picks Genre -> 2. Find TMDb ID in SQL -> 3. Discover Movies
# ===========================================================================
def recommend_movies_from_book(selected_genre, number):
    results = []
    conn = get_db_connection()
    if not conn: return []

    try:
        genre_clean = selected_genre.lower().strip()
        cursor = conn.cursor()
        cursor.execute("SELECT TMDbGenreID FROM GenreMap WHERE BookGenreName = ?", (genre_clean,))
        row = cursor.fetchone()
        
        if row:
            tmdb_id = row[0]
            recs = discover_api.discover_movies({'with_genres': tmdb_id, 'sort_by': 'popularity.desc'})
            
            # Slice the list using 'number'
            target_list = list(recs)[:int(number)]
            
            for m in target_list:
                results.append({
                    "title": m.title,
                    "year": m.release_date[:4] if hasattr(m, 'release_date') and m.release_date else "N/A",
                    "image": f"https://image.tmdb.org/t/p/w500{m.poster_path}" if m.poster_path else "/static/images/image-not-available.jpg",
                    "kind": "Movie"
                })
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
    return results

def format_year(book_data):
    """
    Helper to extract and format only the Year from a book object.
    Returns a string like "2023" or "N/A"
    """
    # 1. Get Year
    pub_date = book_data.get('publish_date')
    
    if pub_date:
        # Convert 1965.0 -> "1965" and return it directly as a string
        return str(int(pub_date))
        
    # If no date is found, return a fallback string
    return "N/A"

# =================================== GET POPULAR MOVIES FOR EXPLORE PAGE ========================================

def get_popular_movies():
    movie = Movie()

    popular = movie.popular()

    for p in list(popular)[:4]:
        print("Title:", p.title)
        print("Poster Path:", p.poster_path)
        print("Popularity Rating:", p.popularity)
        print("Release Date:", p.release_date)

# ===========================================================================
# MAIN EXECUTION
# ===========================================================================
if __name__ == "__main__":
    # Test 1: Movie -> Movie
    recommend_movies_from_movie("The Matrix",2)

    # # Test 2: Book -> Book
    #recommend_books_from_book("Dune",3)

    # # Test 3: Movie -> Book (Reverse Lookup), need to be connected to Azure SQL
    #recommend_books_from_movie("The Notebook", 4) 

    # # Test 4: Book -> Movie (Dropdown Input), need to be connected to Azure SQL
    # # This simulates the user selecting "fantasy" from your dropdown
    #recommend_movies_from_book("fantasy",2)


    #For explore page at beginning
    #get_popular_movies()
    