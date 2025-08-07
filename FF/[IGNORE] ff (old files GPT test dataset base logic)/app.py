import streamlit as st
import os
import json
import random

st.title("FilmFinder")

# Load CSS
with open("ff.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load questions
with open("questions.json") as f:
    questions = json.load(f)

# Load existing user IDs
existingUserIds = []
try:
    with open("existing_user_ids.txt", "r") as f:
        existingUserIds = [int(line.strip()) for line in f]
except FileNotFoundError:
    pass

# Initialize selectedOptions
selectedOptions = []

# Function to generate a unique user ID
def generateUniqueUserId():
    global userId
    while True:
        userId = str(random.randint(10000, 99999))
        if userId not in existingUserIds:
            break

generateUniqueUserId()

# Main Streamlit app
st.header("FilmFinder")
st.subheader('"Discover movies loved by others like you!"')

st.write("Answer these questions to find your next favorite movie.")

if st.button("Start"):
    st.empty()
    for i in range(len(questions)):
        st.subheader(questions[i]["question"])
        col1, col2 = st.columns(2)
        if questions[i]["isMultiSelect"]:
            selected_options = st.multiselect(
                "Select your preferred options",
                options=questions[i]["options"]
            )
            selectedOptions.append(selected_options)
        else:
            option = st.radio("Choose your preference", options=questions[i]["options"])
            selectedOptions.append([option])
    
    if st.button("Finish"):
        st.subheader("Your Preferences:")
        for i in range(len(questions)):
            st.write(f"{questions[i]['question']}: {selectedOptions[i]}")
        
        # Submit preferences to the backend
        import requests
        
        response = requests.post('http://127.0.0.1:5000/submit_preferences', 
                                json={'userId': userId, 'preferences': selectedOptions})
        recommendations = response.json()['recommendations']
        
        st.subheader("Movie Recommendations:")
        for movie in recommendations:
            st.write(movie)

        if st.button("Restart"):
            st.experimental_rerun()
