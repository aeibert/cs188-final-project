from tmdbv3api import TMDb, Genre, Discover, Movie, Search

def main():
    tmdb = TMDb()
    # 1. Re-paste your new TMDb key here
    tmdb.api_key = 'd4dff7104608d6f3f1327157aeba5f7d'

    # 2. Use the Discover class, not Movie
    discover = Discover()
    genre = Genre()

    try:
        print("--- Finding Sci-Fi ID ---")
        genre_list = genre.movie_list()
        # Find the ID for 'Science Fiction'
        sci_fi_id = next(g['id'] for g in genre_list if g['name'] == 'Science Fiction')
        print(f"Sci-Fi ID is: {sci_fi_id}")

        print("\n--- Discovering Popular Sci-Fi Movies ---")
        # 3. Call discover_movie with a dictionary of your filters
        recommendations = discover.discover_movies({
            'with_genres': sci_fi_id,
            'sort_by': 'popularity.desc'
        })

        for m in recommendations:
            print(f"- {m['title']} (Popularity: {m['popularity']})")

    except Exception as e:
        print(f"An error occurred: {e}")

def recommendation(query, limit):
    movie = Movie()
    search = Search()
    s = search.movies(query)
    
    # Check if the search returned any results
    if not s:
        print(f"No movies found for '{query}'")
        return

    first_result = s[0]
    print(f"Found movie: {first_result.title} (ID: {first_result.id})")
    
    print(f"\n--- Finding {limit} recommendations ---")
    recommendations = movie.recommendations(first_result.id)
    
    # Convert to a standard list to be able to slice it
    recommendations_list = list(recommendations)
    
    # Slice the list to the desired limit
    limited_recommendations = recommendations_list[:int(limit)]
    
    for recommendation in limited_recommendations:
        print("%s (%s)" % (recommendation.title, recommendation.release_date))

if __name__ == "__main__":
    main()
    movie_to_search = "The Notebook"
    number_of_recs = 5
    
    recommendation(movie_to_search, number_of_recs)