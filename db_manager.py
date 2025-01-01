import sqlite3
import time

# Initialize database
def initialize_db():
    conn = sqlite3.connect("reddit_data.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS word_data (
            word TEXT,
            timestamp TEXT,
            UNIQUE(word, timestamp)  -- Prevent duplicate entries
        )
    """)
    conn.commit()
    return conn, cursor

# Save word occurrences to the database
def save_to_db(data):
    retries = 5  # Number of retry attempts
    delay = 0.5  # Delay between retries

    conn, cursor = initialize_db()  # Always use a new connection per thread
    try:
        for attempt in range(retries):
            try:
                unique_entries = set()  # Keep track of unique (word, timestamp) pairs
                for word, timestamps in data.items():
                    for timestamp in timestamps:
                        unique_entries.add((word, timestamp))  # Deduplicate in memory

                # Insert unique entries into the database
                cursor.executemany("""
                    INSERT OR IGNORE INTO word_data (word, timestamp)
                    VALUES (?, ?)
                """, list(unique_entries))
                conn.commit()
                break  # Exit loop if successful
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < retries - 1:
                    print(f"Database is locked, retrying... (Attempt {attempt + 1})")
                    time.sleep(delay)  # Wait before retrying
                else:
                    raise  # Re-raise the exception if retries fail
    finally:
        cursor.close()  # Close the cursor after all operations are done
        conn.close()    # Close the connection after all operations are done

# Retrieve data for a specific word
def get_word_data(word):
    """
    Fetch all timestamps for a specific word from the database.
    """
    conn, cursor = initialize_db()
    try:
        cursor.execute("SELECT timestamp FROM word_data WHERE word = ?", (word,))
        data = [timestamp[0] for timestamp in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()  # Close the connection to avoid locks
    return data
