"""CloudAttend - Intelligent Student Attendance & Analytics Platform
ENSP401 - Cloud Computing Capstone Project
"""

import os
import io
import csv
import tempfile
import sqlite3
from datetime import datetime, date
from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    redirect,
    url_for,
    g,
    request,
    flash,
    send_file,
)
from werkzeug.security import generate_password_hash
import db
import auth
from auth import login_required, role_required, log_audit
import analytics_service

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "instance", "cloudattend.db")


def create_app(test_config=None):
    """Application factory for CloudAttend."""
    app = Flask(__name__, instance_relative_config=True)

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key-cloudattend-2026"),
        DATABASE=os.environ.get("DATABASE_PATH", DEFAULT_DB_PATH),
    )

    if test_config:
        app.config.update(test_config)

    # Register database handlers and CLI commands
    db.init_app(app)

    # Automatically initialize and seed database on first startup if file does not exist
    if not os.path.exists(app.config["DATABASE"]):
        with app.app_context():
            db.init_db()
            db.seed_db()

    # Register Auth blueprint
    app.register_blueprint(auth.bp)

    # -------------------------------------------------------------------------
    # Core Application Routes
    # -------------------------------------------------------------------------

    @app.route("/health", methods=["GET"])
    def health():
        """Liveness response for monitoring and automated verification."""
        return jsonify({
            "status": "healthy",
            "service": "CloudAttend",
            "version": "1.0.0"
        }), 200

    @app.route("/", methods=["GET"])
    def index():
        """Role-aware landing route."""
        if g.user is None:
            return redirect(url_for("auth.login"))
        if g.user["role"] == "student":
            return redirect(url_for("student_dashboard"))
        return redirect(url_for("dashboard"))

    @app.route("/dashboard", methods=["GET"])
    @login_required
    @role_required("admin", "faculty")
    def dashboard():
        """Administrator and Faculty operational dashboard."""
        database = db.get_db()

        # Summary KPIs
        student_count = database.execute("SELECT COUNT(*) AS c FROM students").fetchone()["c"]
        course_count = database.execute("SELECT COUNT(*) AS c FROM courses").fetchone()["c"]
        attendance_count = database.execute("SELECT COUNT(*) AS c FROM attendance").fetchone()["c"]
        audit_count = database.execute("SELECT COUNT(*) AS c FROM audit_logs").fetchone()["c"]

        # Courses list
        courses = database.execute("SELECT id, code, name FROM courses ORDER BY code ASC").fetchall()

        # Recent system activity (audit snapshot)
        recent_activity = database.execute(
            "SELECT action, detail, created_at FROM audit_logs ORDER BY id DESC LIMIT 5"
        ).fetchall()

        stats = {
            "student_count": student_count,
            "course_count": course_count,
            "attendance_count": attendance_count,
            "audit_count": audit_count,
        }

        return render_template(
            "dashboard.html",
            stats=stats,
            courses=courses,
            recent_activity=recent_activity,
        )

    @app.route("/student/dashboard", methods=["GET"])
    @login_required
    @role_required("student")
    def student_dashboard():
        """Student self-service dashboard with strict row-level ownership isolation (CA-10)."""
        database = db.get_db()
        student_id = g.user["student_id"]

        student = database.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        ).fetchone()

        if not student:
            flash("Student profile record not found.", "warning")
            return render_template(
                "student_dashboard.html",
                student={"name": g.user["username"], "roll_no": "N/A", "email": None},
                overall_pct=0.0,
                present_count=0,
                absent_count=0,
                total_sessions=0,
                course_summaries=[],
                attendance_history=[],
            )

        # 1. Total presence/absence counts
        totals = database.execute(
            """
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present_count,
                SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) AS absent_count
            FROM attendance
            WHERE student_id = ?
            """,
            (student_id,),
        ).fetchone()

        total_sessions = totals["total"] or 0
        present_count = totals["present_count"] or 0
        absent_count = totals["absent_count"] or 0
        overall_pct = (present_count / total_sessions * 100.0) if total_sessions > 0 else 0.0

        # 2. Course-by-course breakdown
        course_rows = database.execute(
            """
            SELECT 
                c.id, c.code, c.name,
                COUNT(a.id) AS total,
                SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present
            FROM courses c
            JOIN enrollments e ON e.course_id = c.id
            LEFT JOIN attendance a ON a.course_id = c.id AND a.student_id = e.student_id
            WHERE e.student_id = ?
            GROUP BY c.id, c.code, c.name
            ORDER BY c.code ASC
            """,
            (student_id,),
        ).fetchall()

        course_summaries = []
        for cr in course_rows:
            tot = cr["total"] or 0
            pres = cr["present"] or 0
            pct = (pres / tot * 100.0) if tot > 0 else 0.0
            course_summaries.append({
                "course_code": cr["code"],
                "course_name": cr["name"],
                "total": tot,
                "present": pres,
                "percentage": pct,
            })

        # 3. Attendance Session History
        history = database.execute(
            """
            SELECT a.attendance_date, a.status, c.code AS course_code, c.name AS course_name
            FROM attendance a
            JOIN courses c ON c.id = a.course_id
            WHERE a.student_id = ?
            ORDER BY a.attendance_date DESC, a.id DESC
            LIMIT 20
            """,
            (student_id,),
        ).fetchall()

        return render_template(
            "student_dashboard.html",
            student=student,
            overall_pct=overall_pct,
            present_count=present_count,
            absent_count=absent_count,
            total_sessions=total_sessions,
            course_summaries=course_summaries,
            attendance_history=history,
        )

    # -------------------------------------------------------------------------
    # Phase 2: Academic Record Management Routes (CA-06, CA-07, CA-08)
    # -------------------------------------------------------------------------

    @app.route("/students", methods=["GET", "POST"])
    @login_required
    @role_required("admin")
    def students():
        """List and manage student profiles (Admin only)."""
        database = db.get_db()

        if request.method == "POST":
            roll_no = request.form.get("roll_no", "").strip().upper()
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip() or None
            create_login = bool(request.form.get("create_login"))

            if not roll_no or not name:
                flash("Roll number and Student Name are required.", "danger")
            else:
                existing = database.execute(
                    "SELECT id FROM students WHERE roll_no = ?", (roll_no,)
                ).fetchone()

                if existing:
                    flash(f"A student with roll number '{roll_no}' already exists.", "danger")
                else:
                    try:
                        cur = database.execute(
                            "INSERT INTO students (roll_no, name, email) VALUES (?, ?, ?)",
                            (roll_no, name, email),
                        )
                        student_id = cur.lastrowid

                        if create_login:
                            username = roll_no.lower().replace(" ", "").replace("-", "")
                            default_pass = generate_password_hash("student123")
                            database.execute(
                                """
                                INSERT OR IGNORE INTO users 
                                (username, password_hash, role, student_id)
                                VALUES (?, ?, 'student', ?)
                                """,
                                (username, default_pass, student_id),
                            )

                        log_audit(
                            g.user["id"],
                            "CREATE_STUDENT",
                            f"Added student '{name}' ({roll_no}).",
                        )
                        database.commit()
                        flash(f"Student '{name}' ({roll_no}) registered successfully.", "success")
                        return redirect(url_for("students"))
                    except sqlite3.IntegrityError:
                        database.rollback()
                        flash("A database constraint violation occurred while registering the student.", "danger")

        # GET request: search and list students
        query = request.args.get("q", "").strip()
        if query:
            search_param = f"%{query}%"
            student_rows = database.execute(
                """
                SELECT s.*, COUNT(e.course_id) AS enrolled_count
                FROM students s
                LEFT JOIN enrollments e ON e.student_id = s.id
                WHERE s.name LIKE ? OR s.roll_no LIKE ?
                GROUP BY s.id
                ORDER BY s.roll_no ASC
                """,
                (search_param, search_param),
            ).fetchall()
        else:
            student_rows = database.execute(
                """
                SELECT s.*, COUNT(e.course_id) AS enrolled_count
                FROM students s
                LEFT JOIN enrollments e ON e.student_id = s.id
                GROUP BY s.id
                ORDER BY s.roll_no ASC
                """
            ).fetchall()

        return render_template("students.html", students=student_rows, query=query)

    @app.route("/courses", methods=["GET", "POST"])
    @login_required
    @role_required("admin", "faculty")
    def courses():
        """List course catalogue and create new courses (Admin creates, Faculty views)."""
        database = db.get_db()

        if request.method == "POST":
            if g.user["role"] != "admin":
                flash("Only administrators are authorized to add new courses.", "danger")
                return redirect(url_for("courses"))

            code = request.form.get("code", "").strip().upper()
            name = request.form.get("name", "").strip()

            if not code or not name:
                flash("Course Code and Title are required.", "danger")
            else:
                existing = database.execute(
                    "SELECT id FROM courses WHERE code = ?", (code,)
                ).fetchone()

                if existing:
                    flash(f"Course code '{code}' already exists.", "danger")
                else:
                    try:
                        database.execute(
                            "INSERT INTO courses (code, name) VALUES (?, ?)",
                            (code, name),
                        )
                        log_audit(
                            g.user["id"],
                            "CREATE_COURSE",
                            f"Created new course '{name}' ({code}).",
                        )
                        database.commit()
                        flash(f"Course '{code} — {name}' added successfully.", "success")
                        return redirect(url_for("courses"))
                    except sqlite3.IntegrityError:
                        database.rollback()
                        flash("A database constraint violation occurred while creating the course.", "danger")

        # GET request: fetch courses with enrollment count & roster
        course_rows = database.execute(
            """
            SELECT c.*, COUNT(e.student_id) AS enrolled_count
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            GROUP BY c.id
            ORDER BY c.code ASC
            """
        ).fetchall()

        courses_data = []
        for c in course_rows:
            roster = database.execute(
                """
                SELECT s.id, s.roll_no, s.name
                FROM students s
                JOIN enrollments e ON e.student_id = s.id
                WHERE e.course_id = ?
                ORDER BY s.roll_no ASC
                """,
                (c["id"],),
            ).fetchall()

            courses_data.append({
                "id": c["id"],
                "code": c["code"],
                "name": c["name"],
                "created_at": c["created_at"],
                "enrolled_count": c["enrolled_count"],
                "roster": roster,
            })

        all_students = database.execute(
            "SELECT id, roll_no, name FROM students ORDER BY roll_no ASC"
        ).fetchall()

        return render_template(
            "courses.html",
            courses=courses_data,
            all_students=all_students,
        )

    @app.route("/courses/<int:course_id>/enroll", methods=["POST"])
    @login_required
    @role_required("admin")
    def enroll_student(course_id):
        """Enroll a student into a course (CA-08)."""
        database = db.get_db()
        student_id = request.form.get("student_id")

        if not student_id:
            flash("Please select a student to enroll.", "warning")
            return redirect(url_for("courses"))

        try:
            database.execute(
                "INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
                (student_id, course_id),
            )
            course = database.execute("SELECT code FROM courses WHERE id = ?", (course_id,)).fetchone()
            student = database.execute("SELECT roll_no, name FROM students WHERE id = ?", (student_id,)).fetchone()

            log_audit(
                g.user["id"],
                "ENROLL_STUDENT",
                f"Enrolled {student['name']} ({student['roll_no']}) into {course['code']}.",
            )
            database.commit()
            flash(f"Student {student['roll_no']} successfully enrolled in {course['code']}.", "success")
        except sqlite3.IntegrityError:
            database.rollback()
            flash("This student is already enrolled in this course.", "info")

        return redirect(url_for("courses"))

    @app.route("/courses/<int:course_id>/unenroll/<int:student_id>", methods=["POST"])
    @login_required
    @role_required("admin")
    def unenroll_student(course_id, student_id):
        """Remove student enrollment from a course (CA-08)."""
        database = db.get_db()
        database.execute(
            "DELETE FROM enrollments WHERE student_id = ? AND course_id = ?",
            (student_id, course_id),
        )
        database.commit()
        flash("Student enrollment removed successfully.", "info")
        return redirect(url_for("courses"))

    # -------------------------------------------------------------------------
    # Phase 3: Attendance Engine & Analytics Routes (CA-09, CA-11, CA-12)
    # -------------------------------------------------------------------------

    @app.route("/attendance", methods=["GET", "POST"])
    @login_required
    @role_required("admin", "faculty")
    def attendance():
        """Take or update daily attendance for a selected course and date (CA-09)."""
        database = db.get_db()

        if request.method == "POST":
            course_id = request.form.get("course_id")
            att_date = request.form.get("date", "").strip()

            if not course_id or not att_date:
                flash("Course and Date are required.", "danger")
                return redirect(url_for("attendance"))

            try:
                date.fromisoformat(att_date)
            except ValueError:
                flash("Invalid date format provided. Must be YYYY-MM-DD.", "danger")
                return redirect(url_for("attendance", course_id=course_id, date=att_date))

            roster = database.execute(
                "SELECT student_id FROM enrollments WHERE course_id = ?", (course_id,)
            ).fetchall()

            if not roster:
                flash("Cannot record attendance: No students are enrolled in this course.", "warning")
                return redirect(url_for("attendance", course_id=course_id, date=att_date))

            # Atomic multi-row write transaction
            try:
                count_saved = 0
                for r in roster:
                    s_id = r["student_id"]
                    status = request.form.get(f"status_{s_id}", "Present").strip()
                    if status not in ("Present", "Absent"):
                        status = "Present"

                    database.execute(
                        """
                        INSERT INTO attendance (student_id, course_id, attendance_date, status, marked_by)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(student_id, course_id, attendance_date) 
                        DO UPDATE SET status = excluded.status, marked_by = excluded.marked_by, recorded_at = CURRENT_TIMESTAMP
                        """,
                        (s_id, course_id, att_date, status, g.user["id"]),
                    )
                    count_saved += 1

                course_info = database.execute("SELECT code FROM courses WHERE id = ?", (course_id,)).fetchone()
                log_audit(
                    g.user["id"],
                    "MARK_ATTENDANCE",
                    f"Recorded attendance for {course_info['code']} on {att_date} ({count_saved} students).",
                )
                database.commit()
                flash(f"Attendance for {course_info['code']} on {att_date} saved successfully ({count_saved} records).", "success")
                return redirect(url_for("attendance", course_id=course_id, date=att_date))
            except Exception as ex:
                database.rollback()
                flash(f"Error saving attendance: {str(ex)}", "danger")
                return redirect(url_for("attendance", course_id=course_id, date=att_date))

        # GET request: load courses and roster
        courses = database.execute("SELECT id, code, name FROM courses ORDER BY code ASC").fetchall()

        selected_course_id = request.args.get("course_id", type=int)
        if not selected_course_id and courses:
            selected_course_id = courses[0]["id"]

        selected_date = request.args.get("date", "").strip()
        if not selected_date:
            selected_date = date.today().isoformat()

        selected_course = None
        roster_data = []
        is_existing = False

        if selected_course_id:
            selected_course = database.execute(
                "SELECT id, code, name FROM courses WHERE id = ?", (selected_course_id,)
            ).fetchone()

            if selected_course:
                enrolled = database.execute(
                    """
                    SELECT s.id, s.roll_no, s.name, a.status AS current_status
                    FROM students s
                    JOIN enrollments e ON e.student_id = s.id
                    LEFT JOIN attendance a ON a.student_id = s.id 
                                         AND a.course_id = e.course_id 
                                         AND a.attendance_date = ?
                    WHERE e.course_id = ?
                    ORDER BY s.roll_no ASC
                    """,
                    (selected_date, selected_course_id),
                ).fetchall()

                for st in enrolled:
                    if st["current_status"]:
                        is_existing = True
                    roster_data.append({
                        "id": st["id"],
                        "roll_no": st["roll_no"],
                        "name": st["name"],
                        "current_status": st["current_status"],
                    })

        return render_template(
            "attendance.html",
            courses=courses,
            selected_course=selected_course,
            selected_date=selected_date,
            roster=roster_data,
            is_existing=is_existing,
        )

    @app.route("/analytics", methods=["GET"])
    @login_required
    def analytics():
        """Visual analytics and KPI dashboard powered by Pandas & Chart.js (CA-11, CA-12)."""
        database = db.get_db()
        courses = database.execute("SELECT id, code, name FROM courses ORDER BY code ASC").fetchall()

        course_id = request.args.get("course_id", type=int)

        metrics = analytics_service.compute_attendance_analytics(database, course_id=course_id)

        return render_template(
            "analytics.html",
            courses=courses,
            selected_course_id=course_id,
            metrics=metrics,
        )

    @app.route("/export/csv", methods=["GET"])
    @login_required
    @role_required("admin", "faculty")
    def export_csv():
        """Export attendance reports in CSV format (CA-13)."""
        database = db.get_db()
        course_id = request.args.get("course_id", type=int)

        query = """
            SELECT 
                s.roll_no,
                s.name AS student_name,
                c.code AS course_code,
                c.name AS course_name,
                a.attendance_date,
                a.status,
                u.username AS marked_by_user
            FROM attendance a
            JOIN students s ON s.id = a.student_id
            JOIN courses c ON c.id = a.course_id
            JOIN users u ON u.id = a.marked_by
        """
        params = ()
        if course_id:
            query += " WHERE a.course_id = ?"
            params = (course_id,)
        query += " ORDER BY a.attendance_date DESC, c.code ASC, s.roll_no ASC"

        records = database.execute(query, params).fetchall()

        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        writer.writerow([
            "Roll Number",
            "Student Name",
            "Course Code",
            "Course Title",
            "Attendance Date",
            "Status",
            "Marked By",
        ])

        for r in records:
            writer.writerow([
                r["roll_no"],
                r["student_name"],
                r["course_code"],
                r["course_name"],
                r["attendance_date"],
                r["status"],
                r["marked_by_user"],
            ])

        log_audit(g.user["id"], "EXPORT_CSV", f"Exported attendance CSV report ({len(records)} records).")

        filename = "attendance_report.csv"
        if course_id:
            c = database.execute("SELECT code FROM courses WHERE id = ?", (course_id,)).fetchone()
            if c:
                filename = f"attendance_report_{c['code']}.csv"

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    # -------------------------------------------------------------------------
    # Phase 4: Operations & Security Routes (CA-14, CA-15)
    # -------------------------------------------------------------------------

    @app.route("/audit", methods=["GET"])
    @login_required
    @role_required("admin")
    def audit():
        """Review immutable system audit trail (CA-14)."""
        database = db.get_db()
        query = request.args.get("q", "").strip()

        if query:
            search_param = f"%{query}%"
            logs = database.execute(
                """
                SELECT a.*, u.username
                FROM audit_logs a
                LEFT JOIN users u ON u.id = a.user_id
                WHERE a.action LIKE ? OR a.detail LIKE ? OR u.username LIKE ?
                ORDER BY a.id DESC
                LIMIT 100
                """,
                (search_param, search_param, search_param),
            ).fetchall()
        else:
            logs = database.execute(
                """
                SELECT a.*, u.username
                FROM audit_logs a
                LEFT JOIN users u ON u.id = a.user_id
                ORDER BY a.id DESC
                LIMIT 100
                """
            ).fetchall()

        return render_template("audit.html", logs=logs, query=query)

    @app.route("/backup", methods=["GET"])
    @login_required
    @role_required("admin")
    def backup():
        """Display database storage status and disaster recovery options (CA-15)."""
        database = db.get_db()
        db_path = app.config["DATABASE"]

        size_kb = 0
        if os.path.exists(db_path):
            size_kb = round(os.path.getsize(db_path) / 1024, 2)

        student_count = database.execute("SELECT COUNT(*) AS c FROM students").fetchone()["c"]
        course_count = database.execute("SELECT COUNT(*) AS c FROM courses").fetchone()["c"]
        attendance_count = database.execute("SELECT COUNT(*) AS c FROM attendance").fetchone()["c"]

        db_info = {
            "path": db_path,
            "size_kb": size_kb,
            "student_count": student_count,
            "course_count": course_count,
            "attendance_count": attendance_count,
        }

        return render_template("backup.html", db_info=db_info)

    @app.route("/backup/download", methods=["GET"])
    @login_required
    @role_required("admin")
    def download_backup():
        """Create a consistent online SQLite backup and download snapshot (CA-15)."""
        source_db = db.get_db()

        # Create temporary file for consistent SQLite online backup
        temp_fd, temp_path = tempfile.mkstemp(suffix=".db")
        os.close(temp_fd)

        try:
            dest_db = sqlite3.connect(temp_path)
            # Safe non-blocking SQLite online backup API
            source_db.backup(dest_db)
            dest_db.close()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cloudattend_backup_{timestamp}.db"

            log_audit(g.user["id"], "BACKUP_DATABASE", f"Created database snapshot '{filename}'.")

            return send_file(
                temp_path,
                as_attachment=True,
                download_name=filename,
                mimetype="application/x-sqlite3",
            )
        except Exception as ex:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            flash(f"Backup generation failed: {str(ex)}", "danger")
            return redirect(url_for("backup"))

    # -------------------------------------------------------------------------
    # HTTP Error Handlers
    # -------------------------------------------------------------------------

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template(
            "error.html",
            code=403,
            error_title="403 — Access Forbidden",
            error_message="You do not have permission to access this resource.",
        ), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template(
            "error.html",
            code=404,
            error_title="404 — Page Not Found",
            error_message="The requested page could not be located.",
        ), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template(
            "error.html",
            code=500,
            error_title="500 — Server Error",
            error_message="An internal error occurred. Please try again shortly.",
        ), 500

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        if not os.path.exists(app.config["DATABASE"]):
            db.init_db()
            db.seed_db()
            print("Database initialized and seeded.")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
