import pyodbc
import bigbookapi
from bigbookapi.rest import ApiException
import os
from pprint import pprint
import csv  # <-- Import the CSV module
import os.path # <-- Import this to check if the file exists

# --- (Fill in your API keys and connection string) ---

# Big Book API Setup
# Make sure to set this environment variable in your terminal
# export BIGBOOK_API_KEY='your_key_goes_here'
book_config = bigbookapi.Configuration(host="https://api.bigbookapi.com")
book_config.api_key['apiKey'] = os.environ.get("BIGBOOK_API_KEY")
book_config.api_key['headerApiKey'] = os.environ.get("BIGBOOK_API_KEY")

# Azure SQL Setup
AZURE_CONNECTION_STRING = "YOUR_AZURE_SQL_CONNECTION_STRING_HERE"

# -----------------------------------------------------

# (Your get_all_book_genres_from_db function is commented out, which is fine)

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
        # Pass the full error message back as the 'title'
        return None, f"API Error for '{genre_name}': {e.body}" 
    except Exception as e:
        return None, f"General Error for '{genre_name}': {e}"


if __name__ == "__main__":
    print("Starting API calls... Results will be saved to top_books_run_1.csv\n")
    
    # This is the list for your first run
    all_book_genres = [
    'text book',  # Fixed
    'thriller',
    'travel',
    'true crime',  # Fixed
    'war',
    'writing',
    'young adult'  # Fixed
]

    output_filename = "top_books_run_1.csv"
    
    # Check if the file already exists so we know whether to write the header
    file_exists = os.path.isfile(output_filename)

    # Open the file in 'append' mode ('a')
    # This creates the file if it doesn't exist, or adds to it if it does.
    # This is the safest way to save your data.
    with open(output_filename, 'a', newline='', encoding='utf-8') as f:
        
        # Create a CSV writer object
        csv_writer = csv.writer(f)
        
        # If the file is new, write the header row
        if not file_exists:
            csv_writer.writerow(["genre", "book_id", "title_or_error"])

        # Loop through your genres
        for genre in all_book_genres:
            book_id, title = get_top_book_for_genre(genre)
            
            # 1. Write the result to the CSV file IMMEDIATELY
            csv_writer.writerow([genre, book_id, title])
            
            # 2. Print to the terminal so you can see the progress
            if book_id:
                print(f"  - SUCCESS: {genre.capitalize()} -> {title} (ID: {book_id})")
            else:
                # This will print the error message (e.g., "No books found")
                print(f"  - FAILED:  {genre.capitalize()} -> {title}")
                
    print(f"\n...Finished. All results saved to {output_filename}")

