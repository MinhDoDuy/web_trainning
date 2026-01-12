from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2.errors import UniqueViolation
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
            flash("You need to log in!", "warning")
            return redirect(url_for("login_route"))
        return f(*args, **kwargs)

    return wrapper


def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get("role") != role:
                flash("You do not have access!", "danger")
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
            flash("You have not entered a username!", "danger")
        elif not password:
            flash("You have not entered a password!", "danger")
        elif get_user_by_username(username):
            flash("Account already exists!", "danger")
        else:
            hashed = generate_password_hash(password)
            try:
                create_user(username, hashed, role)
                flash("Registration successful!", "success")
                return redirect(url_for("login_route"))
            except UniqueViolation:
                flash(f"Username '{username}' already exists!", "warning")

    return render_template("register.html", username_value=username_value, role_value=role_value)


@app.route("/login", methods=["GET", "POST"])
def login_route():
    username_value = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        username_value = username

        if not username:
            flash("You have not entered a username!", "danger")
        elif not password:
            flash("You have not entered a password!", "danger")
        else:
            user = get_user_by_username(username)
            if not user or not check_password_hash(user["password"], password):
                flash("Wrong username or password!", "danger")
            else:
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["role"] = user["role"]
                flash("Login successful!", "success")
                return redirect(url_for("index_route"))

    return render_template("login.html", username_value=username_value)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out!", "success")
    return redirect(url_for("login_route"))


# -----------------------------
# Routes: Forgot Password
# -----------------------------
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password_route():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if not username:
            flash("Please enter your username!", "warning")
        else:
            user = get_user_by_username(username)
            if not user:
                flash("Username does not exist!", "danger")
            else:
                # Nếu đúng username → chuyển sang route reset password
                return redirect(url_for("reset_password_route", username=username))
    return render_template("forgot_password.html")


@app.route("/reset-password/<username>", methods=["GET", "POST"])
def reset_password_route(username):
    user = get_user_by_username(username)
    if not user:
        flash("Invalid username!", "danger")
        return redirect(url_for("forgot_password_route"))

    if request.method == "POST":
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm_password", "").strip()

        if not password or not confirm:
            flash("Please fill in all fields!", "warning")
        elif password != confirm:
            flash("Passwords do not match!", "danger")
        elif check_password_hash(user["password"], password):
            flash("New password cannot be the same as the old password!", "danger")
        else:
            hashed = generate_password_hash(password)
            update_user(user["id"], password=hashed)
            flash("Password has been reset successfully!", "success")
            return redirect(url_for("login_route"))

    return render_template("reset_password.html", username=username)


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
@app.route('/add-task', methods=['POST'])
@login_required
def add_task_route():
    title = request.form.get("title")
    description = request.form.get("description")
    status = request.form.get("status")

    # Lấy danh sách task của user
    if session['role'] == 'admin':
        tasks = get_all_tasks_admin()  # admin xem tất cả
    else:
        tasks = get_tasks_by_user(session['user_id'])  # user chỉ thấy của mình

    if not title or not description:
        flash("Please fill in all fields before adding a task!", "danger")
        return render_template(
            "tasks.html",
            tasks=tasks,
            title_value=title,
            description_value=description,
            status_value=status,
            username=session.get('username'),
            role=session.get('role')
        )

    create_task(title, description, status, session['user_id'])
    flash("Task added successfully!", "success")
    return redirect(url_for("index_route"))


