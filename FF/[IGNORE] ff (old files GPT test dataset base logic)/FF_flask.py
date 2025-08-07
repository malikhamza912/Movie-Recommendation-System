from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

# Load datasets
try:
    movies = pd.read_csv('C:/Users/Hamza/Documents/6th SEM/5) AI/3) PROJ/Downloaded Datasets/movies.csv')
    ratings = pd.read_csv('C:/Users/Hamza/Documents/6th SEM/5) AI/3) PROJ/Downloaded Datasets/ratings.csv')
    # Ensure necessary columns exist
    required_movie_columns = ['movieId', 'title', 'genre', 'age_rating']
    if not all(col in movies.columns for col in required_movie_columns):
        raise ValueError("The movies dataset is missing required columns.")
    if 'userId' not in ratings.columns or 'movieId' not in ratings.columns or 'rating' not in ratings.columns:
        raise ValueError("The ratings dataset is missing required columns.")
except Exception as e:
    print(f"Error loading datasets: {e}")
    movies = pd.DataFrame()  # Empty DataFrame to prevent errors
    ratings = pd.DataFrame()

# Create the utility matrix for collaborative filtering
try:
    movie_rating_matrix = pd.pivot_table(ratings, values='rating', index='userId', columns='movieId').fillna(0)
except Exception as e:
    print(f"Error creating utility matrix: {e}")
    movie_rating_matrix = pd.DataFrame()

# Function for content-based filtering
def filter_movies(movies, preferences):
    try:
        # Filter based on genre and age rating
        filtered_movies = movies[
            (movies['genre'].str.contains(preferences['genre'], case=False, na=False)) &  # Genre matching
            (movies['age_rating'].apply(lambda x: int(x.split('+')[0]) <= int(preferences['age_rating'].split('+')[0])))  # Age rating comparison
        ]
        return filtered_movies
    except Exception as e:
        print(f"Error filtering movies: {e}")
        return pd.DataFrame()

# Function for collaborative filtering
def recommend_movies(user_id, ratings_matrix, movies, top_n=5):
    try:
        user_similarity = cosine_similarity(ratings_matrix)
        similar_users = np.argsort(-user_similarity[user_id])[1:6]  # Top 5 similar users
        recommended_movies = np.argsort(-np.mean(ratings_matrix[similar_users], axis=0))[:top_n]
        return movies[movies['movieId'].isin(recommended_movies)]['title'].tolist()
    except Exception as e:
        print(f"Error in collaborative filtering: {e}")
        return ["Error generating recommendations."]

# Initialize SQLite database
def init_db():
    try:
        conn = sqlite3.connect('filmfinder.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                age_rating TEXT,
                genre TEXT,
                year_range TEXT,
                rating TEXT,
                duration_range TEXT
            )

        ''')
        conn.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

# Endpoint for content-based filtering
@app.route('/submit_preferences', methods=['POST'])
def submit_preferences():
    try:
        data = request.json  # Expecting JSON data from frontend
        if not data:
            return jsonify({"error": "Invalid input data"}), 400

        # Extract preferences
        age_rating = data.get('age_rating', '')
        genre = data.get('genre', '')
        year_range = data.get('year_range', '')
        rating = data.get('rating', '')
        duration_range = data.get('duration_range', '')

        # Save preferences to database
        conn = sqlite3.connect('filmfinder.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_preferences (age_rating, genre, year_range, rating, duration_range)
            VALUES (?, ?, ?, ?, ?)
        ''', (age_rating, genre, year_range, rating, duration_range))
        conn.commit()
        conn.close()

        # Filter movies based on preferences
        preferences = {
            'age_rating': age_rating,
            'genre': genre,
            'year_range': year_range,
            'rating': rating,
            'duration_range': duration_range
        }
        filtered_movies = filter_movies(movies, preferences)

        # Recommend top 5 movies
        recommended_movies = filtered_movies.head(5)['title'].tolist() if not filtered_movies.empty else ["No matching movies found."]
        return jsonify({"recommendations": recommended_movies})
    except Exception as e:
        print(f"Error in /submit_preferences endpoint: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# Endpoint for collaborative filtering
@app.route('/recommend_movies', methods=['POST'])
def recommend_movies_endpoint():
    try:
        data = request.json  # Expecting JSON data with 'user_id'
        user_id = int(data.get('user_id', -1))
        if user_id == -1:
            return jsonify({"error": "User ID is required"}), 400

        # Generate recommendations using collaborative filtering
        recommended_movies = recommend_movies(user_id - 1, movie_rating_matrix.values, movies, top_n=5)
        return jsonify({"recommendations": recommended_movies})
    except Exception as e:
        print(f"Error in /recommend_movies endpoint: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)