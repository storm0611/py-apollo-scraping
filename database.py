import sqlite3
from sqlite3 import Connection

class SQLite:

    db_name = 'history.db'
    table_name = 'history'
    conn = None

    def __init__(self):
        self.connect_db()
        self.create_table()

    def connect_db(self):
        self.conn = sqlite3.connect(self.db_name)

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} (id INTEGER PRIMARY KEY, pid TEXT)")

    def insert(self, pid: str):
        cursor = self.conn.cursor()
        cursor.execute(f"INSERT INTO {self.table_name} (pid) VALUES (?)", (pid))
        self.conn.commit()

    def select(self, pid: str):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {self.table_name} WHERE pid='{pid}'")
        rows = cursor.fetchall()
        return rows

    def disconnect_db(self):
        self.conn.close()

my_sqlite = SQLite()