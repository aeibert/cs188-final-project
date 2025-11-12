import pyodbc
import os

def get_tmdb_genre_id(book_genre_name):
    """
    Connects to the Azure SQL database and looks up the TMDb genre ID
    for a given book genre name.
    """
    
    # 1. GET THIS FROM THE AZURE PORTAL
    # It will look something like: 
    
    connection_string = os.environ["AZURE_SQL_CONNECTIONSTRING"]
    
    # 2. THIS IS YOUR SQL QUERY
    sql_query = "SELECT MovieGenre FROM Genre WHERE BookGenre = ?"
    
    tmdb_id = None
    
    try:
        # Connect to the database
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Execute the query safely with a parameter
        # This prevents SQL injection attacks
        cursor.execute(sql_query, (book_genre_name,))
        
        # Get the first result
        row = cursor.fetchone()
        
        if row:
            tmdb_id = row[0] # Get the first column from the row
            
    except Exception as e:
        print(f"Database error: {e}")
        
    finally:
        # Always close the connection
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            
    return tmdb_id

if __name__ == "__main__":
    print("Connecting to database...")
    
    # Call your function and store its return value
    found_id = get_tmdb_genre_id("horror")
    
    # Now, print the value you got back!
    print(f"Function returned: {found_id}")

    if found_id:
        print("Success! It found a matching ID.")
    else:
        print("Connection worked, but no ID was found for that genre.")
        print("Check your SQL table to make sure 'Science Fiction' exists.")