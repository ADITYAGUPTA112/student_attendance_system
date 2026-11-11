"""Tests verifying Phase 1 Admin Obsidian Black Mirror views and telemetry isolation."""

from db import get_db


def test_admin_dashboard_obsidian_telemetry_and_role_isolation(client):
    """Admin receives Obsidian telemetry dashboard; Student sees Student Portal isolated from Admin links."""
    client.post("/login", data={"username": "admin", "password": "admin123"})
    admin_resp = client.get("/dashboard")
    assert admin_resp.status_code == 200
    assert b"Administrator Overview" in admin_resp.data
    assert b"obsidian-black-mirror-overrides" in admin_resp.data
    assert b"Daily Turnout Velocity" in admin_resp.data
    assert b"Course Attendance Index" in admin_resp.data
    assert b"Live Operations Ledger" in admin_resp.data
    assert b"CS101" in admin_resp.data
    assert b"Administrator" in admin_resp.data

    # Student sees Obsidian Student Portal without Admin role/links or peer data
    client.get("/logout")
    client.post("/login", data={"username": "alice", "password": "student123"})
    student_resp = client.get("/student/dashboard")
    assert student_resp.status_code == 200
    assert b"My Attendance Dashboard" in student_resp.data
    assert b"obsidian-black-mirror-overrides" in student_resp.data
    assert b"Administrator" not in student_resp.data
    assert b'href="/audit"' not in student_resp.data
    assert b'href="/students"' not in student_resp.data


def test_admin_dashboard_handles_empty_attendance_gracefully(client, app):
    """Verify Admin dashboard renders clean empty states when no attendance or courses exist."""
    with app.app_context():
        database = get_db()
        database.execute("DELETE FROM attendance")
        database.execute("DELETE FROM enrollments")
        database.commit()

    client.post("/login", data={"username": "admin", "password": "admin123"})
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert b"No attendance sessions recorded yet" in resp.data
    assert b"Administrator Overview" in resp.data


def test_admin_only_pages_render_obsidian_shell_and_dialogs(client):
    """Verify Students, Audit, and Backup render Obsidian shell, responsive tables, and native dialogs."""
    client.post("/login", data={"username": "admin", "password": "admin123"})

    students_resp = client.get("/students")
    assert students_resp.status_code == 200
    assert b"obsidian-black-mirror-overrides" in students_resp.data
    assert b'id="addStudentModal"' in students_resp.data
    assert b'id="mobile-nav-drawer"' in students_resp.data

    audit_resp = client.get("/audit")
    assert audit_resp.status_code == 200
    assert b"obsidian-black-mirror-overrides" in audit_resp.data
    assert b"System Audit &amp; Traceability Log" in audit_resp.data
    assert b"MARK_ATTENDANCE" in audit_resp.data

    backup_resp = client.get("/backup")
    assert backup_resp.status_code == 200
    assert b"obsidian-black-mirror-overrides" in backup_resp.data
    assert b"Active Storage Status" in backup_resp.data
    assert b'id="confirmRestoreModal"' in backup_resp.data



def _sign_in(client, username, password):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def test_admin_courses_obsidian_and_rbac_controls(client):
    """Admin sees Obsidian Course Catalogue with full CRUD native dialogs."""
    _sign_in(client, "admin", "admin123")

    res = client.get("/courses")
    assert res.status_code == 200
    assert b"OBSIDIAN DARK MIRROR THEME" in res.data
    assert b"Course Catalogue" in res.data
    assert b'id="addCourseModal"' in res.data
    assert b'id="confirmUnenrollModal"' in res.data
    assert b'id="enrollModal1"' in res.data
    assert b"CS101" in res.data

    # Create a new course via POST and verify rendering
    create_res = client.post(
        "/courses",
        data={"code": "CS499", "name": "Cloud Governance Lab"},
        follow_redirects=True,
    )
    assert create_res.status_code == 200
    assert b"CS499" in create_res.data
    assert b"Cloud Governance Lab" in create_res.data

    # Student role cannot access /courses or create courses (forbidden)
    client.get("/logout", follow_redirects=True)
    _sign_in(client, "alice", "student123")
    stu_res = client.get("/courses")
    assert stu_res.status_code == 403


