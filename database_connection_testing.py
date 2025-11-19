import pyodbc
import os
from tmdbv3api import TMDb, Genre, Discover
import bigbookapi # Your local package
from pprint import pprint
import os


# --- API SETUPS (Fill these in) --------------------------------
tmdb = TMDb()
tmdb.api_key = ''
discover = Discover()

book_config = bigbookapi.Configuration(host="https://api.bigbookapi.com")
book_config.api_key['apiKey'] = os.environ.get("BIGBOOK_API_KEY")
book_config.api_key['headerApiKey'] = os.environ.get("BIGBOOK_API_KEY")
# ---------------------------------------------------------------


def get_tmdb_genre_id(book_genre_name):
    """
    Connects to the Azure SQL database.
    (This function is already correct and needs no changes)
    """
    connection_string = os.environ["AZURE_SQL_CONNECTIONSTRING"]
    
    # 1. GET THIS FROM THE AZURE PORTAL
    # It will look something like: 
    # 'driver={ODBC Driver 18 for SQL Server};server=tcp:your-server-name.database.windows.net,1433;...'
    connection_string = os.environ["AZURE_SQL_CONNECTIONSTRING"]
    
    # 2. THIS IS YOUR SQL QUERY
    sql_query = "SELECT MovieGenre FROM Genre WHERE BookGenre = ?"
    # This query is perfect for your new GenreMap table
    sql_query = "SELECT TMDbGenreID FROM GenreMap WHERE BookGenreName = ?"
    
    tmdb_id = None
    
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute(sql_query, (book_genre_name,))
        row = cursor.fetchone()
        if row:
            tmdb_id = row[0]
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            
    return tmdb_id


# --- MAIN WORKFLOW (With the fix) -----------------------------
def get_movie_recs_from_book(book_title):
    try:
        # STEP 1: Find the book's genres
        with bigbookapi.ApiClient(book_config) as api_client:
            book_api = bigbookapi.DefaultApi(api_client)
            search_response = book_api.search_books(query=book_title, number=1)
            
            if not (search_response.get('books') and len(search_response['books'][0]) > 0):
                print(f"Book '{book_title}' not found.")
                return

            book_id = search_response['books'][0][0].get('id')
            
            # --- THIS IS THE DIAGNOSTIC PART ---
            print(f"\n--- Getting full info for book ID: {book_id} ---")
            book_info = book_api.get_book_information(book_id)
            
            print("\n--- FULL BOOK INFO RESPONSE (DEBUGGING) ---")
            pprint(book_info)
            print("-------------------------------------------\n")
            # --- END DIAGNOSTIC PART ---

            # Look at the output above. 
            # Find the list of genres and see what its key is.
            # I will check for 'genres' first, then 'subjects'.
            
            book_genre_list = None
            if book_info.get('genres'):
                book_genre_list = book_info.get('genres')
            elif book_info.get('subjects'):
                book_genre_list = book_info.get('subjects')
            
            if not book_genre_list:
                print(f"Book '{book_title}' has no genres or subjects listed.")
                return

            # Get the first genre (e.g., "Science Fiction")
            book_genre_from_api = book_genre_list[0]
            print(f"Found book genre: {book_genre_from_api}")

            book_genre_to_query = book_genre_from_api.lower().strip()

        # STEP 2: Translate the genre using your Azure SQL Database
        print(f"Connecting to SQL to look for: '{book_genre_to_query}'")
        tmdb_genre_id = get_tmdb_genre_id(book_genre_to_query)
        
        if not tmdb_genre_id:
            print(f"Genre '{book_genre_to_query}' not found in your SQL GenreMap.")
            return

        print(f"Found TMDb ID: {tmdb_genre_id}")

        # STEP 3: Discover movies with that genre ID
        print("Finding popular movies with that genre...")
        recommendations = discover.discover_movies({
            'with_genres': tmdb_genre_id,
            'sort_by': 'popularity.desc'
        })
        
        print("\n--- MOVIE RECOMMENDATIONS ---")
        for i, movie in enumerate(list(recommendations)[:5]): # Get top 5
            print(f"  {i+1}. {movie.title} (Popularity: {movie.popularity})")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    get_movie_recs_from_book("Dune")