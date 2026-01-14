import sqlite3

conn = sqlite3.connect("database.db")

conn.execute("""
ALTER TABLE tasks ADD COLUMN status TEXT DEFAULT 'Pending'
""")

conn.commit()
conn.close()

print("Status column added")
