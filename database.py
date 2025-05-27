import logging
import sqlite3

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()


def __create_table():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS homes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            link TEXT NOT NULL,
            price TEXT NOT NULL
        )
    ''')
    conn.commit()


def __is_home_exists(link):
    cursor.execute('SELECT * FROM homes WHERE link = ?', (link,))
    return cursor.fetchone() is not None


def check_and_add_home(link, title, price):
    __create_table()

    if __is_home_exists(link):
        return True

    logging.info(f"Adding new home: {title}, link: {link}, price: {price}")
    cursor.execute('INSERT INTO homes (link,title, price) VALUES (?,?, ?)', (link, title, price))
    conn.commit()
    return False
