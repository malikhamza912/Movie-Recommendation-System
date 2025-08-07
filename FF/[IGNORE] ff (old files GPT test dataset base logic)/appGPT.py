import streamlit as st
import requests
import pandas as pd
import random

# Load existing user IDs (from the CSV file)
def fetch_existing_user_ids():
    url = 'https://raw.githubusercontent.com/Uttkarsh14/Movie-Recommendation-Engine/main/ratings.csv'
    try:
        data = pd.read_csv(url)
        existing_user_ids = data['userId'].unique().tolist()
        return existing_user_ids
    except Exception as e:
        st.error(f"Error fetching user IDs: {e}")
        return []

# Function to generate a unique user ID
def generate_unique_user_id(existing_user_ids):
    while True:
        user_id = random.randint(1000, 9999)  # Generate ID between 1000 and 9999
        if user_id not in existing_user_ids:
            return user_id

# Questions for the survey
questions = [
    {
        "question": "Which of these genres do you enjoy the most?",
        "options": ["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Adventure", "Animation", "Crime", 
                    "Documentary", "Fantasy", "IMAX", "Musical", "Mystery", "Romance", "Thriller", "War", "Western", 
                    "Children", "Film-Noir"],
        "multi_select": True,
    },
    {
        "question": "How often do you watch movies?",
        "options": ["Daily", "A few times a week", "Once a week", "Rarely"],
        "multi_select": False,
    },
    {
        "question": "Do you prefer recent movies or classics?",
        "options": ["Recent (2010-2024)", "Classics (Before 2010)"],
        "multi_select": False,
    },
    {
        "question": "What type of endings do you prefer?",
        "options": ["Happy", "Sad", "Open-ended", "Surprise Twists"],
        "multi_select": False,
    },
]

# Streamlit App
def run():
    st.set_page_config(page_title="FilmFinder", layout="centered")

    # Custom CSS
    st.markdown("""
    <style>
    body {
    margin: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-image: url('https://wallpapercave.com/wp/wp10615910.jpg');
    background-size: cover;
    background-position: center;
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: center; /* Keep this for vertical centering */
    align-items: center;     /* Keep this for horizontal centering */
    height: 100vh;          /* Revert to this */
    position: relative;
}

body::before {
    content: '';
    position: fixed; /* Keep this fixed */
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.8); /* Semi-transparent grey overlay */
    z-index: 1; 
}

.content {
    position: relative; /* Ensures the text is above the overlay */
    z-index: 2;
    text-align: center;
}

.together
{
    text-align: center;
    margin-top: 20px;
}

h1 {
    font-size: 3rem;
    color: #e50914;
    margin-bottom: 10px;
}

h2 {
    font-size: 1.5rem;
    margin-bottom: 20px;
}

.tagline {
    font-size: 1.2rem;
    color: #cccccc;
    margin-bottom: 30px;
    text-align: center;
}

button {
    background-color: #e50914;
    color: white;
    border: none;
    padding: 15px 30px;
    font-size: 1rem;
    cursor: pointer;
    border-radius: 5px;
    transition: background-color 0.3s ease, transform 0.2s ease;
}

button:hover {
    background-color: #b20710;
    transform: scale(1.05);
}

.question-page {
    display: none;
}

.question-container {
    text-align: center;
}

.options {
    margin-top: 20px;
}

.options-wrapper {
    display: flex;
    justify-content: center; 
    align-items: center;        
    flex-wrap: wrap;        
    gap: 15px;              
    margin-top: 20px;
}

.option {
    list-style: none;
    margin: 10px 0;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 15px;
    background-color: #333;
    border: 1px solid #555;
    border-radius: 5px;
    transition: background-color 0.3s ease, border-color 0.3s ease;
    min-width: 120px; /* Ensure options have a consistent size */
    text-align: center;
}

.option:hover {
    background-color: #444;
    border-color: #e50914;
}

.option.selected {
    background-color: #e50914;
    border-color: #b20710;
    color: white;
}


.navigation {
    margin-top: 30px;
}

.navigation button {
    margin: 0 15px;
}

.genre-options {
    display: flex;
    justify-content: space-around; /* Distributes space between items */
}

.genre-options .option {
    flex: 1; /* Each option takes equal space */
    text-align: center; /* Center-aligns the text */
    margin: 0 5px; /* Adds some margin between options */
}

.grid-options {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-top: 20px;
    text-align: center;
}
    </style>
    """, unsafe_allow_html=True)

    # Welcome page
    st.title("FilmFinder")
    st.subheader('"Discover movies loved by others like you!"')
    st.write("Answer these questions to find your next favorite movie.")
    
    if st.button("Start"):
        existing_user_ids = fetch_existing_user_ids()
        user_id = generate_unique_user_id(existing_user_ids)
        st.session_state.user_id = user_id
        ask_questions()

# Ask survey questions
def ask_questions():
    selected_options = []
    for i, question in enumerate(questions):
        st.subheader(question["question"])
        
        if question["multi_select"]:
            options = st.multiselect("", question["options"])
        else:
            options = st.radio("", question["options"])
        
        selected_options.append(options)

        if i < len(questions) - 1:
            st.button("Next", on_click=lambda: question(i + 1))
        else:
            st.button("Finish", on_click=lambda: show_results(selected_options))

# Show results after finishing the survey
def show_results(selected_options):
    user_preferences = [
        {"question": q["question"], "answers": selected_options[i]} for i, q in enumerate(questions)
    ]
    
    # Send data to Flask backend
    response = requests.post(
        "http://127.0.0.1:5000/submit_preferences", 
        json={"userId": st.session_state.user_id, "preferences": user_preferences}
    )

    if response.status_code == 200:
        data = response.json()
        recommendations = data.get("recommendations", [])
        st.write("Recommended Movies:")
        for movie in recommendations:
            st.write(movie)
    else:
        st.error("Error: Unable to fetch recommendations")

if __name__ == '__main__':
    run()
