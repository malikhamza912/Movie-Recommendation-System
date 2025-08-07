import pytest
from FF_flask import app, init_db
import sqlite3
import pandas as pd 

@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    with app.app_context():
        init_db()  # Ensure database is initialized
    yield client

# Test case for the /submit_preferences endpoint
def test_submit_preferences(client):
    response = client.post('/submit_preferences', json={
        "age_rating": "13+",
        "genre": "Action",
        "year_range": "",
        "rating": "",
        "duration_range": ""
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "recommendations" in data
    assert isinstance(data['recommendations'], list)

# Test case for the /recommend_movies endpoint
def test_recommend_movies(client):
    response = client.post('/recommend_movies', json={
        "user_id": 1
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "recommendations" in data
    assert isinstance(data['recommendations'], list)

# Test case for filtering with invalid preferences
def test_invalid_preferences(client):
    response = client.post('/submit_preferences', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

# Test case for collaborative filtering with invalid user_id
def test_invalid_user_id(client):
    response = client.post('/recommend_movies', json={
        "user_id": -1
    })
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

# Test case for handling missing movies dataset
def test_missing_movies_dataset(client, monkeypatch):
    def mock_read_csv(filepath, *args, **kwargs):
        if 'movies.csv' in filepath:
            raise FileNotFoundError("movies.csv not found.")
        return pd.DataFrame()
    monkeypatch.setattr('pandas.read_csv', mock_read_csv)
    
    response = client.post('/submit_preferences', json={
        "age_rating": "13+",
        "genre": "Action",
        "year_range": "",
        "rating": "",
        "duration_range": ""
    })
    assert response.status_code == 500

# Test case for handling missing ratings dataset
def test_missing_ratings_dataset(client, monkeypatch):
    def mock_read_csv(filepath, *args, **kwargs):
        if 'ratings.csv' in filepath:
            raise FileNotFoundError("ratings.csv not found.")
        return pd.DataFrame()
    monkeypatch.setattr('pandas.read_csv', mock_read_csv)

    response = client.post('/recommend_movies', json={
        "user_id": 1
    })
    assert response.status_code == 500
