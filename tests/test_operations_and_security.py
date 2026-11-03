"""Tests for Operations, Security, Audit Logs, and Database Backup/Restore (CA-14, CA-15, CA-18)."""

import sqlite3
import tempfile


def test_audit_log_view_and_filtering(client):
    """Verify admin can view and search audit trail (CA-14)."""
    # Trigger an administrative action
    client.post("/login", data={"username": "admin", "password": "admin123"})
    client.post("/courses", data={"code": "AUDIT101", "name": "Audit Test Course"})

    # View audit log
    response = client.get("/audit")
    assert response.status_code == 200
    assert b"System Audit &amp; Traceability Log" in response.data or b"System Audit" in response.data
    assert b"CREATE_COURSE" in response.data

    # Test filtering
    filter_resp = client.get("/audit?q=AUDIT101")
    assert filter_resp.status_code == 200
    assert b"AUDIT101" in filter_resp.data


def test_audit_log_access_denied_for_non_admin(client):
    """Verify non-admin roles cannot access audit trail."""
    # Faculty
    client.post("/login", data={"username": "prof_smith", "password": "faculty123"})
    resp_faculty = client.get("/audit")
    assert resp_faculty.status_code == 403

    # Student
    client.get("/logout")
    client.post("/login", data={"username": "alice", "password": "student123"})
    resp_student = client.get("/audit")
    assert resp_student.status_code == 403


def test_backup_page_and_download(client):
    """Verify admin can view backup status and download consistent database snapshot (CA-15)."""
    client.post("/login", data={"username": "admin", "password": "admin123"})

    # Check status page
    resp_page = client.get("/backup")
    assert resp_page.status_code == 200
    assert b"Active Storage Status" in resp_page.data

    # Download backup file
    resp_dl = client.get("/backup/download")
    assert resp_dl.status_code == 200
    assert resp_dl.content_type == "application/x-sqlite3"

    # SQLite database files always begin with the header 'SQLite format 3\x00'
    backup_bytes = resp_dl.data
    assert backup_bytes.startswith(b"SQLite format 3")

    # Restore Verification Test: verify the snapshot is a valid SQLite DB with intact tables
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_backup:
        temp_backup.write(backup_bytes)
        temp_backup_path = temp_backup.name

    restore_conn = sqlite3.connect(temp_backup_path)
    restore_conn.row_factory = sqlite3.Row
    rows = restore_conn.execute("SELECT roll_no, name FROM students").fetchall()
    assert len(rows) > 0
    student_rolls = [r["roll_no"] for r in rows]
    assert "CS-001" in student_rolls
    restore_conn.close()


def test_backup_access_denied_for_non_admin(client):
    """Verify non-admin roles cannot download database backup."""
    client.post("/login", data={"username": "prof_smith", "password": "faculty123"})
    resp_fac = client.get("/backup/download")
    assert resp_fac.status_code == 403

    client.get("/logout")
    client.post("/login", data={"username": "alice", "password": "student123"})
    resp_stu = client.get("/backup/download")
    assert resp_stu.status_code == 403

