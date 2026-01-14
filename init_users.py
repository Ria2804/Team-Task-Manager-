import sqlite3

users = [
    ("Aarav", "Member"),
    ("Diya", "Member"),
    ("Kabir", "Manager"),
    ("Aditi", "Member"),
    ("Rohan", "Member"),
    ("Sneha", "Member"),
    ("Ishaan", "Member"),
    ("Meera", "Member"),
    ("Arjun", "Member"),
    ("Pooja", "Member"),
    ("Rahul", "Member"),
    ("Neha", "Member"),
    ("Karan", "Member"),
    ("Ananya", "Member"),
    ("Vikram", "Member"),
    ("Sanya", "Member"),
    ("Nikhil", "Member"),
    ("Riya", "Member"),
    ("Manish", "Member"),
    ("Priya", "Member"),
]

db = sqlite3.connect("database.db")
db.execute("""
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  role TEXT
)
""")

db.executemany(
    "INSERT INTO users (name, role) VALUES (?, ?)",
    users
)

db.commit()
db.close()

print("✅ 20 users added")
