import csv
import sqlite3
from datetime import datetime, timedelta

current_date = datetime.now().date()
one_month_ago = current_date - timedelta(days=30)

# Создание соединения с базой данных в памяти
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Создание таблицы Книги в базе данных
cursor.execute('''CREATE TABLE Книги (
    ID_книги INTEGER,
    Название TEXT,
    Автор TEXT,
    Издательство TEXT,
    Город_издания TEXT,
    Количество_страниц INTEGER,
    ID_экземпляра INTEGER,
    Дата_поступления_в_библиотеку INTEGER
)''')

# Чтение данных из CSV файла и вставка их в таблицу Книги
with open('Задача3_Книги.csv', 'r', newline='', encoding='cp1251') as file:
    reader = csv.reader(file, delimiter=';')
    next(reader)  # Пропуск заголовка
    for row in reader:
        # Преобразование даты поступления в библиотеку в формат SQLite
        date = row[7]
        converted_date = f"{int(date[-4:]) - 5}-{date[3:5]}-{date[:2]}"
        row[7] = converted_date

        cursor.execute('''INSERT INTO Книги (
            ID_книги, Название, Автор, Издательство, Город_издания,
            Количество_страниц, ID_экземпляра, Дата_поступления_в_библиотеку
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', row)

# Создание таблицы Выдача в базе данных
cursor.execute('''CREATE TABLE Выдача (
    ID_экземпляра INTEGER,
    Дата_выдачи DATE,
    Дата_возврата DATE,
    Читательский_билет INTEGER
)''')

# Чтение данных из CSV файла и вставка их в таблицу Выдача
with open('Задача3_Выдачи книг.csv', 'r', newline='', encoding='cp1251') as file:
    reader = csv.reader(file, delimiter=';')
    next(reader)  # Пропуск заголовка
    for row in reader:
        cursor.execute('''INSERT INTO Выдача (
            ID_экземпляра, Дата_выдачи, Дата_возврата, Читательский_билет
        ) VALUES (?, ?, ?, ?)''', row)

# Создание таблицы Читатели в базе данных
cursor.execute('''CREATE TABLE Читатели (
    Читательский_билет INTEGER,
    Фамилия TEXT,
    Имя TEXT,
    Отчество TEXT,
    Дата_рождения DATE,
    Пол TEXT,
    Адрес TEXT,
    Телефон TEXT
)''')

# Чтение данных из CSV файла и вставка их в таблицу Читатели
with open('Задача3_Читатели.csv', 'r', newline='', encoding='cp1251') as file:
    reader = csv.reader(file, delimiter=';')
    next(reader)  # Пропуск заголовка
    for row in reader:
        cursor.execute('''INSERT INTO Читатели (
            Читательский_билет, Фамилия, Имя, Отчество, Дата_рождения,
            Пол, Адрес, Телефон
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', row)

# Выполнение SQL-запроса для поиска городов с наибольшим числом книг в 2016 году
query = '''
    SELECT Город_издания, COUNT(*) AS Количество_книг
    FROM Книги
    WHERE strftime('%Y', Дата_поступления_в_библиотеку) = '2016'
    GROUP BY Город_издания
    ORDER BY Количество_книг DESC
'''

cursor.execute(query)
results = cursor.fetchall()

# Вывод результатов
print("Города, в которых в 2016 году было издано больше всего книг:")
for row in results:
    print(f"Город: {row[0]}, Количество книг: {row[1]}")

# Выполнение SQL-запроса для поиска количества экземпляров книг "Война и мир" Л.Н.Толстого
query2 = '''
    SELECT COUNT(*) AS Количество_экземпляров
    FROM Книги
    WHERE Название = "Война и мир" AND Автор = "Л.Н.Толстой"
'''

cursor.execute(query2)
result2 = cursor.fetchone()

print()  # Пустая строка
print("Количество экземпляров книг 'Война и мир' Л.Н.Толстого, которые находятся в библиотеке:")
print(f"Количество экземпляров: {result2[0]}")

# Выполнение SQL-запроса для поиска читателей, которые за последний месяц брали больше всего книг и выполнить сортировку читателей по возрасту (от молодых к старшим)
query3 = '''
    SELECT Читатели.Фамилия, Читатели.Имя, Читатели.Отчество, COUNT(*) AS Количество_книг
    FROM Читатели
    JOIN Выдача ON Читатели.Читательский_билет = Выдача.Читательский_билет
    WHERE Выдача.Дата_выдачи >= ? AND Выдача.Дата_выдачи <= ?
    GROUP BY Читатели.Фамилия, Читатели.Имя, Читатели.Отчество
    ORDER BY Читатели.Дата_рождения ASC
'''
# из-за отсутствия значения в поле "Дата рождения" у некоторых читателей
# пустые значения будут рассматриваться как "наименьшие" значения при сортировке,
# поэтому они будут располагаться в начале результата

cursor.execute(query3, (one_month_ago, current_date))
results3 = cursor.fetchall()

print()  # Пустая строка
print(
    "Читатели, которые за последний месяц брали больше всего книг с сортировкой читателей по возрасту (от молодых к старшим):")
for row in results3:
    print(f"Фамилия: {row[0]}, Имя: {row[1]}, Отчество: {row[2]}, Количество книг: {row[3]}")

# Закрытие соединения с базой данных
conn.close()
