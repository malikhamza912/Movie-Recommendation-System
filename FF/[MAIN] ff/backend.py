from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Load data
df1 = pd.read_csv('C:/Users/Hamza/Documents/6th SEM/5) AI/3) PROJ/FF/[MAIN] ff/movies.csv')
df2 = pd.read_csv('C:/Users/Hamza/Documents/6th SEM/5) AI/3) PROJ/FF/[MAIN] ff/ratings.csv')

# Merge the datasets
df = df2.merge(df1, left_on='movieId', right_on='movieId', how='left')

print(df1.head())  # Print first few rows of movies dataframe
print(df2.head())  # Print first few rows of ratings dataframe
print(df.head())   # Print first few rows of combined dataframe
print(df.columns) 

# Create the user-movie matrix
user_movie_matrix = pd.pivot_table(df, values='rating', index='movieId', columns='userId', fill_value=0)

# User similarity matrix using Pearson correlation
user_user_matrix = user_movie_matrix.corr(method='pearson')

@app.route('/submit_preferences', methods=['POST'])
def submit_preferences():
    global df, user_movie_matrix, user_user_matrix  # Declare these variables as global

    data = request.json
    user_id = data['userId']
    preferences = data['preferences']
    print(f"User ID: {user_id}, Preferences: {preferences}")  # Add debug print
    
    # Check if user already exists
    if user_id not in user_movie_matrix.columns:
        new_row = {'userId': user_id, 'movieId': 0, 'rating': 0}
        # Append the new row to the global DataFrame
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        # Recalculate user-movie matrix
        user_movie_matrix = pd.pivot_table(df, values='rating', index='movieId', columns='userId', fill_value=0)

        # Update the user similarity matrix
        user_user_matrix = user_movie_matrix.corr(method='pearson')

    # Convert preferences to a list if it's a string
    if isinstance(preferences, str):
        preferences = [preferences]

    # Filter movies based on genre preference
    filtered_movies = df[df['genres'].notnull() & df['genres'].apply(lambda x: len(x.split(',')) > 0)]

    # If no movies match preferences, return an empty list
    if filtered_movies.empty:
        return jsonify({'recommendedMovies': []})

    print(f"Filtered Movies shape: {filtered_movies.shape}")
    print(f"Number of filtered movies: {len(filtered_movies)}")
    
    # Calculate scores based on similarity and ratings
    similar_users = user_user_matrix.loc[user_id].sort_values(ascending=False)
    similar_users = similar_users[similar_users.index != user_id]  # Remove the current user

    # Get recommended movies from similar users
    recommended_movies = filtered_movies[filtered_movies['userId'].isin(similar_users.index)]
    recommended_movies = recommended_movies.groupby('title').mean('rating').sort_values(by='rating', ascending=False).head(10)

    recommendations = recommended_movies.index.tolist()
    return jsonify({'recommendedMovies': recommendations, 'userId': user_id})

if __name__ == '__main__':
    app.run(debug=True)