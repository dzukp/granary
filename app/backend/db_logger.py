import sqlite3
from datetime import datetime
from pathlib import Path


class DbLogger:
    def __init__(self, db_path, init_sql_path='init.sql'):
        self.conn = sqlite3.connect(db_path)
        self._init_db(init_sql_path)

    def _init_db(self, init_sql_path):
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table' AND name = 'messages'
        """)

        if cursor.fetchone() is None:
            with open(init_sql_path, 'r', encoding='utf-8') as f:
                self.conn.executescript(f.read())

            self.conn.commit()

    def save_message(self, text, level):
        now = datetime.now()
        self.conn.execute(
            """
            INSERT INTO messages (dtime, tstamp, message, lvl)
            VALUES (?, ?, ?, ?)
            """,
            (
                now.strftime('%d.%m.%Y %H:%M:%S'),
                int(now.timestamp()),
                text,
                level,
            ),
        )
        self.conn.commit()

    def info(self, text):
        self.save_message(text, 'info')

    def error(self, text):
        self.save_message(text, 'error')

    def warning(self, text):
        self.save_message(text, 'warning')

    def close(self):
        self.conn.close()


db_logger = DbLogger(
    db_path=str(Path(__file__).resolve().parent.parent / 'hmi/Data_granary/main.db'),
    init_sql_path=str(Path(__file__).resolve().parent.parent / 'res/init.sql'),
)
