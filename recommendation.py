from tmdbv3api import TMDb, Movie, Search
from argparse import ArgumentParser
tmdb = TMDb()
tmdb.api_key = 'd4dff7104608d6f3f1327157aeba5f7d'
# Simple program that takes a movie name as an argument and finds movie recommendations for the user.
# call it like this in the terminal: # python recommendation.py "Movie Name"
def search(query, limit):
    movie = Movie()
    search = Search()
    s = search.movies(query)
    first_result = s[0]
    recommendations = movie.recommendations(first_result.id)
    # Convert to a standard list first
    recommendations = list(recommendations)
    recommendations = recommendations[:int(limit)]
    for recommendation in recommendations:
        print("%s (%s) - %s" % (recommendation.title, recommendation.overview, recommendation.release_date))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("movie")
    parser.add_argument("--limit", nargs="?", default=1)
    args = parser.parse_args()
    search(args.movie, args.limit)
    
#movie = Movie()
# # search = movie.search('The Notebook')
# # print("------------Search by Title-------------:")
# # for res in search:
# #     print(res.id)
# #     print(res.title)
# #     print(res.overview)
# #     print(res.poster_path)
# #     print(res.vote_average)
# recommendations = movie.recommendations(movie_id=11036)
# print("------------Recommended Movies-------------:")
# for recommendation in recommendations:
#     print(recommendation.title)
#     print(recommendation.overview)

# similar = movie.similar(11036)
# print("------------Similar Movies-------------:")
# for result in similar:
#     print(result.title)
#     print(result.overview)