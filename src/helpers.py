import sqlite3

def get_db():
    conn = sqlite3.connect("tasks.db")
    try:
        yield conn
    finally:
        conn.close()