@app.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task_route(task_id):
    task = get_task(task_id)
    if not task:
        flash("Task does not exist!", "danger")
        return redirect(url_for("index_route"))

    if session["role"] != "admin" and task["user_id"] != session["user_id"]:
        flash("You do not have permission to edit this task!", "danger")
        return redirect(url_for("index_route"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        status = request.form.get("status")
        update_task(task_id, title, description, status)
        flash("Task updated!", "success")
        return redirect(url_for("index_route"))

    return render_template("edit_task.html", task=task)


@app.route("/delete_task/<int:task_id>")
@login_required
@role_required("admin")
def delete_task_route(task_id):
    task = get_task(task_id)
    if not task:
        flash("Task does not exist!", "danger")
    else:
        delete_task(task_id)
        flash("Task deleted!", "success")
    return redirect(url_for("index_route"))


# -----------------------------
# Routes: Admin User Management
# -----------------------------
# from werkzeug.security import generate_password_hash


@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
@role_required("admin")
def admin_users_route():
    edit_user = None
    username_value = ""
    role_value = "user"

    # Kiểm tra chế độ edit
    edit_id = request.args.get("edit")
    if edit_id:
        edit_user = get_user_by_id(edit_id)
        if edit_user:
            username_value = edit_user["username"]
            role_value = edit_user["role"]

    if request.method == "POST":
        user_id = request.form.get("user_id")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "user")

        # Giữ input
        username_value = username
        role_value = role

        # --- Validation chung ---
        if not username:
            flash("Username cannot be empty!", "warning")
            return render_template("admin_users.html",
                                   users=get_all_users(),
                                   edit_user=edit_user,
                                   username_value=username_value,
                                   role_value=role_value)

        # --- Thêm user mới ---
        if not user_id:
            if not password:
                flash("Password cannot be empty when creating a user!", "warning")
                return render_template("admin_users.html",
                                       users=get_all_users(),
                                       edit_user=None,
                                       username_value=username_value,
                                       role_value=role_value)
            try:
                hashed_password = generate_password_hash(password)
                create_user(username, hashed_password, role)
                flash("User created successfully!", "success")
                return redirect(url_for("admin_users_route"))
            except Exception as e:
                if hasattr(e, 'pgcode') and e.pgcode == '23505':
                    flash(f"Username '{username}' already exists!", "warning")
                    return render_template("admin_users.html",
                                           users=get_all_users(),
                                           edit_user=None,
                                           username_value=username_value,
                                           role_value=role_value)
                flash("Database error occurred!", "danger")
                return redirect(url_for("admin_users_route"))

        # --- Cập nhật user ---
        user_db = get_user_by_id(user_id)
        if not user_db:
            flash("User not found!", "danger")
            return redirect(url_for("admin_users_route"))

        if user_db["role"] == "admin":
            flash("You cannot edit Admin!", "warning")
            return redirect(url_for("admin_users_route"))

        try:
            hashed_password = generate_password_hash(password) if password else None
            update_user(user_id, username=username, password=hashed_password, role=role)
            flash("User updated successfully!", "success")
        except Exception as e:
            if hasattr(e, 'pgcode') and e.pgcode == '23505':
                flash(f"Username '{username}' already exists!", "warning")
                return render_template("admin_users.html",
                                       users=get_all_users(),
                                       edit_user=edit_user,
                                       username_value=username_value,
                                       role_value=role_value)
            flash("Database error occurred!", "danger")

        return redirect(url_for("admin_users_route"))

    # Load danh sách users
    return render_template("admin_users.html",
                           users=get_all_users(),
                           edit_user=edit_user,
                           username_value=username_value,
                           role_value=role_value)


@app.route("/admin/delete_user/<int:user_id>")
@login_required
@role_required("admin")
def admin_delete_user_route(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash("User does not exist!", "danger")
        return redirect(url_for("admin_users_route"))

    if user["role"] == "admin":
        flash("Admins cannot be deleted!", "warning")
        return redirect(url_for("admin_users_route"))

    tasks = get_tasks_by_user(user_id)
    if tasks:
        flash("This user has tasks. Please confirm deletion.", "warning")
        # Có thể thêm modal confirm ở frontend
        return redirect(url_for("admin_users_route"))

    delete_user(user_id)
    flash("User deleted!", "success")
    return redirect(url_for("admin_users_route"))

#Thông báo lỗi
@app.errorhandler(404)
def page_not_found(e):
    return render_template(
        "error.html",
        error_code=404,
        error_title="Not Found",
        error_message="The requested URL was not found on the server."
    ), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template(
        "error.html",
        error_code=403,
        error_title="Access Denied",
        error_message="You do not have permission to access this page."
    ), 403

@app.errorhandler(500)
def internal_error(e):
    return render_template(
        "error.html",
        error_code=500,
        error_title="Internal Server Error",
        error_message="Something went wrong on the server."
    ), 500

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)
