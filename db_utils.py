import sqlite3

DB_FILE = "counter.db"

def init_db():
    print("🔧 Initializing counter database...")
    conn = sqlite3.connect(DB_FILE)
    print("✅ Connected to database:", DB_FILE)

    cursor = conn.cursor()
    print("📄 Creating table if it does not exist...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS insertion_counter (
            id INTEGER PRIMARY KEY,
            count INTEGER
        )
    """)

    print("📌 Ensuring counter row exists (id=1)...")
    cursor.execute(
        "INSERT OR IGNORE INTO insertion_counter (id, count) VALUES (1, 0)"
    )

    conn.commit()
    print("💾 Database changes committed.")
    conn.close()
    print("🔒 Database connection closed.\n")


def increment_counter():
    print("➕ Incrementing insertion counter...")
    conn = sqlite3.connect(DB_FILE)
    print("✅ Connected to database.")

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE insertion_counter SET count = count + 1 WHERE id = 1"
    )

    conn.commit()
    print("📈 Counter incremented successfully.")
    conn.close()
    print("🔒 Database connection closed.\n")


def get_counter():
    print("🔍 Fetching current insertion counter value...")
    conn = sqlite3.connect(DB_FILE)
    print("✅ Connected to database.")

    cursor = conn.cursor()
    cursor.execute(
        "SELECT count FROM insertion_counter WHERE id = 1"
    )

    count = cursor.fetchone()[0]
    print(f"📊 Current counter value: {count}")

    conn.close()
    print("🔒 Database connection closed.\n")
    return count


def reset_counter():
    print("♻️ Resetting insertion counter to 0...")
    conn = sqlite3.connect(DB_FILE)
    print("✅ Connected to database.")

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE insertion_counter SET count = 0 WHERE id = 1"
    )

    conn.commit()
    print("🔁 Counter reset successfully.")
    conn.close()
    print("🔒 Database connection closed.\n")
