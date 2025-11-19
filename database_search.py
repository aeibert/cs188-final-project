import pyodbc
from datetime import datetime
from config import CONNECTION_STRING

def log_search(title, search_type):
    conn = pyodbc.connect(CONNECTION_STRING)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO SearchHistory (title, search_type, timestamp)
        VALUES (?, ?, ?)
    """, (title, search_type, datetime.utcnow()))

    conn.commit()
    conn.close()
