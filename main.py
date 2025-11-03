import omdb

def main():
    # --- Configuration ---
    # 1. This is the most important step!
    #    Manually re-type your key inside the quotes.
    #    Do NOT copy-paste it from your old file.
    API_KEY = '35a0d4cf'  # <-- RE-TYPE THIS KEY
   
    try:
        omdb.set_default('apikey', API_KEY)
    except Exception as e:
        print(f"Error setting API key: {e}")
        print("Please check for invisible characters or typos in your key.")
        return # Stop if the key is bad

    try:
        # --- Test 1: Get a specific movie ---
        # Use .get() for a single, detailed result
        print("--- Searching for a specific movie ---")
        movie = omdb.get(title='The Matrix', fullplot=True, tomatoes=True)
        
        if movie:
            print(f"Title: {movie.get('title')}")
            print(f"Year: {movie.get('year')}")
            print(f"Genre: {movie.get('genre')}")
            print(f"Plot: {movie.get('plot')}")
        else:
            print("Movie not found!")

        print("\n" + "="*30 + "\n")

        # --- Test 2: Search for multiple movies ---
        # Use .search() for a list of results
        print("--- Searching for a term ---")
        results = omdb.search(string='Star Wars')
        
        if results:
            print(f"Found {len(results)} results:")
            for item in results:
                print(f"- {item.get('title')} ({item.get('year')})")
        else:
            print("No results found.")

    except Exception as e:
        print(f"\nAn error occurred during API call: {e}")
        print("This often means your API key is invalid or not activated yet.")

# This line tells Python to run the `main` function
# when you execute the file directly.
if __name__ == "__main__":
    main()