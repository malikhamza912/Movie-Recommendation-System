import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
df1 = pd.read_csv('C:/Users/Hamza/Documents/6th SEM/5) AI/3) PROJ/FF/[MAIN] ff/movies.csv')
df2 = pd.read_csv('C:/Users/Hamza/Documents/6th SEM/5) AI/3) PROJ/FF/[MAIN] ff/ratings.csv')

df = df2.merge(df1, left_on='movieId', right_on='movieId', how='left')

del df['timestamp']
del df['genres']


userrr = 578


user_movie_matrix = pd.pivot_table(df, values = 'rating', index='movieId', columns = 'userId')

user_movie_matrix = user_movie_matrix.fillna(0)

user_user_matrix = user_movie_matrix.corr(method='pearson')

user_user_matrix.loc[userrr].sort_values(ascending=False).head(10)

df_2 = pd.DataFrame(user_user_matrix.loc[userrr].sort_values(ascending=False).head(10))
df_2 = df_2.reset_index()
df_2.columns = ['userId', 'similarity']

df_2 = df_2.drop((df_2[df_2['userId'] ==userrr]).index)

final_df = df_2.merge(df, left_on='userId', right_on='userId', how='left')

final_df['score'] = final_df['similarity']*final_df['rating']

watched_df = df[df['userId'] == userrr]

cond = final_df['movieId'].isin(watched_df['movieId'])
final_df.drop(final_df[cond].index, inplace = True)

recommended_df = final_df.sort_values(by = 'score', ascending = False)['title'].head(10)
recommended_df = recommended_df.reset_index()
del recommended_df['index']

print(recommended_df)