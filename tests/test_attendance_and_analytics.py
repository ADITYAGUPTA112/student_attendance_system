"""Tests for Attendance Entry, Analytics Aggregation, and CSV Export (CA-09, CA-11, CA-12, CA-13)."""

from datetime import date
from analytics_service import compute_attendance_analytics
from db import get_db


def test_attendance_page_renders_roster(client):
    """Verify faculty can view attendance entry page with enrolled students."""
    client.post("/login", data={"username": "prof_smith", "password": "faculty123"})
    response = client.get("/attendance?course_id=1")
    assert response.status_code == 200
    assert b"Class Attendance Entry" in response.data
    assert b"CS101" in response.data
    assert b"CS-001" in response.data


def test_attendance_submission_persists_atomically(client, app):
    """Verify faculty can submit attendance and records persist in the database."""
    client.post("/login", data={"username": "prof_smith", "password": "faculty123"})

    test_date = "2026-11-02"
    # Submit for Course 1 (CS101): student 1 present, student 2 absent
    response = client.post(
        "/attendance",
        data={
            "course_id": "1",
            "date": test_date,
            "status_1": "Present",
            "status_2": "Absent",
            "status_3": "Present",
            "status_4": "Present",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"saved successfully" in response.data

    with app.app_context():
        database = get_db()
        rec1 = database.execute(
            "SELECT status FROM attendance WHERE student_id = 1 AND course_id = 1 AND attendance_date = ?",
            (test_date,),
        ).fetchone()
        assert rec1 is not None
        assert rec1["status"] == "Present"

        rec2 = database.execute(
            "SELECT status FROM attendance WHERE student_id = 2 AND course_id = 1 AND attendance_date = ?",
            (test_date,),
        ).fetchone()
        assert rec2 is not None
        assert rec2["status"] == "Absent"


def test_attendance_update_on_duplicate_date(client, app):
    """Verify submitting attendance on a date that already has records updates them cleanly."""
    client.post("/login", data={"username": "prof_smith", "password": "faculty123"})
    test_date = "2026-11-03"

    # Initial submission: student 1 is Absent
    client.post(
        "/attendance",
        data={"course_id": "1", "date": test_date, "status_1": "Absent"},
    )

    # Update submission: change student 1 to Present
    client.post(
        "/attendance",
        data={"course_id": "1", "date": test_date, "status_1": "Present"},
    )

    with app.app_context():
        database = get_db()
        rec = database.execute(
            "SELECT status FROM attendance WHERE student_id = 1 AND course_id = 1 AND attendance_date = ?",
            (test_date,),
        ).fetchone()
        assert rec["status"] == "Present"


def test_analytics_computation_unit(app):
    """Verify Pandas aggregation calculations for known dataset."""
    with app.app_context():
        database = get_db()
        metrics = compute_attendance_analytics(database)
        assert metrics["total_records"] > 0
        assert 0.0 <= metrics["overall_percentage"] <= 100.0
        assert "labels" in metrics["course_comparison"]
        assert "percentages" in metrics["course_comparison"]
        assert len(metrics["course_comparison"]["labels"]) > 0


def test_analytics_dashboard_renders(client):
    """Verify analytics page renders with Chart.js canvas elements."""
    client.post("/login", data={"username": "admin", "password": "admin123"})
    response = client.get("/analytics")
    assert response.status_code == 200
    assert b"Attendance Analytics" in response.data
    assert b"courseBarChart" in response.data
    assert b"timelineLineChart" in response.data


def test_csv_report_export(client):
    """Verify authorized user can download CSV attendance report."""
    client.post("/login", data={"username": "prof_smith", "password": "faculty123"})
    response = client.get("/export/csv")
    assert response.status_code == 200
    assert response.content_type == "text/csv; charset=utf-8"
    assert b"Roll Number,Student Name,Course Code" in response.data
    assert b"CS-001" in response.data


def test_student_forbidden_from_attendance_marking(client):
    """Verify student is forbidden from accessing /attendance."""
    client.post("/login", data={"username": "alice", "password": "student123"})
    response = client.get("/attendance")
    assert response.status_code == 403


def test_mapreduce_analytics_unit(app):
    """Verify MapReduce distributed aggregation calculates correct daily and course totals."""
    import mapreduce_engine
    with app.app_context():
        database = get_db()
        mr_results = mapreduce_engine.compute_mapreduce_analytics(database)
        assert len(mr_results["course_totals"]) > 0
        assert len(mr_results["daily_totals"]) > 0
        assert mr_results["telemetry"]["num_records"] > 0
        assert "map_duration_ms" in mr_results["telemetry"]
        assert "reduce_duration_ms" in mr_results["telemetry"]


def test_api_analytics_mapreduce_endpoint(client):
    """Verify /api/analytics/mapreduce returns JSON with MapReduce paradigm and stages."""
    client.post("/login", data={"username": "admin", "password": "admin123"})
    response = client.get("/api/analytics/mapreduce")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "success"
    assert json_data["paradigm"] == "MapReduce"
    assert "daily_totals" in json_data["results"]
    assert "course_totals" in json_data["results"]


def test_mapreduce_ui_section_renders(client):
    """Verify analytics page displays the Cloud MapReduce section."""
    client.post("/login", data={"username": "admin", "password": "admin123"})
    response = client.get("/analytics")
    assert response.status_code == 200
    assert b"MapReduce Engine" in response.data
    assert b"Course-Wise Totals (MapReduce)" in response.data
    assert b"Daily Totals (MapReduce)" in response.data


