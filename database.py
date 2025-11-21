import psycopg2

# -----------------------------
# Kết nối database
# -----------------------------
def get_db_connection():
    return psycopg2.connect(
        dbname="week4db",
        user="postgres",
        password="aloalo123",
        host="localhost",
        port="5432"
    )

# -----------------------------
# User-related functions
# -----------------------------
def get_user_by_username(username):
    """Lấy user theo username"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password, role FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user  # trả về tuple (id, username, password, role)

def create_user(username, password, role="user"):
    """Tạo user mới"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
        (username, password, role)
    )
    conn.commit()
    cur.close()
    conn.close()

# -----------------------------
# Task-related functions
# -----------------------------
def get_all_tasks():
    """Lấy tất cả task (admin)"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, status, user_id FROM tasks ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "title": r[1], "description": r[2], "status": r[3], "user_id": r[4]} for r in rows]

def get_tasks_by_user(user_id):
    """Lấy task theo user"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, status, user_id FROM tasks WHERE user_id=%s ORDER BY id", (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "title": r[1], "description": r[2], "status": r[3], "user_id": r[4]} for r in rows]

def get_task(task_id):
    """Lấy task theo id"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, status, user_id FROM tasks WHERE id=%s", (task_id,))
    r = cur.fetchone()
    cur.close()
    conn.close()
    if r:
        return {"id": r[0], "title": r[1], "description": r[2], "status": r[3], "user_id": r[4]}
    return None

def create_task(title, description, status, user_id):
    """Tạo task mới"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, description, status, user_id) VALUES (%s,%s,%s,%s) RETURNING id",
        (title, description, status, user_id)
    )
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return task_id

def update_task(task_id, title=None, description=None, status=None):
    """Cập nhật task"""
    conn = get_db_connection()
    cur = conn.cursor()
    if title:
        cur.execute("UPDATE tasks SET title=%s WHERE id=%s", (title, task_id))
    if description:
        cur.execute("UPDATE tasks SET description=%s WHERE id=%s", (description, task_id))
    if status:
        cur.execute("UPDATE tasks SET status=%s WHERE id=%s", (status, task_id))
    conn.commit()
    cur.close()
    conn.close()

def delete_task(task_id):
    """Xóa task"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()
