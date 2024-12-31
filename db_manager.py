import sqlite3
from datetime import datetime, timedelta

# Initialize database
def initialize_db():
    conn = sqlite3.connect("reddit_data.db", check_same_thread=False)  # Disable thread check
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS word_data (
            word TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    return conn, cursor

# Save word occurrences to the database
def save_to_db(cursor, data):
    for word, timestamps in data.items():
        for timestamp in timestamps:
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO word_data (word, timestamp) VALUES (?, ?)", (word, timestamp))
    cursor.connection.commit()

# Retrieve data for all words
def get_word_data(cursor, word):
    cursor.execute("SELECT timestamp FROM word_data WHERE word = ?", (word,))
    return [timestamp[0] for timestamp in cursor.fetchall()]
