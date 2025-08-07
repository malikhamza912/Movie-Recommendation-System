import streamlit as st
import requests
import json
import random

def flask_backend(data):
    # Simulating API call
    url = "http://localhost:5000/submit_preferences"
    response = requests.post(url, json=data)
    return response.json()

# Streamlit app
st.title("Movie Recommendation System")

# Form
with st.form("movie_form"):
    user_id = st.text_input("Enter your User ID")
    genre_pref = st.selectbox("Select your preferred genre", ["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Adventure", "Animation", "Crime", "Documentary", "Fantasy", "IMAX", "Musical", "Mystery", "Romance", "Thriller", "War", "Western", "Children", "Film-Noir"])
    
    mood = st.radio("How are you feeling?", ("Happy and Excited", "Neutral", "Sad and Depressed"))
    
    movie_endings = st.radio("What movie endings do you prefer?", ("Happy", "Sad", "Twist", "Open", "Ambiguous"))

    submitted = st.form_submit_button("Submit")

if submitted:
    # Validate user ID
    if not user_id or not user_id.isdigit():
        st.error("Please enter a valid numeric User ID.")
    else:
        # Call Flask backend
        data = {
            'userId': int(user_id),
            'preferences': genre_pref,
            'mood': mood,
            'movieEndings': movie_endings
        }
        
        try:
            result = flask_backend(data)
            
            if isinstance(result, dict):
                st.subheader("Top Recommended Movie")
                recommended_movie = result.get('recommendedMovie', 'No movie found')
                st.write(f"The top recommended movie based on your preferences is: {recommended_movie}")
                
                st.subheader("Similar Users")
                similar_users = result.get('similarUsers', [])
                st.json(similar_users, expanded=False)
                
                st.subheader("Score Details")
                score_details = result.get('scoreDetails', {})
                st.json(score_details, expanded=False)
            else:
                st.error(f"Unexpected response format: {type(result)}")
        except Exception as e:
            st.error(f"Error calling backend: {str(e)}")

else:
    st.info("Please fill out the form and click Submit.")