"""Pandas-powered attendance aggregation and statistical reporting service (CA-11)."""

import pandas as pd


def compute_attendance_analytics(conn, course_id=None):
    """Calculate aggregated attendance statistics using Pandas.
    
    Returns a dictionary of structured metrics and Chart.js-ready data series.
    """
    # 1. Extract raw attendance data merged with student and course details
    query = """
        SELECT 
            a.id AS attendance_id,
            a.attendance_date,
            a.status,
            s.id AS student_id,
            s.roll_no,
            s.name AS student_name,
            c.id AS course_id,
            c.code AS course_code,
            c.name AS course_name
        FROM attendance a
        JOIN students s ON s.id = a.student_id
        JOIN courses c ON c.id = a.course_id
    """
    params = ()
    if course_id:
        query += " WHERE a.course_id = ?"
        params = (course_id,)

    df = pd.read_sql_query(query, conn, params=params)

    # If dataset is empty, return safe default structures
    if df.empty:
        return {
            "total_records": 0,
            "overall_percentage": 0.0,
            "total_sessions": 0,
            "at_risk_count": 0,
            "at_risk_students": [],
            "course_comparison": {"labels": [], "percentages": [], "present_counts": [], "total_counts": []},
            "timeline_trends": {"labels": [], "percentages": []},
            "student_summary": [],
        }

    # Normalize status column
    df["is_present"] = (df["status"] == "Present").astype(int)

    total_records = len(df)
    total_presents = df["is_present"].sum()
    overall_percentage = round((total_presents / total_records * 100.0), 1) if total_records > 0 else 0.0

    # 2. Course-wise Aggregation
    course_group = df.groupby(["course_id", "course_code", "course_name"]).agg(
        total=("is_present", "count"),
        present=("is_present", "sum"),
    ).reset_index()

    course_group["percentage"] = (course_group["present"] / course_group["total"] * 100.0).round(1)

    course_labels = course_group["course_code"].tolist()
    course_percentages = course_group["percentage"].tolist()
    course_present = course_group["present"].tolist()
    course_total = course_group["total"].tolist()

    # 3. Student-wise Aggregation (to identify at-risk students < 75%)
    student_group = df.groupby(["student_id", "roll_no", "student_name"]).agg(
        total=("is_present", "count"),
        present=("is_present", "sum"),
    ).reset_index()

    student_group["percentage"] = (student_group["present"] / student_group["total"] * 100.0).round(1)
    student_group = student_group.sort_values(by=["percentage", "roll_no"], ascending=[True, True])

    student_summary = student_group.to_dict(orient="records")
    at_risk_students = [s for s in student_summary if s["percentage"] < 75.0]

    # 4. Date-wise Timeline Trends
    timeline_group = df.groupby("attendance_date").agg(
        total=("is_present", "count"),
        present=("is_present", "sum"),
    ).reset_index().sort_values(by="attendance_date")

    timeline_group["percentage"] = (timeline_group["present"] / timeline_group["total"] * 100.0).round(1)

    timeline_labels = timeline_group["attendance_date"].tolist()
    timeline_percentages = timeline_group["percentage"].tolist()

    return {
        "total_records": int(total_records),
        "overall_percentage": float(overall_percentage),
        "total_sessions": int(len(timeline_group)),
        "at_risk_count": len(at_risk_students),
        "at_risk_students": at_risk_students,
        "course_comparison": {
            "labels": course_labels,
            "percentages": course_percentages,
            "present_counts": course_present,
            "total_counts": course_total,
        },
        "timeline_trends": {
            "labels": timeline_labels,
            "percentages": timeline_percentages,
        },
        "student_summary": student_summary,
    }

