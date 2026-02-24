import sqlite3
import os

class Database:
    def __init__(self, db_path="data/session.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def _execute_query(self, query, params=None, is_many=False):
        """Helper to ensure connection and cursor closure."""
        conn = self.get_connection()
        try:
            with conn:
                if is_many:
                    conn.executemany(query, params)
                else:
                    conn.execute(query, params or ())
        finally:
            conn.close()

    def init_db(self):
        self._execute_query("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                event_type TEXT,
                x INTEGER,
                y INTEGER,
                window_title TEXT
            )
        """)

    def log_event(self, event_type, x, y, window_title=""):
        import time
        self._execute_query(
            "INSERT INTO events (timestamp, event_type, x, y, window_title) VALUES (?, ?, ?, ?, ?)",
            (time.time(), event_type, x, y, window_title)
        )

    def log_events_batch(self, events):
        """Log a batch of events for better performance."""
        self._execute_query(
            "INSERT INTO events (timestamp, event_type, x, y, window_title) VALUES (?, ?, ?, ?, ?)",
            events,
            is_many=True
        )

    def clear_data(self):
        """Clear all tracking data."""
        self._execute_query("DELETE FROM events")

