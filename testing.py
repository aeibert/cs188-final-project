import pyodbc
import os
from tmdbv3api import TMDb, Movie, Discover, Search
import bigbookapi
from bigbookapi.rest import ApiException
from dotenv import load_dotenv
load_dotenv(".secret.env")  # <--- This loads the variables from .env

# --- CONFIGURATION ---------------------------------------------------------
# 1. API KEYS
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
BIGBOOK_API_KEY = os.environ.get("BIGBOOK_API_KEY")

# 2. AZURE CONNECTION STRING
AZURE_CONN_STRING = os.environ.get("AZURE_SQL_CONNECTIONSTRING")


# --- SETUP -----------------------------------------------------------------
# TMDb Setup
tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY
movie_api = Movie()
discover_api = Discover()
search_api = Search()

# Big Book API Setup
book_config = bigbookapi.Configuration(host="https://api.bigbookapi.com")
book_config.api_key['apiKey'] = BIGBOOK_API_KEY
book_config.api_key['headerApiKey'] = BIGBOOK_API_KEY
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
def recommend_movies_from_movie(movie_title):
    print(f"\n--- 1. Movie to Movie: '{movie_title}' ---")
    try:
        # 1. Find the movie ID
        search_results = search_api.movies(movie_title)
        if not search_results:
            print(f"Movie '{movie_title}' not found.")
            return

        first_movie = search_results[0]
        print(f"Found Source Movie: {first_movie.title} (ID: {first_movie.id})")

        # 2. Get recommendations
        recommendations = movie_api.recommendations(first_movie.id)
        
        print("Recommendations:")
        for i, m in enumerate(list(recommendations)[:5]):
            print(f"  {i+1}. {m.title}")

    except Exception as e:
        print(f"Error in Movie->Movie: {e}")

# ===========================================================================
# FLOW 2: BOOK -> BOOK (Using Big Book API Built-in)
# ===========================================================================
def recommend_books_from_book(book_title):
    print(f"\n--- 2. Book to Book: '{book_title}' ---")
    try:
        with bigbookapi.ApiClient(book_config) as api_client:
            api_instance = bigbookapi.DefaultApi(api_client)
            
            # 1. Find the book ID
            search_res = api_instance.search_books(query=book_title, number=1)
            if not (search_res.get('books') and len(search_res['books'][0]) > 0):
                print(f"Book '{book_title}' not found.")
                return

            book_id = search_res['books'][0][0].get('id')
            print(f"Found Source Book ID: {book_id}")

            # 2. Get similar books
            similar_res = api_instance.find_similar_books(book_id, number=5)
            
            print("Recommendations:")
            if similar_res.get('similar_books'):
                for i, b in enumerate(similar_res['similar_books']):
                    print(f"  {i+1}. {b.get('title')}")
            else:
                print("  No similar books found.")

    except Exception as e:
        print(f"Error in Book->Book: {e}")

# ===========================================================================
# FLOW 3: MOVIE -> BOOK (The "Reverse" Logic)
# 1. Get Movie Genre -> 2. Find matching Book Genre in SQL -> 3. Search Books
# ===========================================================================
def recommend_books_from_movie(movie_title):
    print(f"\n--- 3. Movie to Book: '{movie_title}' ---")
    conn = get_db_connection()
    if not conn: return

    try:
        # 1. Get Movie Details to find Genre ID
        search_results = search_api.movies(movie_title)
        if not search_results:
            print("Movie not found.")
            return
        
        # We need detailed info to get genres
        movie_details = movie_api.details(search_results[0].id)
        if not movie_details.genres:
            print("No genres found for this movie.")
            return
            
        # Take the first genre (e.g., 878 for Sci-Fi)
        first_tmdb_genre = movie_details.genres[0]
        tmdb_id = first_tmdb_genre['id']
        tmdb_name = first_tmdb_genre['name']
        print(f"Movie Genre: {tmdb_name} (ID: {tmdb_id})")

        # 2. Query SQL to convert TMDb ID -> Book Genre Name
        # We pick the first matching book genre from our map
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 1 BookGenreName FROM GenreMap WHERE TMDbGenreID = ?", (tmdb_id,))
        row = cursor.fetchone()
        
        if not row:
            print(f"No mapping found in SQL for TMDb ID {tmdb_id}")
            return
            
        book_genre_name = row[0]
        print(f"Mapped to Book Genre: '{book_genre_name}'")

        # 3. Search for popular books in that genre
        with bigbookapi.ApiClient(book_config) as api_client:
            api_instance = bigbookapi.DefaultApi(api_client)
            book_recs = api_instance.search_books(
                genres=book_genre_name, 
                sort='rating', 
                number=5
            )
            
            print("Book Recommendations:")
            if book_recs.get('books'):
                for i, group in enumerate(book_recs['books']):
                    if group:
                        book = group[0]
                        title = book.get('title')
                        
                        # --- CALL THE HELPER FUNCTION HERE ---
                        cover_url = get_book_cover_url(book)
                        # -------------------------------------
                        
                        print(f"  {i+1}. {title}")
                        print(f"     Cover: {cover_url}")
                        print("-" * 30)
                # for i, group in enumerate(book_recs['books']):
                #     if group:
                #         print(f"  {i+1}. {group[0].get('title')}")

    except Exception as e:
        print(f"Error in Movie->Book: {e}")
    finally:
        conn.close()

