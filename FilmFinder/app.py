from flask import Flask, request, jsonify, render_template
from recommendation import get_recommendations
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Load datasets
movies = pd.read_csv('C:/Users/Hamza/Documents/6th SEM/5) AI/3) PROJ/FilmFinder/data/movies.csv')
ratings = pd.read_csv('C:/Users/Hamza/Documents/6th SEM/5) AI/3) PROJ/FilmFinder/data/ratings.csv')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_preferences', methods=['POST'])
def submit_preferences():
    user_preferences = request.json
    recommended_movies = get_recommendations(user_preferences, ratings, movies)
    return jsonify({"recommendations": recommended_movies})

if __name__ == '__main__':
    app.run(debug=True)