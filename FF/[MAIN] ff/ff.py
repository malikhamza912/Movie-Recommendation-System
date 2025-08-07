from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

# Initialize Flask app
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

# Load data
df1 = pd.read_csv(r'https://raw.githubusercontent.com/Uttkarsh14/Movie-Recommendation-Engine/main/movies.csv')
df2 = pd.read_csv(r'https://raw.githubusercontent.com/Uttkarsh14/Movie-Recommendation-Engine/main/ratings.csv')

# Merge the datasets
df = df2.merge(df1, left_on='movieId', right_on='movieId', how='left')

# Clean the data
del df['genres']

# Create the user-movie matrix
user_movie_matrix = pd.pivot_table(df, values='rating', index='movieId', columns='userId')
user_movie_matrix = user_movie_matrix.fillna(0)

# User similarity matrix using Pearson correlation
user_user_matrix = user_movie_matrix.corr(method='pearson')

@app.route('/submit_preferences', methods=['POST'])
def submit_preferences():
    try:
        data = request.get_json()
        user_id = data.get('userId')
        preferences = data.get('preferences', [])  # Ensure preferences are extracted

        if user_id is None:
            return jsonify({'error': 'User ID is required'}), 400

        # Fetch top similar users based on the similarity matrix
        df_2 = pd.DataFrame(user_user_matrix.loc[user_id].sort_values(ascending=False).head(10))
        df_2 = df_2.reset_index()
        df_2.columns = ['userId', 'similarity']

        # Remove the current user
        df_2 = df_2.drop((df_2[df_2['userId'] == user_id]).index)

        # Merge similar users' ratings with movies
        final_df = df_2.merge(df, left_on='userId', right_on='userId', how='left')

        # Calculate score for each movie recommendation
        final_df['score'] = final_df['similarity'] * final_df['rating']

        # Remove movies the current user has already watched
        watched_df = df[df['userId'] == user_id]
        cond = final_df['movieId'].isin(watched_df['movieId'])
        final_df.drop(final_df[cond].index, inplace=True)

        # Sort by the calculated score to recommend movies
        recommended_df = final_df.sort_values(by='score', ascending=False)['title'].head(10)
        recommended_df = recommended_df.reset_index()

        # Return the top 10 recommended movies
        recommendations = recommended_df['title'].tolist()

        return jsonify({'recommendations': recommendations})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Return the error message for debugging

if __name__ == '__main__':
    app.run(debug=True)