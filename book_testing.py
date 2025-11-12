import bigbookapi
from bigbookapi.rest import ApiException

def main():
    # 1. Paste your Big Book API key here
    API_KEY = "dec57ed47cb341449df3b7ab2ce678f2"

    # 2. Set up the configuration
    configuration = bigbookapi.Configuration(
        host = "https://api.bigbookapi.com"
    )
    configuration.api_key['apiKey'] = API_KEY
    configuration.api_key['headerApiKey'] = API_KEY

    try:
        with bigbookapi.ApiClient(configuration) as api_client:
            api_instance = bigbookapi.DefaultApi(api_client)
            
            # --- STEP 1: Search for a book to get a valid ID ---
            print("--- Searching for 'The Hobbit' ---")
            search_query = 'The Notebook'
            
            search_response = api_instance.search_books(query=search_query, number=1)
            
            # Check if the 'books' key exists and is not empty
            if search_response.get('books') and len(search_response['books']) > 0 and len(search_response['books'][0]) > 0:
                
                # Access the first book [0] in the inner list [0]
                book_data = search_response['books'][0][0]
                real_book_id = book_data.get('id')
                
                # --- Reader-Friendly Output for Search ---
                print("\n--- Search Result ---")
                print(f"Title:    {book_data.get('title')}")
                if book_data.get('subtitle'):
                    print(f"Subtitle: {book_data.get('subtitle')}")
                # Check if author info exists
                if book_data.get('authors'):
                    print(f"Author:   {book_data['authors'][0].get('name')}")
                print(f"Found ID: {real_book_id}")
                
                # book_info = api_instance.get_book_information(real_book_id)
                # if book_info.get('genres'):
                #     first_genre = book_info['genres'][0]
                #     print(f"Genre: {first_genre}")
                # else:
                #     print("No genres found for this book.")
                # --- End of Reader-Friendly Output ---
                
                if real_book_id:
                    print("\n--- Now finding similar books... ---")

                    # Use the real ID in your find_similar_books call
                    similar_response = api_instance.find_similar_books(real_book_id, number=5)
                    
                    # --- Reader-Friendly Output for Similar Books ---
                    print("\n--- Similar Books Response ---")
                    if similar_response.get('similar_books'):
                        for i, book in enumerate(similar_response['similar_books']):
                            print(f"  {i+1}. {book.get('title')} (ID: {book.get('id')})")
                    else:
                        print("No similar books found.")
                    # --- End of Reader-Friendly Output ---

                else:
                    print("Could not find an ID for the first book.")

            else:
                print("Could not find 'The Hobbit' to get a real ID.")

    except ApiException as e:
        print(f"\nAn error occurred: {e}")
    except Exception as e:
        print(f"\nA general error occurred: {e}")

if __name__ == "__main__":
    main()