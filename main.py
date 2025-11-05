from tmdbv3api import TMDb, Genre, Discover

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
if __name__ == "__main__":
    main()