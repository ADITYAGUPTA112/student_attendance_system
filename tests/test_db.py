"""Tests for database schema, foreign key enforcement, and seed data (CA-02)."""

import sqlite3
import pytest
from db import get_db


def test_tables_created(app):
    """Verify that all core tables exist in the database."""
    with app.app_context():
        database = get_db()
        cur = database.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        )
        tables = [row["name"] for row in cur.fetchall()]
        assert "users" in tables
        assert "students" in tables
        assert "courses" in tables
        assert "enrollments" in tables
        assert "attendance" in tables
        assert "audit_logs" in tables


def test_seed_users_and_roles(app):
    """Verify that synthetic demo users and roles are seeded correctly."""
    with app.app_context():
        database = get_db()
        # Admin
        admin = database.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()
        assert admin is not None
        assert admin["role"] == "admin"

        # Faculty
        faculty = database.execute("SELECT * FROM users WHERE username = 'prof_smith'").fetchone()
        assert faculty is not None
        assert faculty["role"] == "faculty"

        # Student with linked student record
        student_user = database.execute("SELECT * FROM users WHERE username = 'alice'").fetchone()
        assert student_user is not None
        assert student_user["role"] == "student"
        assert student_user["student_id"] is not None

        student_profile = database.execute(
            "SELECT * FROM students WHERE id = ?", (student_user["student_id"],)
        ).fetchone()
        assert student_profile is not None
        assert student_profile["roll_no"] == "CS-001"


def test_foreign_key_enforcement(app):
    """Verify that foreign keys are enforced by PRAGMA foreign_keys = ON."""
    with app.app_context():
        database = get_db()
        # Non-existent student ID 99999 should violate foreign key constraint on enrollment
        with pytest.raises(sqlite3.IntegrityError):
            database.execute(
                "INSERT INTO enrollments (student_id, course_id) VALUES (99999, 1)"
            )


def test_uniqueness_constraints(app):
    """Verify uniqueness constraints on roll_no and course code."""
    with app.app_context():
        database = get_db()
        # Duplicate student roll_no
        with pytest.raises(sqlite3.IntegrityError):
            database.execute(
                "INSERT INTO students (roll_no, name) VALUES ('CS-001', 'Duplicate Alice')"
            )

        # Duplicate course code
        with pytest.raises(sqlite3.IntegrityError):
            database.execute(
                "INSERT INTO courses (code, name) VALUES ('CS101', 'Duplicate CS101')"
            )


def test_init_db_command(runner):
    """Verify that the flask init-db CLI command runs successfully."""
    result = runner.invoke(args=["init-db", "--seed"])
    assert result.exit_code == 0
    assert "Initialized the database tables." in result.output
    assert "Seeded synthetic demo data." in result.output

