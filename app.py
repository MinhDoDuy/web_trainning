from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from database import (
    get_user_by_username, create_user,
    get_all_tasks_admin, get_tasks_by_user,
    get_task, create_task, update_task, delete_task
)

app = Flask(__name__)
app.secret_key = "supersecretkey"

# -----------------------------
# Decorators
# -----------------------------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Bạn cần đăng nhập!", "warning")
            return redirect(url_for("login_route"))
        return f(*args, **kwargs)
    return wrapper

def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get("role") != role:
                flash("Bạn không có quyền truy cập!", "danger")
                return redirect(url_for("index_route"))
            return f(*args, **kwargs)
        return wrapper
    return decorator

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register_route():
    username_value = ""
    role_value = "user"
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "user")
        username_value = username
        role_value = role

        if not username:
            flash("Bạn chưa nhập username!", "danger")
        elif not password:
            flash("Bạn chưa nhập password!", "danger")
        elif get_user_by_username(username):
            flash("Tài khoản đã tồn tại!", "danger")
        else:
            create_user(username, password, role)
            flash("Đăng ký thành công!", "success")
            return redirect(url_for("login_route"))

    return render_template("register.html", username_value=username_value, role_value=role_value)

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login_route():
    username_value = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        username_value = username  # giữ lại username nhập

        if not username:
            flash("Bạn chưa nhập username!", "danger")
        elif not password:
            flash("Bạn chưa nhập password!", "danger")
        else:
            user = get_user_by_username(username)
            if not user or user[2] != password:
                flash("Sai username hoặc password!", "danger")
            else:
                session["user_id"] = user[0]
                session["username"] = user[1]
                session["role"] = user[3]
                flash("Đăng nhập thành công!", "success")
                return redirect(url_for("index_route"))

    return render_template("login.html", username_value=username_value)



@app.route("/logout")
def logout_route():
    session.clear()
    flash("Bạn đã đăng xuất!", "success")
    return redirect(url_for("login_route"))

# -----------------------------
# Route: Tasks
# -----------------------------
@app.route("/")
@login_required
def index_route():
    if session["role"] == "admin":
        tasks = get_all_tasks_admin()  # admin xem tất cả
    else:
        tasks = get_tasks_by_user(session["user_id"])  # user xem của mình
    return render_template("tasks.html", tasks=tasks, username=session["username"], role=session["role"])

# -----------------------------
# Route: Add Task
# -----------------------------
@app.route("/add_task", methods=["POST"])
@login_required
def add_task_route():
    title = request.form.get("title")
    description = request.form.get("description")
    status = request.form.get("status")
    create_task(title, description, status, session["user_id"])
    flash("Task thêm thành công!", "success")
    return redirect(url_for("index_route"))

# -----------------------------
# Route: Edit Task
# -----------------------------
@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task_route(task_id):
    task = get_task(task_id)
    if not task:
        flash("Task không tồn tại!", "danger")
        return redirect(url_for("index_route"))

    if session["role"] != "admin" and task["user_id"] != session["user_id"]:
        flash("Bạn không có quyền sửa task này!", "danger")
        return redirect(url_for("index_route"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        status = request.form.get("status")
        update_task(task_id, title, description, status)
        flash("Task đã cập nhật!", "success")
        return redirect(url_for("index_route"))

    return render_template("edit_task.html", task=task)

# -----------------------------
# Route: Delete Task
# -----------------------------
@app.route("/delete/<int:task_id>")
@login_required
@role_required("admin")
def delete_task_route(task_id):
    task = get_task(task_id)
    if not task:
        flash("Task không tồn tại!", "danger")
    else:
        delete_task(task_id)
        flash("Task đã xóa!", "success")
    return redirect(url_for("index_route"))

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)
