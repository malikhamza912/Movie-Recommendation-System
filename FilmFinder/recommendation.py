import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

# Generate user-item matrix
def create_user_item_matrix(ratings):
    user_item_matrix = ratings.pivot(index='userId', columns='movieId', values='rating')
    user_item_matrix.fillna(0, inplace=True)
    return user_item_matrix

# Collaborative Filtering
def get_recommendations(preferences, ratings, movies):
    user_item_matrix = create_user_item_matrix(ratings)
    similarity_matrix = cosine_similarity(user_item_matrix)

    # Dummy user similarity (example calculation for simplification)
    user_index = user_item_matrix.index[-1]  # Mock new user
    similar_users = similarity_matrix[user_index].argsort()[-10:][::-1]

    recommended_movie_ids = set()
    for user in similar_users:
        rated_movies = ratings[ratings['userId'] == user]['movieId']
        recommended_movie_ids.update(rated_movies)

    # Filter recommendations based on preferences
    recommended_movies = movies[movies['movieId'].isin(recommended_movie_ids)]
    return recommended_movies['title'].tolist()