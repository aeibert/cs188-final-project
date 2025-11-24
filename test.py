from tmdbv3api import TMDb, Movie

tmdb = TMDb()

tmdb.api_key = "d4dff7104608d6f3f1327157aeba5f7d"

movie = Movie()

popular = movie.popular()

for p in popular:
    print(p.title)
    print(p.poster_path)