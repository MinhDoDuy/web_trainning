from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Bắt buộc để flash hoạt động


# -----------------------------
# Hàm kết nối database PostgreSQL
# -----------------------------
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="week4db",  # đổi tên DB của bạn
        user="postgres",
        password="aloalo123"  # đổi mật khẩu DB của bạn
    )
    return conn


# -----------------------------
# Route: danh sách tasks
# -----------------------------
@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, status FROM tasks ORDER BY id ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    tasks = []
    for r in rows:
        tasks.append({
            'id': r[0],
            'title': r[1],
            'description': r[2],
            'status': r[3]
        })

    return render_template("tasks.html", tasks=tasks)


# -----------------------------
# Route: thêm task mới
# -----------------------------
@app.route('/add_task', methods=['POST'])
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')
    status = request.form.get('status')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s)",
        (title, description, status)
    )
    conn.commit()
    cur.close()
    conn.close()

    flash("Task thêm thành công!", "success")
    return redirect(url_for('index'))


# -----------------------------
# Route: sửa task
# -----------------------------
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status')
        cur.execute(
            "UPDATE tasks SET title=%s, description=%s, status=%s WHERE id=%s",
            (title, description, status, task_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        flash("Task cập nhật thành công!", "info")
        return redirect(url_for('index'))

    # GET: lấy dữ liệu task
    cur.execute("SELECT id, title, description, status FROM tasks WHERE id=%s", (task_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row is None:
        flash("Task không tồn tại!", "danger")
        return redirect(url_for('index'))

    task = {
        'id': row[0],
        'title': row[1],
        'description': row[2],
        'status': row[3]
    }

    return render_template("edit_task.html", task=task)


# -----------------------------
# Route: xóa task
# -----------------------------
@app.route('/delete/<int:task_id>')
def delete(task_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()

    flash("Task xóa thành công!", "danger")
    return redirect(url_for('index'))

# -----------------------------
# Run app
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5001)
