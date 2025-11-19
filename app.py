from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
import hashlib

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Bắt buộc để flash hoạt động


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

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
# Route: đăng nhập
# -----------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Hash password (nếu dùng hashing)
        # password_hash = hashlib.sha256(password.encode()).hexdigest()
        password_hash = password  # dùng plain text thử nghiệm

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username FROM users WHERE username=%s AND password=%s",
                    (username, password_hash))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for('index'))
        else:
            flash("Sai username hoặc password!", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')


# -----------------------------
# Route: đăng xuất
# -----------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("Bạn đã đăng xuất!", "success")
    return redirect(url_for('login'))


# -----------------------------
# Route: đăng ký
# -----------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Thêm user vào DB
        conn = get_db_connection()
        cur = conn.cursor()
        # Lưu password plain text cho dễ thử nghiệm, sau này dùng hash
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        cur.close()
        conn.close()

        flash("Đăng ký thành công! Hãy đăng nhập.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')


# -----------------------------
# Route: danh sách tasks
# -----------------------------
@app.route('/')
@login_required
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
@login_required
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
@login_required
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
@login_required
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
