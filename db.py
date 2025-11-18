import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="week4db",
        user="postgres",
        password="aloalo123",
        host="localhost",
        port="5432"
    )

def get_all_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY id")
    tasks = cursor.fetchall()
    conn.close()
    return [{"id": t[0], "title": t[1], "description": t[2], "status": t[3]} for t in tasks]

def get_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id=%s", (task_id,))
    t = cursor.fetchone()
    conn.close()
    if t:
        return {"id": t[0], "title": t[1], "description": t[2], "status": t[3]}
    return None

def create_task(title, description, status="pending"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, description, status) VALUES (%s,%s,%s) RETURNING id",
                   (title, description, status))
    task_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return task_id

def update_task(task_id, title=None, description=None, status=None):
    conn = get_connection()
    cursor = conn.cursor()
    if title:
        cursor.execute("UPDATE tasks SET title=%s WHERE id=%s", (title, task_id))
    if description:
        cursor.execute("UPDATE tasks SET description=%s WHERE id=%s", (description, task_id))
    if status:
        cursor.execute("UPDATE tasks SET status=%s WHERE id=%s", (status, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    conn.commit()
    conn.close()
