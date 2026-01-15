from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2 import IntegrityError
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
            except IntegrityError:
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
# Routes: Forgot/Reset Password
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
    role = session.get("role")
    user_id = session.get("user_id")
    username = session.get("username")

    if role == "admin":
        tasks = get_all_tasks_admin()
        users = get_all_users()
    else:
        tasks = get_tasks_by_user(user_id)
        users = []

    completed_count = sum(1 for t in tasks if t["status"] == "completed")
    pending_count = sum(1 for t in tasks if t["status"] == "pending")

    return render_template(
        "tasks.html",
        tasks=tasks,
        username=username,
        role=role,
        completed_count=completed_count,
        pending_count=pending_count,
        users=users
    )

# -----------------------------
# Routes: Tasks
# -----------------------------
@app.route('/add-task', methods=['POST'])
@login_required
def add_task_route():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    status = request.form.get("status", "pending")
    role = session.get("role")
    user_id = session.get("user_id")

    if not title or not description:
        flash("Please fill in Title and Description!", "warning")
        return redirect(url_for("index_route"))

    if role == 'admin':
        assigned_user_id = request.form.get("assigned_user_id") or user_id
        create_task(title, description, status, assigned_user_id, assigned_by_admin=True)
    else:
        create_task(title, description, status, user_id)

    flash("Task added successfully!", "success")
    return redirect(url_for("index_route"))

@app.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task_route(task_id):
    task = get_task(task_id)
    if not task:
        flash("Task does not exist!", "danger")
        return redirect(url_for("index_route"))

    role = session.get("role")
    user_id = session.get("user_id")

    if role != "admin" and task["user_id"] != user_id:
        flash("You do not have permission to edit this task!", "danger")
        return redirect(url_for("index_route"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        status = request.form.get("status", "pending")
        update_task(task_id, title, description, status)
        flash("Task updated!", "success")
        return redirect(url_for("index_route"))

    return render_template("edit_task.html", task=task)

@app.route("/delete_task/<int:task_id>")
@login_required
def delete_task_route(task_id):
    task = get_task(task_id)
    if not task:
        flash("Task does not exist!", "danger")
        return redirect(url_for("index_route"))

    user_id = session.get("user_id")
    role = session.get("role")
    if role != "admin" and task["user_id"] != user_id:
        flash("You do not have permission to delete this task!", "danger")
        return redirect(url_for("index_route"))

    delete_task(task_id)
    flash("Task deleted!", "success")
    return redirect(url_for("index_route"))

# -----------------------------
# Routes: Admin User Management
# -----------------------------
@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
@role_required("admin")
def admin_manager_route():
    edit_user = None
    username_value = ""
    role_value = "user"

    edit_id = request.args.get("edit")
    if edit_id:
        edit_user = get_user_by_id(int(edit_id))
        if edit_user:
            username_value = edit_user["username"]
            role_value = edit_user["role"]

    if request.method == "POST":
        user_id = request.form.get("user_id")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "user")

        username_value = username
        role_value = role

        if not username:
            flash("Username cannot be empty!", "warning")
            return redirect(url_for("admin_manager_route"))

        # Add new user
        if not user_id:
            if not password:
                flash("Password cannot be empty when creating a user!", "warning")
                return redirect(url_for("admin_manager_route"))
            try:
                hashed_password = generate_password_hash(password)
                create_user(username, hashed_password, role)
                flash("User created successfully!", "success")
                return redirect(url_for("admin_manager_route"))
            except IntegrityError:
                flash(f"Username '{username}' already exists!", "warning")
                return redirect(url_for("admin_manager_route"))

        # Update existing user
        user_db = get_user_by_id(user_id)
        if not user_db:
            flash("User not found!", "danger")
            return redirect(url_for("admin_manager_route"))

        if user_db["role"] == "admin":
            flash("You cannot edit Admin!", "warning")
            return redirect(url_for("admin_manager_route"))

        hashed_password = generate_password_hash(password) if password else None
        update_user(user_id, username=username, password=hashed_password, role=role)
        flash("User updated successfully!", "success")
        return redirect(url_for("admin_manager_route"))

    # GET
    users = get_all_users()
    user_tasks_map = {user['id']: get_tasks_by_user(user['id']) for user in users}
    confirm_user_id = request.args.get("confirm_user_id")
    confirm_user = get_user_by_id(int(confirm_user_id)) if confirm_user_id else None
    confirm_user_tasks = get_tasks_by_user(confirm_user["id"]) if confirm_user else []

    return render_template(
        "admin_manager.html",
        users=users,
        user_tasks_map=user_tasks_map,
        edit_user=edit_user,
        username_value=username_value,
        role_value=role_value,
        confirm_user=confirm_user,
        confirm_user_tasks=confirm_user_tasks
    )


@app.route("/admin/delete_user/<int:user_id>")
@login_required
@role_required("admin")
def admin_delete_user_route(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash("User does not exist!", "danger")
        return redirect(url_for("admin_manager_route"))

    # Lấy tất cả task của user
    tasks = get_tasks_by_user(user_id)
    for task in tasks:
        delete_task(task['id'])  # xóa từng task

    # Xóa user
    delete_user(user_id)
    flash(f"User {user['username']} and all their tasks were deleted successfully!", "success")
    return redirect(url_for("admin_manager_route"))


# -----------------------------
# Error Handlers
# -----------------------------
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
