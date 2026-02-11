import sqlite3

DB_PATH = "posted.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS posted_tweets (
            tweet_id TEXT PRIMARY KEY
        )
    """)
    conn.commit()
    conn.close()

def already_posted(tweet_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM posted_tweets WHERE tweet_id = ?", (tweet_id,))
    row = c.fetchone()
    conn.close()
    return row is not None

def mark_posted(tweet_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO posted_tweets (tweet_id) VALUES (?)", (tweet_id,))
    conn.commit()
    conn.close()
