import psycopg2

def get_db_connection():
    return psycopg2.connect(
        dbname="week4db",
        user="postgres",
        password="aloalo123",
        host="localhost",
        port="5432"
    )

# -----------------------------
# User functions
# -----------------------------
def get_user_by_username(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password, role FROM users WHERE username=%s", (username,))
    r = cur.fetchone()
    cur.close()
    conn.close()
    if r:
        return {"id": r[0], "username": r[1], "password": r[2], "role": r[3]}
    return None

def get_user_by_id(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password, role FROM users WHERE id=%s", (user_id,))
    r = cur.fetchone()
    cur.close()
    conn.close()
    if r:
        return {"id": r[0], "username": r[1], "password": r[2], "role": r[3]}
    return None

def get_all_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, role FROM users ORDER BY CASE WHEN role='admin' THEN 0 ELSE 1 END, id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "username": r[1], "role": r[2]} for r in rows]

def create_user(username, password, role="user"):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
        (username, password, role)
    )
    conn.commit()
    cur.close()
    conn.close()

def update_user(user_id, username=None, password=None, role=None):
    conn = get_db_connection()
    cur = conn.cursor()
    if username:
        cur.execute("UPDATE users SET username=%s WHERE id=%s", (username, user_id))
    if password:
        cur.execute("UPDATE users SET password=%s WHERE id=%s", (password, user_id))
    if role:
        cur.execute("UPDATE users SET role=%s WHERE id=%s", (role, user_id))
    conn.commit()
    cur.close()
    conn.close()

def delete_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()

# -----------------------------
# Task functions
# -----------------------------
def get_all_tasks_admin():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT t.id, t.title, t.description, t.status, u.username
        FROM tasks t
        JOIN users u ON t.user_id = u.id
        ORDER BY t.id
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "title": r[1], "description": r[2], "status": r[3], "username": r[4]} for r in rows]

def get_tasks_by_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, status FROM tasks WHERE user_id=%s ORDER BY id", (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "title": r[1], "description": r[2], "status": r[3]} for r in rows]

def get_task(task_id):
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
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, description, status, user_id) VALUES (%s, %s, %s, %s)",
        (title, description, status, user_id)
    )
    conn.commit()
    cur.close()
    conn.close()

def update_task(task_id, title=None, description=None, status=None):
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
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()

    @app.route("/admin/users/delete/<int:user_id>")
    @login_required
    @role_required
    def admin_delete_user_route(user_id):
        user = get_user_by_id(user_id)
        if not user:
            flash("User không tồn tại", "danger")
            return redirect(url_for("admin_users_route"))

        if user["role"] == "admin":
            flash("Không thể xóa user là admin", "danger")
            return redirect(url_for("admin_users_route"))

        delete_user(user_id)
        flash(f"Đã xóa user {user['username']}", "danger")  # toast màu đỏ
        return redirect(url_for("admin_users_route"))

