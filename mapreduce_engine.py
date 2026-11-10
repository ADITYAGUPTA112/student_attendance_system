"""Cloud MapReduce Aggregation Engine for CloudAttend.

Implements the classic MapReduce distributed computing paradigm (Mapper -> Shuffle & Sort -> Reducer)
to compute Daily Attendance Totals, Course-wise Totals, and Student Attendance Aggregates.
Designed for the 'Computational Services in the Cloud' curriculum.
"""

import time
from collections import defaultdict
from typing import List, Tuple, Dict, Any


def mapper_course_totals(record: dict) -> Tuple[str, Tuple[int, int]]:
    """Mapper Function for Course-wise Attendance.
    
    Emits: (course_code, (1 if Present else 0, 1))
    """
    key = record["course_code"]
    value = (1 if record["status"] == "Present" else 0, 1)
    return key, value


def mapper_daily_totals(record: dict) -> Tuple[str, Tuple[int, int]]:
    """Mapper Function for Daily Attendance Totals.
    
    Emits: (attendance_date, (1 if Present else 0, 1))
    """
    key = record["attendance_date"]
    value = (1 if record["status"] == "Present" else 0, 1)
    return key, value


def mapper_student_totals(record: dict) -> Tuple[Tuple[str, str], Tuple[int, int]]:
    """Mapper Function for Student Attendance Aggregation.
    
    Emits: ((roll_no, student_name), (1 if Present else 0, 1))
    """
    key = (record["roll_no"], record["student_name"])
    value = (1 if record["status"] == "Present" else 0, 1)
    return key, value


def shuffle_and_sort(mapped_pairs: List[Tuple[Any, Tuple[int, int]]]) -> Dict[Any, List[Tuple[int, int]]]:
    """Shuffle & Sort / Partitioning Phase.
    
    Groups all intermediate (Key, Value) pairs by Key across simulated partition workers.
    """
    grouped = defaultdict(list)
    for key, value in mapped_pairs:
        grouped[key].append(value)
    return dict(sorted(grouped.items()))


def reducer_attendance(key: Any, values: List[Tuple[int, int]]) -> Dict[str, Any]:
    """Reducer Function.
    
    Aggregates list of (is_present, 1) values for a given key:
    Sums total present count and total session count, and derives attendance percentage.
    """
    total_present = sum(v[0] for v in values)
    total_sessions = sum(v[1] for v in values)
    percentage = round((total_present / total_sessions * 100.0), 1) if total_sessions > 0 else 0.0
    
    return {
        "key": key,
        "present_count": total_present,
        "total_sessions": total_sessions,
        "percentage": percentage,
    }


def execute_mapreduce_pipeline(raw_records: List[dict], num_workers: int = 4) -> Dict[str, Any]:
    """Runs end-to-end MapReduce pipeline on raw attendance records.
    
    Simulates distributed cloud processing across Map, Shuffle/Sort, and Reduce phases.
    Returns:
        - daily_totals: List of aggregated daily metrics
        - course_totals: List of aggregated course-wise metrics
        - student_totals: List of aggregated student-wise metrics
        - telemetry: Execution metrics (stage timing, sample intermediate pairs, worker count)
    """
    start_time = time.perf_counter()

    if not raw_records:
        return {
            "daily_totals": [],
            "course_totals": [],
            "student_totals": [],
            "telemetry": {
                "num_records": 0,
                "execution_time_ms": 0.0,
                "num_workers": num_workers,
                "map_samples": [],
                "shuffled_keys_count": 0,
            }
        }

    # -------------------------------------------------------------------------
    # 1. MAP PHASE (Distribute records across mappers)
    # -------------------------------------------------------------------------
    t_map_start = time.perf_counter()
    
    mapped_courses: List[Tuple[str, Tuple[int, int]]] = []
    mapped_dates: List[Tuple[str, Tuple[int, int]]] = []
    mapped_students: List[Tuple[Tuple[str, str], Tuple[int, int]]] = []

    for rec in raw_records:
        mapped_courses.append(mapper_course_totals(rec))
        mapped_dates.append(mapper_daily_totals(rec))
        mapped_students.append(mapper_student_totals(rec))

    t_map_end = time.perf_counter()

    # -------------------------------------------------------------------------
    # 2. SHUFFLE & SORT PHASE (Group intermediate key-value pairs)
    # -------------------------------------------------------------------------
    t_shuffle_start = time.perf_counter()

    grouped_courses = shuffle_and_sort(mapped_courses)
    grouped_dates = shuffle_and_sort(mapped_dates)
    grouped_students = shuffle_and_sort(mapped_students)

    t_shuffle_end = time.perf_counter()

    # -------------------------------------------------------------------------
    # 3. REDUCE PHASE (Aggregate totals for each partition key)
    # -------------------------------------------------------------------------
    t_reduce_start = time.perf_counter()

    course_results = [
        reducer_attendance(key, values) for key, values in grouped_courses.items()
    ]
    daily_results = [
        reducer_attendance(key, values) for key, values in grouped_dates.items()
    ]
    student_results = [
        {
            "roll_no": key[0],
            "name": key[1],
            "present_count": res["present_count"],
            "total_sessions": res["total_sessions"],
            "percentage": res["percentage"],
        }
        for key, values in grouped_students.items()
        for res in [reducer_attendance(key, values)]
    ]
    # Sort students by percentage ascending to highlight at-risk learners
    student_results.sort(key=lambda s: (s["percentage"], s["roll_no"]))

    t_reduce_end = time.perf_counter()
    total_time_ms = round((time.perf_counter() - start_time) * 1000, 3)

    return {
        "daily_totals": daily_results,
        "course_totals": course_results,
        "student_totals": student_results,
        "telemetry": {
            "num_records": len(raw_records),
            "num_workers": num_workers,
            "execution_time_ms": total_time_ms,
            "map_duration_ms": round((t_map_end - t_map_start) * 1000, 3),
            "shuffle_duration_ms": round((t_shuffle_end - t_shuffle_start) * 1000, 3),
            "reduce_duration_ms": round((t_reduce_end - t_reduce_start) * 1000, 3),
            "map_samples": [
                {"key": k, "value": v} for k, v in mapped_courses[:6]
            ],
            "shuffled_keys_count": len(grouped_courses) + len(grouped_dates),
        }
    }


def compute_mapreduce_analytics(conn, course_id=None, num_workers=4) -> Dict[str, Any]:
    """Extract raw attendance data from DB and feed it into the MapReduce pipeline."""
    query = """
        SELECT 
            a.id AS attendance_id,
            a.attendance_date,
            a.status,
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

    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Convert sqlite3.Row or tuples to dicts
    records = []
    for row in rows:
        if isinstance(row, dict):
            records.append(row)
        else:
            records.append({
                "attendance_id": row["attendance_id"],
                "attendance_date": row["attendance_date"],
                "status": row["status"],
                "roll_no": row["roll_no"],
                "student_name": row["student_name"],
                "course_id": row["course_id"],
                "course_code": row["course_code"],
                "course_name": row["course_name"],
            })

    return execute_mapreduce_pipeline(records, num_workers=num_workers)
