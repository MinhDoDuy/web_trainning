import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "dbname": "week4db",
    "user": "postgres",
    "password": "aloalo123",
    "host": "localhost",
    "port": "5432"
}

VALID_STATUSES = ['todo', 'doing', 'done']

# -----------------------------
# DB Connection
# -----------------------------
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# -----------------------------
# User functions
# -----------------------------
def get_user_by_username(username):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT id, username, password, role FROM users WHERE username=%s",
        (username,)
    )
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT id, username, password, role FROM users WHERE id=%s",
        (user_id,)
    )
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


def get_all_users():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT id, username, role
        FROM users
        ORDER BY CASE WHEN role='admin' THEN 0 ELSE 1 END, id
    """)
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users


def create_user(username, password, role="user"):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, password, role)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()


def update_user(user_id, username=None, password=None, role=None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        if username:
            cur.execute("UPDATE users SET username=%s WHERE id=%s", (username, user_id))
        if password:
            cur.execute("UPDATE users SET password=%s WHERE id=%s", (password, user_id))
        if role:
            cur.execute("UPDATE users SET role=%s WHERE id=%s", (role, user_id))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def delete_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
    finally:
        cur.close()
        conn.close()

# -----------------------------
# Task functions
# -----------------------------
def get_all_tasks_admin():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT t.id,
               t.title,
               t.description,
               t.status,
               t.assigned_by_admin,
               u.username
        FROM tasks t
        JOIN users u ON t.user_id = u.id
        ORDER BY t.id
    """)
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return tasks


def get_tasks_by_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT id,
               title,
               description,
               status,
               user_id,
               assigned_by_admin
        FROM tasks
        WHERE user_id=%s
        ORDER BY id
    """, (user_id,))
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return tasks


def get_task(task_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT id,
               title,
               description,
               status,
               user_id,
               assigned_by_admin
        FROM tasks
        WHERE id=%s
    """, (task_id,))
    task = cur.fetchone()
    cur.close()
    conn.close()
    return task


def create_task(title, description, status, user_id, assigned_by_admin=False):
    if status not in VALID_STATUSES:
        status = 'todo'

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO tasks (title, description, status, user_id, assigned_by_admin)
            VALUES (%s, %s, %s, %s, %s)
        """, (title, description, status, user_id, assigned_by_admin))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def update_task(task_id, title=None, description=None, status=None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        if title:
            cur.execute("UPDATE tasks SET title=%s WHERE id=%s", (title, task_id))
        if description:
            cur.execute("UPDATE tasks SET description=%s WHERE id=%s", (description, task_id))
        if status and status in VALID_STATUSES:
            cur.execute("UPDATE tasks SET status=%s WHERE id=%s", (status, task_id))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def delete_task(task_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
        conn.commit()
    finally:
        cur.close()
        conn.close()
