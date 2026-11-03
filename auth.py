"""Authentication, session lifecycle, and role-based authorization helpers (CA-03, CA-04)."""

from functools import wraps
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    abort,
)
from werkzeug.security import check_password_hash
from db import get_db

bp = Blueprint("auth", __name__)


def log_audit(user_id, action, detail):
    """Record an audit trail event without sensitive credentials."""
    try:
        db = get_db()
        db.execute(
            "INSERT INTO audit_logs (user_id, action, detail) VALUES (?, ?, ?)",
            (user_id, action, detail),
        )
        db.commit()
    except Exception:
        # Avoid crashing primary user flows on audit logging issues
        pass


@bp.before_app_request
def load_logged_in_user():
    """Load the current authenticated user into flask.g for template and route access."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute(
            "SELECT id, username, role, student_id FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()


def login_required(view):
    """Decorator to require authentication for protected routes."""
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login", next=request.path))
        return view(**kwargs)

    return wrapped_view


def role_required(*allowed_roles):
    """Decorator to enforce role-based access control (RBAC) at the server level."""
    def decorator(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                return redirect(url_for("auth.login", next=request.path))

            user_role = g.user["role"]
            if user_role not in allowed_roles:
                log_audit(
                    g.user["id"],
                    "ACCESS_DENIED",
                    f"Forbidden access to {request.path} for role '{user_role}'.",
                )
                abort(403)

            return view(**kwargs)

        return wrapped_view

    return decorator


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Render login form and authenticate user sessions."""
    # Redirect if already signed in
    if g.user is not None:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        error = None

        if not username or not password:
            error = "Both username and password are required."
        else:
            db = get_db()
            user = db.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

            if user is None or not check_password_hash(user["password_hash"], password):
                error = "Invalid username or password."
                # Log failed attempt without password
                log_audit(None, "LOGIN_FAILED", f"Failed login attempt for username '{username}'.")
            else:
                # Mitigate session fixation: clear old session state
                session.clear()
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["role"] = user["role"]
                session["student_id"] = user["student_id"]

                log_audit(user["id"], "LOGIN_SUCCESS", f"User '{username}' authenticated successfully.")

                next_page = request.args.get("next")
                if next_page and next_page.startswith("/"):
                    return redirect(next_page)
                return redirect(url_for("index"))

        flash(error, "danger")

    return render_template("login.html")


@bp.route("/logout", methods=["GET"])
def logout():
    """Clear session and log out the user."""
    user_id = session.get("user_id")
    username = session.get("username")
    if user_id:
        log_audit(user_id, "LOGOUT", f"User '{username}' logged out.")

    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("auth.login"))

