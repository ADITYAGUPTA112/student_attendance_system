"""Tests verifying Phase 3 Student Obsidian Black Mirror Portal and CA-10 isolation."""

from db import get_db


def _sign_in(client, username, password):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def test_student_dashboard_obsidian_ui_and_widgets(client):
    """Student Portal renders Obsidian UI, ID credential card, simulator, and heatmap."""
    _sign_in(client, "alice", "student123")

    res = client.get("/student/dashboard")
    assert res.status_code == 200
    assert b"OBSIDIAN DARK MIRROR THEME" in res.data
    assert b"My Attendance Dashboard" in res.data
    assert b"Student Portal" in res.data
    assert b"STUDENT // LIVE V2.4" in res.data
    assert b"CS-001" in res.data
    assert b'id="studentHoloCard"' in res.data
    assert b'id="studentRadialIndicator"' in res.data
    assert b'stroke-dasharray="314.159"' in res.data
    assert b'id="calcCourseScope"' in res.data
    assert b'id="simulationRange"' in res.data
    assert b'id="simulationMode"' in res.data
    assert b'id="sliderValueLabel"' in res.data
    assert b'id="projectedPctDisplay"' in res.data
    assert b'id="safetyVerdictBadge"' in res.data
    assert b'id="safetyAdviceAlert"' in res.data
    assert b'id="safetyAdviceText"' in res.data
    assert b'id="studentHeatmapGrid"' in res.data
    assert b'id="studentHistoryData"' in res.data
    assert b"CS101" in res.data


def test_student_portal_strict_rbac_and_privacy_isolation(client):
    """Student shell exposes zero Admin/Faculty links and isolates peer roll numbers."""
    _sign_in(client, "alice", "student123")

    dash = client.get("/student/dashboard")
    assert dash.status_code == 200
    assert b"CS-001" in dash.data
    assert b"CS-002" not in dash.data
    assert b'href="/students"' not in dash.data
    assert b'href="/courses"' not in dash.data
    assert b'href="/attendance"' not in dash.data
    assert b'href="/audit"' not in dash.data
    assert b'href="/backup"' not in dash.data
    assert b"/export/csv" not in dash.data
    assert b"Administrator" not in dash.data
    assert b"Faculty Member" not in dash.data

    # Analytics hides peer breakdown tables & CSV export from students
    ana = client.get("/analytics")
    assert ana.status_code == 200
    assert b"OBSIDIAN DARK MIRROR THEME" in ana.data
    assert b"Privacy-Isolated Course Telemetry" in ana.data
    assert b"/export/csv" not in ana.data
    assert b"At-Risk Students" not in ana.data
    assert b"Learner Breakdown" not in ana.data
    assert b"CS-002" not in ana.data


def test_student_dashboard_handles_empty_and_unlinked_profile(client, app):
    """Student dashboard handles empty attendance and unlinked student profile cleanly."""
    with app.app_context():
        database = get_db()
        database.execute("DELETE FROM attendance")
        database.execute("DELETE FROM enrollments")
        database.commit()

    _sign_in(client, "alice", "student123")
    empty_res = client.get("/student/dashboard")
    assert empty_res.status_code == 200
    assert b"My Attendance Dashboard" in empty_res.data
    assert b"Pending Sessions" in empty_res.data
    assert b"No course enrollments or attendance sessions found yet." in empty_res.data
    assert b"No session logs recorded yet." in empty_res.data

    with app.app_context():
        database = get_db()
        database.execute("UPDATE users SET student_id = NULL WHERE username = 'alice'")
        database.commit()

    unlinked_res = client.get("/student/dashboard")
    assert unlinked_res.status_code == 200
    assert b"Student profile record not found." in unlinked_res.data
    assert b"N/A" in unlinked_res.data
    assert b"Pending Sessions" in unlinked_res.data


def test_student_dashboard_formats_percentages_to_two_decimals(client, app):
    """Repeating decimal attendance ratios display cleanly with at most 2 digits after the decimal point."""
    with app.app_context():
        database = get_db()
        stu = database.execute("SELECT id FROM students WHERE roll_no = 'CS-001'").fetchone()
        admin = database.execute("SELECT id FROM users WHERE username = 'admin'").fetchone()
        database.execute("DELETE FROM attendance WHERE student_id = ?", (stu["id"],))
        # Course 1 (CS101): 6 Present out of 6, Course 2 (CS201): 2 Present, 1 Absent (66.67%) -> overall 8/9 (88.89%)
        database.execute("INSERT OR IGNORE INTO enrollments (student_id, course_id) VALUES (?, 1)", (stu["id"],))
        database.execute("INSERT OR IGNORE INTO enrollments (student_id, course_id) VALUES (?, 2)", (stu["id"],))
        for i in range(1, 7):
            database.execute(
                "INSERT INTO attendance (student_id, course_id, attendance_date, status, marked_by) VALUES (?, 1, ?, 'Present', ?)",
                (stu["id"], f"2026-10-0{i}", admin["id"]),
            )
        for day, status in [("2026-10-10", "Present"), ("2026-10-11", "Present"), ("2026-10-12", "Absent")]:
            database.execute(
                "INSERT INTO attendance (student_id, course_id, attendance_date, status, marked_by) VALUES (?, 2, ?, ?, ?)",
                (stu["id"], day, status, admin["id"]),
            )
        database.commit()

    _sign_in(client, "alice", "student123")
    res = client.get("/student/dashboard")
    assert res.status_code == 200
    assert b"88.89%" in res.data
    assert b"66.67%" in res.data
    assert b"88.888" not in res.data
    assert b"66.666" not in res.data
