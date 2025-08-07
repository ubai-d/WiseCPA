# Placeholder for database functions (Postgres or SQLite)
import sqlite3

def init_db(db_path="taxwise.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS filings (
        id INTEGER PRIMARY KEY,
        user TEXT,
        raw_text TEXT,
        deductions TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def save_filing(user, raw_text, deductions, db_path="taxwise.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO filings (user, raw_text, deductions) VALUES (?, ?, ?)", (user, raw_text, deductions))
    conn.commit()
    conn.close()
