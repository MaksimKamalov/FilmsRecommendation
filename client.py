import streamlit as st
import requests
import os
import extra_streamlit_components as stx

def getFilms(films: list, input=None):
    for i in range(0, len(films)):
        st.write(str(i + 1) + " " + films[i])


def main():
    st.title("Рекомендации фильмов")

    st.session_state.film_name = "Test"

    chosen_id = stx.tab_bar(data=[
        stx.TabBarItemData(id=1, title="Популярные фильмы", description=""),
        stx.TabBarItemData(id=2, title="Популярные фильмы по жанрам", description=""),
        stx.TabBarItemData(id=3, title="Популярные фильмы по контенту", description=""),
        stx.TabBarItemData(id=4, title="Популярные фильмы по пользователям", description=""),
    ], default=1)

    if chosen_id == '1':
        response = requests.get("http://127.0.0.1:5050/recs/popular")
        result = response.json()
        films = result.get("films")

        getFilms(films)

    elif chosen_id == '2':
        input_text = st.text_input("Введите жанр")

        if st.button("Получить"):
            if input_text.strip() != "":
                response = requests.post("http://127.0.0.1:5050/recs/genre", json={
                    "genre": input_text
                })
                result = response.json()
                films = result.get("films")

                getFilms(films)
    elif chosen_id == '3':
        input_text = st.text_input("Введите название фильма")

        if st.button("Получить"):
            if input_text.strip() != "":
                response = requests.post("http://127.0.0.1:5050/recs/content", json={
                    "title": input_text
                })
                result = response.json()
                films = result.get("films")

                getFilms(films)

    elif chosen_id == '4':
        input_text = st.text_input("Введите id пользователя")

        if st.button("Получить"):
            if input_text.strip() != "":
                response = requests.post("http://127.0.0.1:5050/recs/user/collaborative", json={
                    "id": int(input_text)
                })
                result = response.json()

                st.header("Что смотрят другие")
                collaborative_films = result.get("collaborative_films")
                getFilms(collaborative_films)
                st.header("Что нравится вам")
                favorite_films = result.get("favorite_films")
                getFilms(favorite_films)


if __name__ == "__main__":
    main()
