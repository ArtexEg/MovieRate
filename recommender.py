import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import pickle
import os
import sys


def resource_path(filename):
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), filename)
    else:
        return os.path.join(os.path.dirname(__file__), filename)

#Загружаем модель нейронной сети
model = load_model(resource_path("recommender_model.keras"))

#Загружаем словарь переиндексованных фильмов
with open(resource_path("movie_map.pkl"), "rb") as f:
    movie_map = pickle.load(f)

def nn_recommendations_gui(
    df,
    movies,
    model,
    movie_map,
    top_n=20
):

    #Получаем список индексов фильмов, которые пользователь посмотрел
    watched = df['movieId'].values
    watched = [m for m in watched if m in movie_map]

    #Формируем список непросмотренных фильмов
    unwatched = movies[
        ~movies["movieId"].isin(watched)].copy()

    unwatched = unwatched[
        unwatched["movieId"].isin(movie_map.keys())].copy()

    if unwatched.empty:
        return pd.DataFrame()

    #Используем модель нейронной сети
    movie_ids = unwatched["movieId"].values
    movie_encoded = np.array([movie_map[m] for m in movie_ids])

    user_array = np.zeros(len(movie_encoded), dtype=int)

    predictions = model.predict(
        [user_array, movie_encoded],
        verbose=0
    ).flatten()

    #Усиляем влияние схожих фильмов
    boost = np.zeros(len(unwatched))

    for _, row in df.iterrows():
        movie_id = row["movieId"]
        rating = row["rating"]

        if movie_id not in movie_map:
            continue

        genre = movies[movies["movieId"] == movie_id]["genres"].values

        if len(genre) == 0:
            continue

        genre = genre[0]

        #Усиливаем похожие жанры
        mask = unwatched["genres"].str.contains(genre, na=False)

        #Нормализация
        boost[mask] += (rating - 3) * 0.3

    #Итоговая оценка
    final_scores = predictions + boost

    #Лучшие кандидаты
    top_n = min(top_n, len(final_scores))
    top_indices = final_scores.argsort()[-top_n:][::-1]

    result = []

    for i in top_indices:
        result.append({
            "title": unwatched.iloc[i]["title"],
            "score": round(float(final_scores[i]), 2)
        })

    return pd.DataFrame(result)