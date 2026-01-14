import sqlite3
from datetime import datetime

conn = sqlite3.connect("database.db")
c = conn.cursor()

# USERS
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    role TEXT
)
""")

# TASKS
c.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    category TEXT,
    priority TEXT,
    status TEXT,
    assignee_id TEXT,
    due_date TEXT,
    created_date TEXT,
    attachment TEXT,
    dependency_id INTEGER,
    FOREIGN KEY (assignee_id) REFERENCES users(user_id)
)
""")

# COMMENTS
c.execute("""
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    user TEXT,
    comment TEXT,
    timestamp TEXT
)
""")

# ACTIVITY LOG
c.execute("""
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT,
    timestamp TEXT
)
""")

# SAMPLE USERS (20 members simulated)
users = [
    ("U01","Aarav","Admin"),("U02","Diya","Manager"),("U03","Kabir","Member"),
    ("U04","Aditi","Member"),("U05","Rohan","Member")
]

c.executemany("INSERT OR IGNORE INTO users VALUES (?,?,?)", users)

conn.commit()
conn.close()

print("Database initialized completely")
