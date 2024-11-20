import pickle

import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.metrics.pairwise import linear_kernel
from scipy.sparse import csr_matrix

with open('tfidf_matrix.pkl', 'rb') as file:
    tfidf_matrix = pickle.load(file)

with open('model_knn.pkl', 'rb') as file:
    model_knn = pickle.load(file)

popularite = pd.read_csv("data.csv",sep="\t")
films=pd.read_csv("films.csv", low_memory=False,sep="\t")
merged=pd.read_csv("merged.csv", low_memory=False,sep="\t")

users_pivot=merged.pivot_table(index=["userId"],columns=["title"],values="rating")
users_pivot.fillna(0,inplace=True)
films_df_matrix = csr_matrix(users_pivot.values)

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
indices = pd.Series(films.index, index=films['title_wy'])

def get_recommendations(title, cosine_sim=cosine_sim):
    try:
        title = title.strip()

        try:
            idx = indices[title.lower()]
        except:
            titles = indices.index.tolist()
            for i in range(0, len(titles)):
                val = titles[i]
                if title.lower() in val.lower():
                    idx = i
                    break

        sim_scores = list(enumerate(cosine_sim[idx]))

        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        sim_scores = sim_scores[1:11]

        movie_indices = [i[0] for i in sim_scores]

        return films['title'].iloc[movie_indices].values.tolist()
    except:
        return list()

def get_recs_by_genres(genre):
    return popularite[popularite['genres'].str.contains(genre)].sort_values('score', ascending=False).head(10)['title'].values.tolist()

def get_popular_recs():
    return popularite.sort_values('score', ascending=False).head(10)['title'].values.tolist()


def find_favorite_films(User_id):
    return merged[merged['userId']==User_id].sort_values('rating',ascending=False).head(10)['title'].values.tolist()

def find_collaborative_films(User_id, count=10):
    try:
        user_index = users_pivot.index.get_loc(User_id)

        distances, indices = model_knn.kneighbors(films_df_matrix[user_index], n_neighbors=count + 1)

        favorite_indices = indices[0][1:]

        favorite_films = pd.DataFrame({"title": [users_pivot.columns[idx] for idx in favorite_indices]})
        return favorite_films['title'].values.tolist()
    except:
        return list()


app = FastAPI()

class ContentRecs(BaseModel):
    title: str

@app.post("/recs/content")
async def predict_cluster(item: ContentRecs):
    return {'films': get_recommendations(item.title)}

class GenreRecs(BaseModel):
    genre: str

@app.post("/recs/genre")
async def predict_cluster(item: GenreRecs):
    return {'films': get_recs_by_genres(item.genre)}

@app.get("/recs/popular")
async def predict_cluster():
    return {'films': get_popular_recs()}

class UserColRecs(BaseModel):
    id: int

@app.post("/recs/user/collaborative")
async def predict_cluster(item: UserColRecs):
    return {
        'collaborative_films': find_collaborative_films(item.id,10),
        'favorite_films': find_favorite_films(item.id)
    }