def test_admin_attendance_obsidian_workflow(client):
    """Admin sees Obsidian Attendance Entry with dual views & live tallies; Student stays forbidden."""
    _sign_in(client, "admin", "admin123")

    # Seeded CS101 session on 2026-10-27 exists -> Previously Recorded
    res = client.get("/attendance?course_id=1&date=2026-10-27")
    assert res.status_code == 200
    assert b"OBSIDIAN DARK MIRROR THEME" in res.data
    assert b"Class Attendance Entry" in res.data
    assert b"Previously Recorded" in res.data
    assert b'id="attendanceForm"' in res.data
    assert b'id="livePresentCount"' in res.data
    assert b'id="rosterGridView"' in res.data
    assert b'id="floatingModifiedBadge"' in res.data

    # New date session for CS101 + POST attendance save
    new_day = client.get("/attendance?course_id=1&date=2026-11-11")
    assert new_day.status_code == 200
    assert b"New Session Entry" in new_day.data

    post_res = client.post(
        "/attendance",
        data={
            "course_id": "1",
            "date": "2026-11-11",
            "status_1": "Present",
            "status_2": "Absent",
            "status_3": "Present",
            "status_4": "Present",
        },
        follow_redirects=True,
    )
    assert post_res.status_code == 200
    assert b"Previously Recorded" in post_res.data

    # Empty roster edge case (CS301 has no enrollments in seed)
    empty_res = client.get("/attendance?course_id=3&date=2026-11-11")
    assert empty_res.status_code == 200
    assert b"No Enrolled Students Found" in empty_res.data

    # Student remains forbidden from attendance entry
    client.get("/logout", follow_redirects=True)
    _sign_in(client, "alice", "student123")
    stu_res = client.get("/attendance?course_id=1&date=2026-10-27")
    assert stu_res.status_code == 403


def test_admin_analytics_obsidian_and_student_isolated(client):
    """Admin Analytics renders Obsidian UI, charts, MapReduce tables & empty-filter safety; Student stays untouched."""
    _sign_in(client, "admin", "admin123")

    res = client.get("/analytics")
    assert res.status_code == 200
    assert b"OBSIDIAN DARK MIRROR THEME" in res.data
    assert b"Attendance Analytics" in res.data
    assert b'id="courseFilter"' in res.data
    assert b'id="courseBarChart"' in res.data
    assert b'id="timelineLineChart"' in res.data
    assert b"MapReduce Engine" in res.data
    assert b"Course-Wise Totals (MapReduce)" in res.data
    assert b"Daily Totals (MapReduce)" in res.data
    assert b"/api/analytics/mapreduce" in res.data
    assert b"themeChanged" in res.data

    # Filter on empty course (CS301 = id 3) to verify safe telemetry defaults
    empty_res = client.get("/analytics?course_id=3")
    assert empty_res.status_code == 200
    assert b"Attendance Analytics" in empty_res.data

    # Student sees Obsidian Analytics with Export CSV & peer tables isolated
    client.get("/logout", follow_redirects=True)
    _sign_in(client, "alice", "student123")
    stu_res = client.get("/analytics")
    assert stu_res.status_code == 200
    assert b"OBSIDIAN DARK MIRROR THEME" in stu_res.data
    assert b"/export/csv" not in stu_res.data
    assert b"Privacy-Isolated Course Telemetry" in stu_res.data


