from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime, date

app = Flask(__name__)


def get_db():
    return sqlite3.connect("database.db")

VALID_TRANSITIONS = {
    "Pending": ["In Progress"],
    "In Progress": ["Blocked", "Completed"],
    "Blocked": ["In Progress"],
    "Completed": []
}


def normalize_status(db):
    """
    Automatically fixes inconsistent status values.
    Runs silently whenever Kanban is opened.
    """
    db.execute("""
        UPDATE tasks
        SET status =
        CASE
            WHEN LOWER(TRIM(status)) IN ('inprogress', 'in progress') THEN 'In Progress'
            WHEN LOWER(TRIM(status)) LIKE 'pending%' THEN 'Pending'
            WHEN LOWER(TRIM(status)) LIKE 'completed%' THEN 'Completed'
            WHEN LOWER(TRIM(status)) LIKE 'blocked%' THEN 'Blocked'
            ELSE status
        END
    """)
    db.commit()


@app.route("/")
def dashboard():
    db = get_db()
    today = date.today().isoformat()

    total_tasks = db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    due_today = db.execute(
        "SELECT COUNT(*) FROM tasks WHERE due_date = ?", (today,)
    ).fetchone()[0]
    overdue = db.execute(
        "SELECT COUNT(*) FROM tasks WHERE due_date < ? AND status != 'Completed'", (today,)
    ).fetchone()[0]
    high_priority = db.execute(
        "SELECT COUNT(*) FROM tasks WHERE priority = 'High'"
    ).fetchone()[0]

    users = db.execute("SELECT user_id, name FROM users").fetchall()

    workload = db.execute("""
    SELECT u.name, COUNT(t.id)
    FROM users u
    LEFT JOIN tasks t ON u.user_id = t.assignee_id
    GROUP BY u.user_id
    """).fetchall()


    tasks = db.execute("""
        SELECT t.id, t.title, t.category, t.priority, t.status,
               t.due_date, u.name
        FROM tasks t
        LEFT JOIN users u ON t.assignee_id = u.user_id
        ORDER BY t.created_date DESC
    """).fetchall()
    
    return render_template(
    "dashboard.html",
    tasks=tasks,
    workload=workload
)


@app.route("/create", methods=["GET", "POST"])
def create():
    db = get_db()

    # fetch existing tasks for dependency dropdown
    tasks = db.execute(
        "SELECT id, title FROM tasks"
    ).fetchall()

    # fetch users for assignee dropdown
    users = db.execute(
        "SELECT user_id, name FROM users"
    ).fetchall()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        category = request.form["category"]
        priority = request.form["priority"]
        status = request.form["status"]
        assignee = request.form["assignee"]
        due_date = request.form["due_date"]
        dependency = request.form["dependency"]

        # convert empty dependency to NULL
        if dependency == "":
            dependency = None

        db.execute("""
            INSERT INTO tasks
            (title, description, category, priority, status, assignee_id, due_date, dependency_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            description,
            category,
            priority,
            status,
            assignee,
            due_date,
            dependency
        ))

        db.commit()
        return redirect("/")

    return render_template(
        "create_task.html",
        users=users,
        tasks=tasks
    )


@app.route("/update_status/<int:task_id>/<new_status>")
def update_status(task_id, new_status):
    db = get_db()

    task = db.execute(
        "SELECT dependency_id FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if task and task["dependency_id"]:
        parent = db.execute(
            "SELECT status FROM tasks WHERE id = ?",
            (task["dependency_id"],)
        ).fetchone()

        if parent and parent["status"] != "Completed" and new_status == "In Progress":
            return "❌ Cannot start task. Parent task not completed."

    db.execute(
        "UPDATE tasks SET status = ? WHERE id = ?",
        (new_status, task_id)
    )
    db.commit()

    return redirect("/")


@app.route("/kanban")
def kanban():
    db = get_db()

    # 🔥 FIX ANY STATUS INCONSISTENCY AUTOMATICALLY
    normalize_status(db)

    pending = db.execute(
        "SELECT title FROM tasks WHERE TRIM(status)='Pending'"
    ).fetchall()
    progress = db.execute(
        "SELECT title FROM tasks WHERE TRIM(status)='In Progress'"
    ).fetchall()
    blocked = db.execute(
        "SELECT title FROM tasks WHERE TRIM(status)='Blocked'"
    ).fetchall()
    completed = db.execute(
        "SELECT title FROM tasks WHERE TRIM(status)='Completed'"
    ).fetchall()

    db.close()

    return render_template(
        "kanban.html",
        pending=pending,
        progress=progress,
        blocked=blocked,
        completed=completed
    )


@app.route("/activity")
def activity():
    db = get_db()
    logs = db.execute("""
        SELECT message, timestamp
        FROM activity_logs
        ORDER BY timestamp DESC
    """).fetchall()
    db.close()
    return render_template("activity.html", logs=logs)


if __name__ == "__main__":
    app.run(debug=True)
