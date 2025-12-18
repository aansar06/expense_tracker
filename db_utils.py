import sqlite3

DB_FILE = "counter.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS insertion_counter (
            id INTEGER PRIMARY KEY,
            count INTEGER
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO insertion_counter (id, count) VALUES (1, 0)")
    conn.commit()
    conn.close()

def increment_counter():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE insertion_counter SET count = count + 1 WHERE id=1")
    conn.commit()
    conn.close()

def get_counter():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT count FROM insertion_counter WHERE id=1")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def reset_counter():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE insertion_counter SET count=0 WHERE id=1")
    conn.commit()
    conn.close()
