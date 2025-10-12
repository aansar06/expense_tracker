import pandas as pd
import sqlite3

# -------------------------------
# File paths
# -------------------------------
transactions_csv = "transactions_dataset.csv"
backup_csv = "backup_dataset.csv"
db_file = "expense_tracker.db"

# -------------------------------
# Load CSVs
# -------------------------------
transactions_df = pd.read_csv(transactions_csv)
backup_df = pd.read_csv(backup_csv)

# -------------------------------
# Connect to SQLite database
# -------------------------------
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# -------------------------------
# Create tables
# -------------------------------

# Transactions table
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_category TEXT NOT NULL,
    merchant TEXT NOT NULL
)
""")

# Backup merchants table
cursor.execute("""
CREATE TABLE IF NOT EXISTS backup_merchants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL
)
""")

# -------------------------------
# Insert data into tables
# -------------------------------

# Transactions: append all rows
transactions_df.to_sql("transactions", conn, if_exists="replace", index=False)

# Backup merchants: handle duplicates
for _, row in backup_df.iterrows():
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO backup_merchants (merchant, category) VALUES (?, ?)",
            (row['merchant'].lower(), row['merchant_category'])
        )
    except Exception as e:
        print(f"Error inserting {row['merchant']}: {e}")

conn.commit()
conn.close()

print("✅ CSVs successfully stored in SQLite database!")
