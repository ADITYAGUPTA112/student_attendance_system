"""Database initialization, connection lifecycle, and synthetic seeding for CloudAttend."""

import os
import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash


def get_db():
    """Retrieve or initialize a database connection with foreign key enforcement."""
    if "db" not in g:
        db_path = current_app.config["DATABASE"]
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

        conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        # CRITICAL: Always enforce foreign keys
        conn.execute("PRAGMA foreign_keys = ON;")
        g.db = conn
    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Initialize database tables according to schema.sql."""
    db = get_db()
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, mode="r", encoding="utf-8") as f:
        db.executescript(f.read())


def seed_db():
    """Seed database with deterministic, synthetic demo records."""
    db = get_db()

    # 1. Seed Courses
    courses = [
        ("CS101", "Introduction to Computer Science"),
        ("CS201", "Data Structures & Algorithms"),
        ("CS301", "Database Management Systems"),
    ]
    for code, name in courses:
        db.execute(
            "INSERT OR IGNORE INTO courses (code, name) VALUES (?, ?)",
            (code, name),
        )

    # 2. Seed Students
    students_data = [
        ("CS-001", "Alice Adams", "alice.adams@example.edu"),
        ("CS-002", "Bob Baker", "bob.baker@example.edu"),
        ("CS-003", "Charlie Clark", "charlie.clark@example.edu"),
        ("CS-004", "Diana Davies", "diana.davies@example.edu"),
    ]
    student_ids = {}
    for roll_no, name, email in students_data:
        db.execute(
            "INSERT OR IGNORE INTO students (roll_no, name, email) VALUES (?, ?, ?)",
            (roll_no, name, email),
        )
        cur = db.execute("SELECT id FROM students WHERE roll_no = ?", (roll_no,))
        row = cur.fetchone()
        if row:
            student_ids[roll_no] = row["id"]

    # 3. Seed Users
    # Admin User
    admin_hash = generate_password_hash("admin123")
    db.execute(
        "INSERT OR IGNORE INTO users (username, password_hash, role, student_id) VALUES (?, ?, ?, ?)",
        ("admin", admin_hash, "admin", None),
    )

    # Faculty Users
    faculty_hash = generate_password_hash("faculty123")
    db.execute(
        "INSERT OR IGNORE INTO users (username, password_hash, role, student_id) VALUES (?, ?, ?, ?)",
        ("prof_smith", faculty_hash, "faculty", None),
    )
    db.execute(
        "INSERT OR IGNORE INTO users (username, password_hash, role, student_id) VALUES (?, ?, ?, ?)",
        ("prof_johnson", faculty_hash, "faculty", None),
    )

    # Student Users
    student_hash = generate_password_hash("student123")
    student_users = [
        ("alice", "CS-001"),
        ("bob", "CS-002"),
        ("charlie", "CS-003"),
        ("diana", "CS-004"),
    ]
    for uname, roll_no in student_users:
        s_id = student_ids.get(roll_no)
        db.execute(
            "INSERT OR IGNORE INTO users (username, password_hash, role, student_id) VALUES (?, ?, ?, ?)",
            (uname, student_hash, "student", s_id),
        )

    # 4. Seed Enrollments (Link students to courses)
    course_cur = db.execute("SELECT id, code FROM courses")
    course_map = {row["code"]: row["id"] for row in course_cur.fetchall()}

    cs101_id = course_map.get("CS101")
    cs201_id = course_map.get("CS201")

    if cs101_id and cs201_id:
        for s_id in student_ids.values():
            # Enroll all students in CS101
            db.execute(
                "INSERT OR IGNORE INTO enrollments (student_id, course_id) VALUES (?, ?)",
                (s_id, cs101_id),
            )
            # Enroll first 3 students in CS201
            if s_id != student_ids.get("CS-004"):
                db.execute(
                    "INSERT OR IGNORE INTO enrollments (student_id, course_id) VALUES (?, ?)",
                    (s_id, cs201_id),
                )

    # 5. Seed Attendance (Historical sample data for demo & testing)
    faculty_cur = db.execute("SELECT id FROM users WHERE username = 'prof_smith'")
    faculty_row = faculty_cur.fetchone()
    faculty_id = faculty_row["id"] if faculty_row else 1

    sample_sessions = [
        # (date, course_code, {roll_no: status})
        ("2026-10-27", "CS101", {"CS-001": "Present", "CS-002": "Present", "CS-003": "Absent", "CS-004": "Present"}),
        ("2026-10-28", "CS101", {"CS-001": "Present", "CS-002": "Absent", "CS-003": "Present", "CS-004": "Present"}),
        ("2026-10-29", "CS101", {"CS-001": "Present", "CS-002": "Present", "CS-003": "Present", "CS-004": "Absent"}),
        ("2026-10-28", "CS201", {"CS-001": "Present", "CS-002": "Present", "CS-003": "Absent"}),
        ("2026-10-29", "CS201", {"CS-001": "Absent", "CS-002": "Present", "CS-003": "Present"}),
    ]

    for att_date, c_code, records in sample_sessions:
        c_id = course_map.get(c_code)
        if c_id:
            for roll_no, status in records.items():
                s_id = student_ids.get(roll_no)
                if s_id:
                    db.execute(
                        """
                        INSERT OR IGNORE INTO attendance 
                        (student_id, course_id, attendance_date, status, marked_by)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (s_id, c_id, att_date, status, faculty_id),
                    )

    # 6. Seed Audit Log Entry
    db.execute(
        """
        INSERT INTO audit_logs (user_id, action, detail)
        VALUES (?, ?, ?)
        """,
        (1, "SYSTEM_SEED", "Database successfully initialized with synthetic demo data."),
    )

    db.commit()


@click.command("init-db")
@click.option("--seed/--no-seed", default=True, help="Seed database with synthetic demo data.")
@with_appcontext
def init_db_command(seed):
    """Clear existing data and create new database tables."""
    init_db()
    click.echo("Initialized the database tables.")
    if seed:
        seed_db()
        click.echo("Seeded synthetic demo data.")


def init_app(app):
    """Register database functions with the Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
