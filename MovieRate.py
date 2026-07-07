from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
from recommender import nn_recommendations_gui, model, movie_map
import os
import sys

def resource_path(filename):
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), filename)
    else:
        return os.path.join(os.path.dirname(__file__), filename)


#Задаём стартовое окно
root = Tk()
root.title('Вход в профиль')
root.geometry("320x50+700+350")

#функция создания нового окна
def new_window(x, y, old, title):
    #прячем старое окно
    old.withdraw()

    #задаём новое окно
    window = Toplevel(old)
    window.title(title)
    window.geometry(f"{x}x{y}+700+350")
    return window

#Окно основного меню
def main_menu():
    #Функция закрытия приложения
    def exit_app():
        root.destroy()

    #Функция закрытия окна и возврата в главное меню
    def exit_window(window, back):
        window.destroy()
        back.deiconify()

    #Скрываем корневое окно
    root.withdraw()

    #Задаём окно основного меню
    menu = new_window(200, 150, root, "Главное меню")

    #Меняем протокол закрытия окна
    menu.protocol("WM_DELETE_WINDOW", exit_app)

    #Настройка растягивания
    menu.grid_columnconfigure(0, weight=1)

    # Функция открытия окна оценки фильма
    def open_rating_window(parent, movie_data, idx, edit=False, tree=None, item=None):
        # Создаём новое окно
        rating = new_window(350, 60, parent, "Оценка")
        rating.protocol("WM_DELETE_WINDOW", lambda: exit_window(rating, parent))

        # Масштабируем элементы
        for i in range(5):
            rating.grid_columnconfigure(i, weight=1)

        # Задаём стартовое значение mark
        mark = StringVar(value='0')

        # Обозначаем все RadioButton
        for i in range(1, 6):
            rate = ttk.Radiobutton(
                rating,
                text=str(i),
                value=str(i),
                variable=mark
            )
            rate.grid(column=i - 1, row=0, sticky=NSEW, padx=5)

        # Функция принятия оценки
        def okay():
            # Проверка, что выбран RadioButton
            if mark.get() == '0':
                messagebox.showerror("Ошибка", "Выберите оценку")
                return

            # Берём значения из списка по индексу
            movie_id = movie_data.iloc[idx]['movieId']
            title = movie_data.iloc[idx]['title']
            genre = movie_data.iloc[idx]['genres']
            rating_value = int(mark.get())

            global df

            if edit:
                #Изменяем параметр рейтинга
                df.loc[df['movieId'] == movie_id, 'rating'] = rating_value
                tree.item(item, values=(title, rating_value))
            else:
                # Создаём новый элемент
                new_movie = {
                    'movieId': movie_id,
                    'title': title,
                    'genres': genre,
                    'rating': rating_value
                }

                # Добавляем элемент в профиль
                df = pd.concat([df, pd.DataFrame([new_movie])], ignore_index=True)

            # Выходим из окна оценки и возвращаемся назад
            exit_window(rating, parent)

        # Функция отмены
        def cancel():
            # Закрываем окно оценки и возвращаемся назад
            exit_window(rating, parent)

        # Контейнер для кнопок
        btn_frame = Frame(rating)
        btn_frame.grid(row=1, column=0, columnspan=5, pady=10)

        # Кнопка ОК
        OK = ttk.Button(btn_frame, text="ОК", command=okay)
        OK.grid(row=0, column=0, padx=5)

        # Кнопка Отмены
        Cancel = ttk.Button(btn_frame, text="Отмена", command=cancel)
        Cancel.grid(row=0, column=1, padx=5)

    def back_button(window, row):
        # Обозначаем кнопку для возвращения в главное меню
        back = ttk.Button(window, text='Вернуться в главное меню', command=lambda: exit_window(window, menu))
        back.grid(column=0, row=row, sticky="ew", padx=10, pady=5)



    # Функция вывода окна списка фильмов
    def movie_list():
        #Обозначаем окно списка фильмов
        movies = new_window(350, 500, menu, "Список фильмов")
        movies.protocol("WM_DELETE_WINDOW", lambda: exit_window(movies, menu))

        #Загружаем датасет с фильмами
        movie_data = pd.read_csv('movies.csv')
        current_movies = movie_data.copy()

        #Настраиваем сетку
        movies.grid_columnconfigure(0, weight=1)
        movies.grid_rowconfigure(2, weight=1)

        #Создаём панель поиска
        search_frame = Frame(movies)
        search_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        search_frame.grid_columnconfigure(0, weight=1)

        #Поле ввода текста
        search_entry = ttk.Entry(search_frame)
        search_entry.grid(row=0, column=0, sticky="ew")

        #Функция поиска
        def search_movies():
            #Берём текст из текстового поля search_entry и убираем чувствительность к регистру
            query = search_entry.get().lower()

            #Очищаем список фильмов
            moviesListBox.delete(0, END)

            #Фильтруем данные, сравнивая значения с query
            nonlocal current_movies

            current_movies = movie_data[
                movie_data['title'].str.lower().str.contains(query, na=False)
            ]

            #Добаляем отфильтрованные значения в список
            for title in current_movies['title']:
                moviesListBox.insert(END, title)

        #Обозначаем кнопку
        search_btn = ttk.Button(search_frame, text="Поиск", command=search_movies)
        search_btn.grid(row=0, column=1, padx=(5, 0))

        #Создаём список
        #Обозначаем контейнер для списка фильмов
        frame_left = Frame(movies)
        frame_left.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        frame_left.grid_rowconfigure(0, weight=1)
        frame_left.grid_columnconfigure(0, weight=1)

        #Создаём список, добавляя в него элемент Scrollbar
        moviesListBox = Listbox(frame_left)
        scrollbar = Scrollbar(frame_left, orient="vertical")

        moviesListBox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=moviesListBox.yview)

        moviesListBox.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        #Добавляем элементы из датасета в список
        for title in movie_data['title']:
            moviesListBox.insert(END, title)

        #Код вывода жанров фильма
        #Задаём стартовый label
        genre_label = ttk.Label(movies, text="Жанр:")
        genre_label.grid(column=0, row=3, padx=10, pady=(10, 0), sticky="w")

        #Задаём label, в котором будут выводится жанры
        genres = ttk.Label(movies, text="")
        genres.grid(column=0, row=4, padx=10, pady=5, sticky="ew")

        #Функция для изменения genres, чтобы выводить жанры фильма
        def show_genre(event):
            #Проверяем выбрал ли пользователь фильм
            if not moviesListBox.curselection():
                return

            #Находим жанр фильма из ListBox по индексу
            idx = moviesListBox.curselection()[0]
            genre = current_movies.iloc[idx]['genres']

            #Меняем параметр genre_label
            genre_label.config(text=f"Жанр: {genre}")

        #Связываем выбор элемента списка с обработкой жанра
        moviesListBox.bind("<<ListboxSelect>>", show_genre)

        # Функция вывода окна для оценки фильма
        def rate_movie():
            # Проверка выбран ли фильм
            if not moviesListBox.curselection():
                messagebox.showerror(title="Ошибка", message="Фильм не выбран")
                return

            # Берём индекс выбранного фильма
            idx = moviesListBox.curselection()[0]

            # Берём movieId выбранного фильма
            movie_id = current_movies.iloc[idx]['movieId']

            global df

            #Проверка: есть ли уже фильм в профиле
            if movie_id in df['movieId'].values:
                messagebox.showinfo("Информация", "Фильм уже оценён")
                return

            # Открываем окно оценки
            open_rating_window(movies, current_movies, idx)

        #Обозначаем кнопку для выставления оценки фильма
        rating = ttk.Button(movies, text='Оценить фильм', command=rate_movie)
        rating.grid(column=0, row=5, sticky="ew", padx=10, pady=5)

        #Обозначаем кнопку для возвращения в главное меню
        back_button(movies, 6)


    #Кнопка для списка фильмов
    mlist = ttk.Button(menu, text="Выбрать фильм", command=movie_list)
    mlist.grid(column=0, row=0, sticky=NSEW, padx=10, pady=5)

    # Функция вывода окна списка фильмов, просмотренных пользователем
    def my_list():
        # Задаём окно основного меню
        mymovies = new_window(350, 500, menu, "Мои фильмы")
        mymovies.protocol("WM_DELETE_WINDOW", lambda: exit_window(mymovies, menu))

        #Задаём столбцы для Treeview
        columns = ('title', 'rating')

        #Задаём древо
        tree = ttk.Treeview(mymovies, columns=columns, show='headings',  height=15)

        # Задаём заголовки
        tree.heading('title', text='Название')
        tree.heading('rating', text='Оценка')

        # Настраиваем ширину колонок
        tree.column('title', width=200, anchor='w')
        tree.column('rating', width=80, anchor='center')

        # Размещаем таблицу
        tree.grid(row=1, column=0, padx=10, pady=10)

        # Настройка растягивания окна
        mymovies.grid_rowconfigure(0, weight=1)
        mymovies.grid_columnconfigure(0, weight=1)

        global df
        for _, row in df.iterrows():
            tree.insert("", END, values=(row['title'], row['rating']))

        def change():
            # Проверка выбран ли фильм
            if not tree.selection():
                messagebox.showerror(title="Ошибка", message="Фильм не выбран")
                return

            # Берём выбранный элемент
            selected_item = tree.selection()[0]
            values = tree.item(selected_item)['values']

            title = values[0]

            global df

            # Находим индекс в df
            idx = df[df['title'] == title].index[0]

            # Открываем окно оценки в режиме редактирования
            open_rating_window(mymovies, df, idx, edit=True, tree=tree, item=selected_item)


        def delete():
            # Проверка выбран ли фильм
            if not tree.selection():
                messagebox.showerror(title="Ошибка", message="Фильм не выбран")
                return

            # Берём выбранный элемент
            selected_item = tree.selection()[0]
            values = tree.item(selected_item)['values']

            title = values[0]

            global df

            # Удаляем из DataFrame
            df = df[df['title'] != title]

            # Удаляем из Treeview
            tree.delete(selected_item)

        # Контейнер для кнопок
        btn_frame = Frame(mymovies)
        btn_frame.grid(row=0, column=0, pady=10, sticky="ew")

        # Растягиваем колонку
        btn_frame.grid_columnconfigure(0, weight=1)

        # Кнопки
        change_btn = ttk.Button(btn_frame, text="Изменить", command=change)
        change_btn.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        delete_btn = ttk.Button(btn_frame, text="Удалить", command=delete)
        delete_btn.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        back_button(mymovies, 2)


    #Кнопка для списка фильмов, просмотренных пользователем
    mylist = ttk.Button(menu, text="Мои фильмы", command=my_list)
    mylist.grid(column=0, row=1, sticky=NSEW, padx=10, pady=5)

    # Функция вывода окна списка фильмов, просмотренных пользователем
    def recommend():
        # Если нет рекомендаций
        if df.empty:
            messagebox.showinfo("Рекомендации", "Нет данных для рекомендаций")
            return

        # Задаём окно
        recom = new_window(400, 500, menu, "Рекомендации")
        recom.protocol("WM_DELETE_WINDOW", lambda: exit_window(recom, menu))

        # Загружаем фильмы
        movies_data = pd.read_csv(resource_path("movies.csv"))

        # Получаем рекомендации
        result = nn_recommendations_gui(
            df,
            movies_data,
            model,
            movie_map
        )

        # Настройка сетки
        recom.grid_columnconfigure(0, weight=1)
        recom.grid_rowconfigure(0, weight=1)

        # Контейнер под список
        frame = Frame(recom)
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Listbox + Scrollbar
        listbox = Listbox(frame)
        scrollbar = Scrollbar(frame, orient="vertical")

        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)

        listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Заполняем список (ТОЛЬКО названия)
        for title in result['title']:
            listbox.insert(END, title)

        # Кнопка назад
        back_button(recom, 1)


    #Кнопка для вывода рекомендаций
    rec = ttk.Button(menu, text="Рекомендации", command=recommend)
    rec.grid(column=0, row=2, sticky=NSEW, padx=10, pady=5)

    #Функция сохранения файла
    def save_file():
        global df
        #Задаём путь с помощью диалогового окна и обзначаем формат файлов
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        #Сохраняем
        if filepath:
            try:
                df.to_excel(filepath, index=False)
                print("Файл сохранён")
            except Exception as e:
                print("Ошибка при сохранении:", e)

    #Кнопка для сохранения профиля пользователя
    save = ttk.Button(menu, text="Сохранить профиль", command=save_file)
    save.grid(column=0, row=3, sticky=NSEW, padx=10, pady=5)

#Задаём функцию открытия файла
def open_file():
    global df
    filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if filepath:
        try:
            df = pd.read_excel(filepath)

            main_menu()
        except Exception as e:
            print("Ошибка при чтении файла:", e)

#Функия создания нового профиля
def new_file():
    #объявляем глобальную переменную df
    global df
    #Создаём пустой DataFrame
    df = pd.DataFrame(columns = ["movieId", "rating", "title", "genres"])

    main_menu()

#Ставим запрет на изменения размеров окна
root.resizable(False, False)

label = ttk.Label(text="Загрузите существующий или создайте новый профиль")
label.grid(column=0, row=0, columnspan=2)

#Задаём кнопки
load = ttk.Button(text="Загрузить профиль", command = open_file)
load.grid(column=0, row=1, sticky=NSEW, padx=10)

new = ttk.Button(text="Создать новый профиль", command=new_file)
new.grid(column=1, row=1, sticky=NSEW, padx=10)

root.mainloop()