# ===========================================================================
# FLOW 4: BOOK (Genre) -> MOVIE (The "Dropdown" Logic)
# 1. User picks Genre -> 2. Find TMDb ID in SQL -> 3. Discover Movies
# ===========================================================================
def recommend_movies_from_genre_dropdown(selected_genre):
    print(f"\n--- 4. Book (Dropdown) to Movie: Genre '{selected_genre}' ---")
    conn = get_db_connection()
    if not conn: return

    try:
        # 1. Look up the TMDb ID for the selected genre
        # We normalize to lowercase just in case
        genre_clean = selected_genre.lower().strip()
        
        cursor = conn.cursor()
        cursor.execute("SELECT TMDbGenreID FROM GenreMap WHERE BookGenreName = ?", (genre_clean,))
        row = cursor.fetchone()
        
        if not row:
            print(f"Genre '{selected_genre}' not found in database.")
            return
            
        tmdb_id = row[0]
        print(f"Found TMDb ID: {tmdb_id}")

        # 2. Discover Movies
        recs = discover_api.discover_movies({
            'with_genres': tmdb_id,
            'sort_by': 'popularity.desc'
        })
        
        print("Movie Recommendations:")
        for i, m in enumerate(list(recs)[:5]):
            print(f"  {i+1}. {m.title}")

    except Exception as e:
        print(f"Error in Book->Movie: {e}")
    finally:
        conn.close()


# =================================== GET POSTER ========================================
def get_movie_posters(movie_title):
    print(f"\n--- Finding Recommendations & Posters for: '{movie_title}' ---")
    
    # 1. Find the source movie
    search_results = search_api.movies(movie_title)
    if not search_results:
        print("Movie not found.")
        return

    first_movie = search_results[0]
    print(f"Source: {first_movie.title}")
    
    # 2. Get recommendations (The poster path is INSIDE these results)
    recommendations = movie_api.recommendations(first_movie.id)
    
    print("\n--- Recommended Movies & Posters ---")
    
    # We'll just look at the top 3
    for i, m in enumerate(list(recommendations)[:3]):
        title = m.title
        poster_path = m.poster_path
        
        if poster_path:
            # CONSTRUCT THE FULL URL
            # w500 is a good size for web apps. You can also use 'w200', 'w300', 'original'
            full_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            
            print(f"{i+1}. {title}")
            print(f"   Image Link: {full_poster_url}")
        else:
            print(f"{i+1}. {title}")
            print("   (No poster available)")
        print("-" * 40)



def get_book_cover_url(book_data):
    """
    Extracts the best available cover URL for a book.
    Prioritizes the direct 'image' link (Cover ID) to avoid rate limits.
    Falls back to ISBN if necessary.
    """
    # 1. BEST OPTION: Use the direct link provided by Big Book API
    # This usually looks like: https://covers.openlibrary.org/b/id/12345-M.jpg
    # This uses the "Cover ID" which is NOT rate-limited.
    if book_data.get('image'):
        return book_data.get('image')

    # 2. FALLBACK OPTION: Construct URL using ISBN
    # This is rate-limited to 100 requests / 5 mins.
    identifiers = book_data.get('identifiers')
    if identifiers:
        # Try ISBN-13 first, then ISBN-10
        isbn = identifiers.get('isbn_13') or identifiers.get('isbn_10')
        
        if isbn:
            # Construct the URL manually as per Open Library docs
            return f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"

    # 3. No cover found
    return "https://via.placeholder.com/128x192?text=No+Cover"

# ===========================================================================
# MAIN EXECUTION
# ===========================================================================
if __name__ == "__main__":
    # Test 1: Movie -> Movie
    #recommend_movies_from_movie("The Matrix")

    # Test 2: Book -> Book
    
    #recommend_books_from_book("Dune")

    # Test 3: Movie -> Book (Reverse Lookup)
    recommend_books_from_movie("The Notebook") 

    # Test 4: Book -> Movie (Dropdown Input)
    # This simulates the user selecting "fantasy" from your dropdown
    #recommend_movies_from_genre_dropdown("fantasy")

    #Test Poster Function
    #get_movie_posters("The Matrix")