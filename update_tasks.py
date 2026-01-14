import sqlite3

conn = sqlite3.connect("database.db")

conn.execute("""
ALTER TABLE tasks ADD COLUMN assignee_id TEXT
""")

conn.commit()
conn.close()

print("Assignee column added")