def test_admin_teachers_directory_crud_password_reset_and_rbac(client, app):
    """Admin can manage teachers, create custom IDs/passwords, and reset passwords with strict RBAC."""
    _sign_in(client, "admin", "admin123")

    # Teachers Directory loads for Admin and includes sidebar link + native modals
    list_res = client.get("/teachers")
    assert list_res.status_code == 200
    assert b"Teachers Directory" in list_res.data
    assert b"prof_smith" in list_res.data
    assert b'href="/teachers"' in list_res.data
    assert b'id="addTeacherModal"' in list_res.data
    assert b'id="resetTeacherPwdModal"' in list_res.data

    # Reject mismatched passwords or duplicate username
    bad_pwd = client.post(
        "/teachers",
        data={
            "username": "prof_bad",
            "password": "Pass1234",
            "confirm_password": "Mismatch123",
        },
        follow_redirects=True,
    )
    assert bad_pwd.status_code == 200

    dup_res = client.post(
        "/teachers",
        data={
            "username": "PROF_SMITH",
            "password": "Pass1234",
            "confirm_password": "Pass1234",
        },
        follow_redirects=True,
    )
    assert dup_res.status_code == 200

    # Create valid teacher with custom Login ID and Password
    create_res = client.post(
        "/teachers",
        data={
            "username": "prof_jones",
            "password": "TeachPass99",
            "confirm_password": "TeachPass99",
        },
        follow_redirects=True,
    )
    assert create_res.status_code == 200
    assert b"prof_jones" in create_res.data
    assert b"TeachPass99" not in create_res.data

    with app.app_context():
        database = get_db()
        bad_row = database.execute(
            "SELECT id FROM users WHERE username = 'prof_bad'"
        ).fetchone()
        assert bad_row is None
        jones_row = database.execute(
            "SELECT id, username, role, student_id FROM users WHERE username = 'prof_jones'"
        ).fetchone()
        assert jones_row is not None
        assert jones_row["role"] == "faculty"
        assert jones_row["student_id"] is None
        jones_id = jones_row["id"]

        audit_rows = database.execute("SELECT action, detail FROM audit_logs").fetchall()
        assert any(r["action"] == "CREATE_FACULTY" for r in audit_rows)
        assert all("TeachPass99" not in (r["detail"] or "") for r in audit_rows)

    # Search filter works on /teachers
    search_res = client.get("/teachers?q=jones")
    assert search_res.status_code == 200
    assert b"@prof_jones" in search_res.data
    assert b"@prof_smith" not in search_res.data

    # New teacher logs into Faculty Portal and is blocked from Admin Teacher routes
    client.get("/logout", follow_redirects=True)
    fac_login = _sign_in(client, "prof_jones", "TeachPass99")
    assert fac_login.status_code == 200
    assert b"Faculty Portal" in fac_login.data
    assert b'href="/teachers"' not in fac_login.data
    assert client.get("/teachers").status_code == 403
    assert (
        client.post(
            "/teachers",
            data={
                "username": "rogue_teacher",
                "password": "Pass1234",
                "confirm_password": "Pass1234",
            },
        ).status_code
        == 403
    )
    assert (
        client.post(
            f"/teachers/{jones_id}/password",
            data={"password": "Hack1234", "confirm_password": "Hack1234"},
        ).status_code
        == 403
    )

    # Admin resets teacher password; old password fails, new password succeeds
    client.get("/logout", follow_redirects=True)
    _sign_in(client, "admin", "admin123")
    reset_res = client.post(
        f"/teachers/{jones_id}/password",
        data={"password": "NewTeach77!", "confirm_password": "NewTeach77!"},
        follow_redirects=True,
    )
    assert reset_res.status_code == 200
    assert b"NewTeach77!" not in reset_res.data

    with app.app_context():
        database = get_db()
        audit_rows = database.execute("SELECT action, detail FROM audit_logs").fetchall()
        assert any(r["action"] == "RESET_FACULTY_PASSWORD" for r in audit_rows)
        assert all("NewTeach77!" not in (r["detail"] or "") for r in audit_rows)

    client.get("/logout", follow_redirects=True)
    old_login = _sign_in(client, "prof_jones", "TeachPass99")
    assert b"Invalid" in old_login.data or b"Sign In" in old_login.data

    new_login = _sign_in(client, "prof_jones", "NewTeach77!")
    assert new_login.status_code == 200
    assert b"Faculty Portal" in new_login.data

    # Student also cannot access Admin Teacher routes or see nav link
    client.get("/logout", follow_redirects=True)
    stu_dash = _sign_in(client, "alice", "student123")
    assert stu_dash.status_code == 200
    assert b'href="/teachers"' not in stu_dash.data
    assert client.get("/teachers").status_code == 403
    assert (
        client.post(
            f"/teachers/{jones_id}/password",
            data={"password": "Hack1234", "confirm_password": "Hack1234"},
        ).status_code
        == 403
    )


