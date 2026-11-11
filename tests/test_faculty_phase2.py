"""Tests verifying Phase 2 Faculty Obsidian Black Mirror portal and Student UI isolation."""

from db import get_db


def _sign_in(client, username, password):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def test_faculty_dashboard_obsidian_and_student_isolated(client):
    """Faculty sees Obsidian workspace with teaching telemetry; no Admin nav links; Student untouched."""
    _sign_in(client, "prof_smith", "faculty123")

    res = client.get("/dashboard")
    assert res.status_code == 200
    assert b"OBSIDIAN DARK MIRROR THEME" in res.data
    assert b"Faculty Portal" in res.data
    assert b"Faculty Member" in res.data
    assert b"My Submitted Marks" in res.data
    assert b"Course Curriculum &amp; Turnout" in res.data
    assert b'class="obsidian-progress' in res.data
    assert b'id="liveFacultyClock"' in res.data
    assert b"CS101" in res.data

    # Admin-only endpoints and role label must NOT appear in Faculty shell
    assert b'href="/students"' not in res.data
    assert b'href="/audit"' not in res.data
    assert b'href="/backup"' not in res.data
    assert b"Administrator" not in res.data

    # Student Portal runs Obsidian Student view without Faculty/Admin controls
    client.get("/logout", follow_redirects=True)
    _sign_in(client, "alice", "student123")
    stu_dash = client.get("/student/dashboard")
    assert stu_dash.status_code == 200
    assert b"My Attendance Dashboard" in stu_dash.data
    assert b"OBSIDIAN DARK MIRROR THEME" in stu_dash.data
    assert b'href="/attendance"' not in stu_dash.data
    assert b'href="/courses"' not in stu_dash.data


def test_faculty_courses_obsidian_readonly_rosters(client):
    """Faculty views Obsidian Course Catalogue with read-only Roster dialogs and no Admin CRUD forms."""
    _sign_in(client, "prof_smith", "faculty123")

    res = client.get("/courses")
    assert res.status_code == 200
    assert b"OBSIDIAN DARK MIRROR THEME" in res.data
    assert b"Course Catalogue" in res.data
    assert b"View Roster" in res.data
    assert b"CS101" in res.data
    assert b'id="enrollModal1"' in res.data

    # Admin CRUD dialogs/buttons must be absent for Faculty
    assert b'id="addCourseModal"' not in res.data
    assert b'id="confirmUnenrollModal"' not in res.data
    assert b"Enroll Selected" not in res.data


def test_faculty_attendance_and_analytics_obsidian(client):
    """Faculty uses Obsidian Attendance Entry & Analytics while Student Analytics remains untouched."""
    _sign_in(client, "prof_smith", "faculty123")

    att_res = client.get("/attendance?course_id=1&date=2026-10-27")
    assert att_res.status_code == 200
    assert b"OBSIDIAN DARK MIRROR THEME" in att_res.data
    assert b"Class Attendance Entry" in att_res.data
    assert b"Previously Recorded" in att_res.data
    assert b'id="attendanceForm"' in att_res.data

    ana_res = client.get("/analytics")
    assert ana_res.status_code == 200
    assert b"OBSIDIAN DARK MIRROR THEME" in ana_res.data
    assert b"Attendance Analytics" in ana_res.data
    assert b'id="courseBarChart"' in ana_res.data
    assert b'id="timelineLineChart"' in ana_res.data
    assert b"MapReduce Engine" in ana_res.data
    assert b"/export/csv" in ana_res.data

    # Student Analytics runs Obsidian UI with peer PII & CSV export isolated
    client.get("/logout", follow_redirects=True)
    _sign_in(client, "alice", "student123")
    stu_ana = client.get("/analytics")
    assert stu_ana.status_code == 200
    assert b"OBSIDIAN DARK MIRROR THEME" in stu_ana.data
    assert b"/export/csv" not in stu_ana.data
    assert b"At-Risk Students" not in stu_ana.data


def test_faculty_dashboard_handles_empty_db_gracefully(client, app):
    """Faculty dashboard renders clean empty states when attendance logs are empty."""
    with app.app_context():
        database = get_db()
        database.execute("DELETE FROM attendance")
        database.execute("DELETE FROM enrollments")
        database.commit()

    _sign_in(client, "prof_smith", "faculty123")
    res = client.get("/dashboard")
    assert res.status_code == 200
    assert b"Faculty Portal" in res.data
    assert b"No recorded sessions yet" in res.data
