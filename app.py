from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from database import (
    get_user_by_username, create_user, get_user_by_id,
    get_all_users, update_user, delete_user,
    get_all_tasks_admin, get_tasks_by_user, get_task,
    create_task, update_task, delete_task
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

# -----------------------------
# Routes: Auth
# -----------------------------
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

@app.route("/login", methods=["GET", "POST"])
def login_route():
    username_value = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        username_value = username

        if not username:
            flash("Bạn chưa nhập username!", "danger")
        elif not password:
            flash("Bạn chưa nhập password!", "danger")
        else:
            user = get_user_by_username(username)
            if not user or user["password"] != password:
                flash("Sai username hoặc password!", "danger")
            else:
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["role"] = user["role"]
                flash("Đăng nhập thành công!", "success")
                return redirect(url_for("index_route"))

    return render_template("login.html", username_value=username_value)

@app.route("/logout")
def logout_route():
    session.clear()
    flash("Bạn đã đăng xuất!", "success")
    return redirect(url_for("login_route"))

# -----------------------------
# Routes: Dashboard
# -----------------------------
@app.route("/")
@login_required
def index_route():
    if session["role"] == "admin":
        tasks = get_all_tasks_admin()
    else:
        tasks = get_tasks_by_user(session["user_id"])
    return render_template("tasks.html", tasks=tasks, username=session["username"], role=session["role"])

# -----------------------------
# Routes: Tasks
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

@app.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
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

@app.route("/delete_task/<int:task_id>")
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
# Routes: Admin User Management
# -----------------------------
@app.route("/admin/users", methods=["GET", "POST"])
@login_required
@role_required("admin")
def admin_users_route():
    edit_user = None
    users = get_all_users()  # lấy tất cả user từ database

    # Nếu có query ?edit=ID thì load user để edit
    edit_id = request.args.get("edit")
    if edit_id:
        edit_user = get_user_by_id(int(edit_id))

    # Xử lý form POST
    if request.method == "POST":
        user_id = request.form.get("user_id")
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        role = request.form.get("role", "user")

        if user_id:  # update
            update_user(user_id, username, password if password else None, role)
            flash("User đã cập nhật!", "success")
        else:  # tạo mới
            create_user(username, password, role)
            flash("User đã thêm!", "success")
        return redirect(url_for("admin_users_route"))

    return render_template("admin_users.html", users=users, edit_user=edit_user)


@app.route("/admin/edit_user/<int:user_id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def admin_edit_user_route(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash("User không tồn tại!", "danger")
        return redirect(url_for("admin_users_route"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        role = request.form.get("role", "user")
        password = request.form.get("password", "").strip()  # optional

        if not username:
            flash("Username không được để trống!", "danger")
        else:
            update_user(user_id, username, role, password if password else None)
            flash("User đã cập nhật!", "success")
            return redirect(url_for("admin_users_route"))

    return render_template("edit_user.html", user=user)

@app.route("/admin/delete_user/<int:user_id>")
@login_required
@role_required("admin")
def admin_delete_user_route(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash("User không tồn tại!", "danger")
    else:
        delete_user(user_id)
        flash("User đã bị xóa!", "success")
    return redirect(url_for("admin_users_route"))

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)