def test_admin_students_custom_credentials_create_and_update(client, app):
    """Admin can set custom login IDs/passwords when adding students and update/provision them later."""
    _sign_in(client, "admin", "admin123")

    # Duplicate login username must fail BEFORE creating an orphan student record
    dup_login_res = client.post(
        "/students",
        data={
            "roll_no": "CS2026-99",
            "name": "Conflict User",
            "email": "conflict@edu.test",
            "create_login": "1",
            "login_username": "ALICE",
            "login_password": "Secret99",
        },
        follow_redirects=True,
    )
    assert dup_login_res.status_code == 200

    with app.app_context():
        database = get_db()
        orphan = database.execute(
            "SELECT id FROM students WHERE roll_no = 'CS2026-99'"
        ).fetchone()
        assert orphan is None

    # Create student with explicit custom Login ID & Password
    add_res = client.post(
        "/students",
        data={
            "roll_no": "CS2026-88",
            "name": "Maya Patel",
            "email": "maya@edu.test",
            "create_login": "1",
            "login_username": "maya_patel",
            "login_password": "MayaPass88",
        },
        follow_redirects=True,
    )
    assert add_res.status_code == 200
    assert b"Maya Patel" in add_res.data
    assert b"@maya_patel" in add_res.data
    assert b"MayaPass88" not in add_res.data
    assert b'id="studentCredsModal"' in add_res.data

    with app.app_context():
        database = get_db()
        maya_stu = database.execute(
            "SELECT id FROM students WHERE roll_no = 'CS2026-88'"
        ).fetchone()
        assert maya_stu is not None
        maya_id = maya_stu["id"]
        maya_user = database.execute(
            "SELECT username, role, student_id FROM users WHERE student_id = ?",
            (maya_id,),
        ).fetchone()
        assert maya_user is not None
        assert maya_user["username"] == "maya_patel"
        assert maya_user["role"] == "student"

        audit_rows = database.execute("SELECT action, detail FROM audit_logs").fetchall()
        assert all("MayaPass88" not in (r["detail"] or "") for r in audit_rows)

    # New student signs in with custom ID/password and stays blocked from /credentials
    client.get("/logout", follow_redirects=True)
    maya_login = _sign_in(client, "maya_patel", "MayaPass88")
    assert maya_login.status_code == 200
    assert b"My Attendance Dashboard" in maya_login.data
    assert b"CS2026-88" in maya_login.data
    assert (
        client.post(
            f"/students/{maya_id}/credentials",
            data={"login_username": "hijack", "login_password": "Password1"},
        ).status_code
        == 403
    )

    # Admin updates Maya's login ID and password via /students/<id>/credentials
    client.get("/logout", follow_redirects=True)
    _sign_in(client, "admin", "admin123")
    upd_res = client.post(
        f"/students/{maya_id}/credentials",
        data={"login_username": "maya_2026", "login_password": "UpdatedPass99"},
        follow_redirects=True,
    )
    assert upd_res.status_code == 200
    assert b"@maya_2026" in upd_res.data
    assert b"UpdatedPass99" not in upd_res.data

    with app.app_context():
        database = get_db()
        audit_rows = database.execute("SELECT detail FROM audit_logs").fetchall()
        assert all("UpdatedPass99" not in (r["detail"] or "") for r in audit_rows)

    # Admin creates a student without initial login, then provisions credentials later
    client.post(
        "/students",
        data={
            "roll_no": "CS2026-77",
            "name": "Noah Kim",
            "email": "noah@edu.test",
            "create_login": "",
        },
        follow_redirects=True,
    )
    with app.app_context():
        noah_stu = (
            get_db()
            .execute("SELECT id FROM students WHERE roll_no = 'CS2026-77'")
            .fetchone()
        )
        assert noah_stu is not None
        noah_id = noah_stu["id"]

    prov_res = client.post(
        f"/students/{noah_id}/credentials",
        data={"login_username": "noah_k", "login_password": "NoahPass12"},
        follow_redirects=True,
    )
    assert prov_res.status_code == 200
    assert b"@noah_k" in prov_res.data

    # Verify updated student & newly provisioned student can sign in
    client.get("/logout", follow_redirects=True)
    old_maya = _sign_in(client, "maya_patel", "MayaPass88")
    assert b"Sign In" in old_maya.data or b"Invalid" in old_maya.data

    new_maya = _sign_in(client, "maya_2026", "UpdatedPass99")
    assert new_maya.status_code == 200
    assert b"My Attendance Dashboard" in new_maya.data
    assert b"CS2026-88" in new_maya.data

    client.get("/logout", follow_redirects=True)
    noah_login = _sign_in(client, "noah_k", "NoahPass12")
    assert noah_login.status_code == 200
    assert b"My Attendance Dashboard" in noah_login.data
    assert b"CS2026-77" in noah_login.data
