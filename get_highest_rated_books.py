import pyodbc
import bigbookapi
from bigbookapi.rest import ApiException
import os
from pprint import pprint

# --- (Fill in your API keys and connection string) ---

# Big Book API Setup
book_config = bigbookapi.Configuration(host="https://api.bigbookapi.com")
book_config.api_key['apiKey'] = os.environ.get("BIGBOOK_API_KEY")
book_config.api_key['headerApiKey'] = os.environ.get("BIGBOOK_API_KEY")
# Azure SQL Setup
AZURE_CONNECTION_STRING = "YOUR_AZURE_SQL_CONNECTION_STRING_HERE"

# -----------------------------------------------------

def get_all_book_genres_from_db():
    """
    Queries your Azure SQL 'GenreMap' table and returns a list
    of all unique book genre names.
    """
    sql_query = "SELECT BookGenreName FROM GenreMap"
    genre_list = []
    
    try:
        conn = pyodbc.connect(AZURE_CONNECTION_STRING)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        
        # Create a list from the first column of each row
        genre_list = [row[0] for row in rows]
            
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            
    return genre_list

def get_top_book_for_genre(genre_name):
    """
    Calls the Big Book API to find the #1 highest-rated book
    for a given genre.
    """
    try:
        with bigbookapi.ApiClient(book_config) as api_client:
            api_instance = bigbookapi.DefaultApi(api_client)
            
            api_response = api_instance.search_books(
                genres=genre_name,
                sort='rating',  # Sort by highest rating
                number=1        # We only want the top one
            )
            
            # Check if we got a result
            if api_response.get('books') and len(api_response['books'][0]) > 0:
                book_data = api_response['books'][0][0]
                return book_data.get('id'), book_data.get('title')
            else:
                return None, f"No books found for '{genre_name}'"
                
    except ApiException as e:
        return None, f"API Error for '{genre_name}': {e}"


if __name__ == "__main__":
    print("Finding the top-rated book for a few test genres...\n")
    all_book_genres = [
    'action',
    'adventure',
    'anthropology',
    'astronomy',
    'archaeology',
    'architecture',
    'art',
    'aviation',
    'biography',
    'biology',
    'business',
    'chemistry',
    'children',
    'classics',
    'contemporary',
    'cookbook',
    'crafts',
    'crime',
    'dystopia',
    'economics',
    'education',
    'engineering',
    'environment',
    'erotica',
    'essay',
    'fairy tales',  # Fixed
    'fantasy',
    'fashion',
    'feminism',
    'fiction',
    'finance',
    'folklore',
    'food',
    'gaming',
    'gardening',
    'geography',
    'geology',
    'graphic novel',  # Fixed
    'health',
    'historical',
    'historical fiction',  # Fixed
    'history',
    'horror',
    'how to',  # Fixed
    'humor',
    'inspirational',
    'journalism',
    'law',
    'literary fiction',  # Fixed
    'literature',
    'magical realism',  # Fixed
    'manga',
    'martial arts',  # Fixed
    'mathematics',
    'medicine',
    'medieval',
    'memoir',
    'mystery',
    'mythology',
    'nature',
    'nonfiction',
    'novel',
    'occult',
    'paranormal',
    'parenting',
    'philosophy',
    'physics',
    'picture book',  # Fixed
    'poetry',
    'politics',
    'programming',
    'psychology',
    'reference',
    'relationships',
    'religion',
    'romance',
    'science and technology',  # Fixed
    'science fiction',  # Fixed
    'self help',  # Fixed
    'short stories',  # Fixed
    'society',
    'sociology',
    'space',
    'spirituality',
    'sports',
    'text book',  # Fixed
    'thriller',
    'travel',
    'true crime',  # Fixed
    'war',
    'writing',
    'young adult'  # Fixed
]
    # --- To run all genres (NOT RECOMMENDED ON FREE TIER) ---
    #
    # print("Fetching all genres from SQL... (This may take a while)")
    # all_genres = get_all_book_genres_from_db()
    # print(f"Found {len(all_genres)} genres. Starting API calls...")
    #
    # for genre in all_genres: 
    #     book_id, title = get_top_book_for_genre(genre)
    #     ...
    # --------------------------------------------------------

    for genre in all_book_genres:
        book_id, title = get_top_book_for_genre(genre)
        
        if book_id:
            print(f"  - {genre.capitalize()}: {title} (ID: {book_id})")
        else:
            print(f"  - {genre.capitalize()}: {title}") # This will print the error (e.g., "No books found")