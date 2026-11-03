# Step-by-Step Project Execution Plan — CloudAttend

This document outlines the complete, step-by-step ("step-wise") implementation plan for CloudAttend. Each phase is subdivided into discrete, sequential steps with specific deliverables, affected files, acceptance criteria, and verification commands.

---

## Architecture of Phases

```
+----------------------------------------------------------------------------------+
| PHASE 1: FOUNDATION & AUTHENTICATION (Steps 1.1 - 1.5)                           |
| Scaffolding -> Database & Seed -> Auth & Sessions -> RBAC Decorators -> Dashboards|
+----------------------------------------------------------------------------------+
                                         │
                                         ▼
+----------------------------------------------------------------------------------+
| PHASE 2: ACADEMIC DATA MANAGEMENT (Steps 2.1 - 2.3)                              |
| Student Records (Admin) -> Course Catalogue -> Student-Course Enrollment Mapping |
+----------------------------------------------------------------------------------+
                                         │
                                         ▼
+----------------------------------------------------------------------------------+
| PHASE 3: ATTENDANCE ENGINE & ANALYTICS (Steps 3.1 - 3.4)                         |
| Daily Attendance Entry -> Student Self-Service (Privacy) -> Pandas -> Chart.js   |
+----------------------------------------------------------------------------------+
                                         │
                                         ▼
+----------------------------------------------------------------------------------+
| PHASE 4: OPERATIONS, SECURITY & PERSISTENCE (Steps 4.1 - 4.6)                    |
| CSV Export -> Audit Logging -> Backup/Restore -> Docker -> Pytest -> Benchmarks  |
+----------------------------------------------------------------------------------+
                                         │
                                         ▼
+----------------------------------------------------------------------------------+
| PHASE 5: DESIGN POLISH & SUBMISSION EVIDENCE (Steps 5.1 - 5.2)                   |
| Bootstrap / CSS Design System -> Final README, Runbook & Capstone Demo Evidence  |
+----------------------------------------------------------------------------------+
```

---

## Phase 1: Foundation & Authentication

### Step 1.1 — Project Scaffolding & Environment Setup (CA-01)
- **Goal**: Create a clean, reproducible Flask project environment with pinned dependencies.
- **Files Created/Modified**:
  - `requirements.txt`: Pin `Flask==3.0.3`, `pandas==2.2.2`, `gunicorn==22.0.0`, `pytest==8.2.2`, etc.
  - `.gitignore`: Exclude `.venv/`, `__pycache__/`, `instance/*.db`, `.env`, `.pytest_cache/`.
  - `.dockerignore`: Exclude local caches and virtual environments from container builds.
  - `.env.example`: Configuration template (`SECRET_KEY`, `FLASK_ENV`, `DATABASE_PATH`).
  - `app.py`: Minimal Flask factory application with `/health` liveness route.
  - `tests/test_app.py`: Initial test ensuring test runner works and `/health` returns `200 OK`.
- **Verification**: Run `pytest tests/test_app.py`.

### Step 1.2 — Database Schema & Synthetic Seed Data (CA-02)
- **Goal**: Initialize SQLite schema with strict foreign keys and deterministic synthetic demo data.
- **Files Created/Modified**:
  - Database initializer in `app.py` or `db.py`: Enforces `PRAGMA foreign_keys = ON;`.
  - Tables: `users`, `students`, `courses`, `enrollments`, `attendance`, `audit_logs`.
  - Synthetic Demo Seed:
    - Admin: `admin` / `admin123`
    - Faculty: `prof_smith` / `faculty123`, `prof_johnson` / `faculty123`
    - Students: `alice` / `student123` (Roll: CS101-01), `bob` / `student123` (Roll: CS101-02), `charlie` / `student123` (Roll: CS101-03)
- **Verification**: Test database initialization script; verify unique constraints and foreign key enforcement.

### Step 1.3 — Authentication & Session Lifecycle (CA-03)
- **Goal**: Implement secure login, session creation, and logout functionality.
- **Files Created/Modified**:
  - `app.py`: Routes `GET /login`, `POST /login`, `GET /logout`.
  - `templates/login.html`: Accessible login form with username, password, and error alerts.
- **Security Invariants**:
  - Password verification using `werkzeug.security.check_password_hash`.
  - Session regeneration on login to prevent session fixation.
  - Generic error feedback: `"Invalid username or password."`
- **Verification**: Automated tests for valid login, invalid login, and session clearance on logout.

### Step 1.4 — Role-Based Authorization Helpers (CA-04)
- **Goal**: Create server-side access control decorators for `admin`, `faculty`, and `student` roles.
- **Files Created/Modified**:
  - `app.py`: Decorators `@login_required` and `@role_required(*allowed_roles)`.
  - `templates/error.html`: User-friendly 403 Forbidden and 404 Not Found templates.
- **Verification**: Pytest tests attempting cross-role access (e.g. Student accessing Admin route $\rightarrow$ 403 Forbidden).

### Step 1.5 — Role-Aware Dashboards & Navigation (CA-05)
- **Goal**: Provide customized dashboard views and dynamic navigation bars for each role.
- **Files Created/Modified**:
  - `templates/base.html`: Common navbar showing links based on `session['role']`.
  - `templates/dashboard.html`: Staff/Admin dashboard with metrics and management shortcuts.
  - `templates/faculty_dashboard.html`: Faculty view with assigned course shortcuts.
  - `templates/student_dashboard.html`: Student view foundation.
  - `app.py`: Route `/` automatically redirects authenticated users to their specific dashboard.
- **Verification**: Verify that logging in as Admin, Faculty, or Student redirects to the correct dashboard.

---

## Phase 2: Academic Record Management

### Step 2.1 — Student Record Management (CA-06)
- **Goal**: Allow administrators to list, search, and register student profiles.
- **Files Created/Modified**:
  - `app.py`: Routes `GET /students`, `POST /students`.
  - `templates/students.html`: Searchable table of students and modal/form for adding a student.
- **Validation**:
  - Unique roll number validation (`UNIQUE constraint`).
  - Name cannot be whitespace-only.
  - Optional email format check.
- **Verification**: Pytest test confirming Admin can add a student, duplicate roll number is rejected with flash error, and non-admins receive 403.

### Step 2.2 — Course Catalogue Management (CA-07)
- **Goal**: Display and manage course offerings.
- **Files Created/Modified**:
  - `app.py`: Routes `GET /courses`, `POST /courses`.
  - `templates/courses.html`: Course cards/table and admin course creation form.
- **Validation**: Course code uniqueness (e.g. `CS101`, `MATH201`).
- **Verification**: Verify course listing; verify faculty can view courses while only admin can create new courses.

### Step 2.3 — Student-Course Enrollment Mapping (CA-08)
- **Goal**: Map students to courses to create course rosters for attendance.
- **Files Created/Modified**:
  - `app.py`: Routes `POST /courses/<course_id>/enroll`.
  - `templates/courses.html`: Enrollment management modal.
- **Validation**: Composite primary key `(student_id, course_id)` prevents duplicate enrollments.
- **Verification**: Test enrolling students into courses and verifying roster output.

---

## Phase 3: Attendance Engine & Analytics

### Step 3.1 — Attendance Entry UI & Backend (CA-09)
- **Goal**: Allow faculty to record and save daily attendance for enrolled students.
- **Files Created/Modified**:
  - `app.py`: Routes `GET /attendance`, `POST /attendance`.
  - `templates/attendance.html`: Course selector, date input (`YYYY-MM-DD`), student roster with `Present` / `Absent` radio buttons or toggle switches.
- **Data Integrity**:
  - Multi-row insert/update executed in a single atomic SQLite transaction.
  - Status allow-list: strictly `'Present'` or `'Absent'`.
  - Duplicate date behavior: updates existing attendance record for the date or displays warning.
- **Verification**: Submit attendance for a class; verify records in database; verify invalid status is rejected.

### Step 3.2 — Student Personal Attendance View & Privacy (CA-10)
- **Goal**: Enable students to view only their own attendance summaries and history.
- **Files Created/Modified**:
  - `app.py`: Route `GET /student/dashboard`.
  - `templates/student_dashboard.html`: Overall attendance percentage, attended/total counts, course breakdown, and attendance date log.
- **Privacy Enforcement**:
  - Backend strictly binds query to `WHERE student_id = ?` using `session['student_id']`.
  - Tampering with query parameters cannot disclose another student's data.
  - Empty state rendered gracefully if student has no classes recorded.
- **Verification**: Negative security tests: Student A logs in and attempts to access Student B's data $\rightarrow$ blocked.

### Step 3.3 — Attendance Aggregation Service with Pandas (CA-11)
- **Goal**: Compute statistical summaries, class trends, and attendance percentages.
- **Files Created/Modified**:
  - `analytics.py` (or service module inside `app.py`):
    - Reads attendance rows into Pandas DataFrame.
    - Groups by student, course, and date.
    - Calculates present counts, total sessions, and attendance percentages:
      $$\text{Attendance \%} = \frac{\text{Present Count}}{\text{Total Sessions}} \times 100$$
    - Safely handles zero-denominator edge case ($0 / 0 = 0.0\%$).
- **Verification**: Unit tests with test datasets verifying expected statistical outputs.

### Step 3.4 — Analytics Dashboard & Chart.js Visualization (CA-12)
- **Goal**: Render visual analytics, charts, and KPI summary cards for faculty and administrators.
- **Files Created/Modified**:
  - `app.py`: Route `GET /analytics`.
  - `templates/analytics.html`: KPI cards (Average Attendance, At-Risk Students $< 75\%$, Total Classes).
  - `static/js/charts.js`: Chart.js bar charts (course comparison) and line charts (weekly trends).
  - Accessible fallback data table for screen readers.
- **Verification**: Manual browser verification of charts rendering + unit test ensuring analytics endpoint delivers correct JSON / template context.

---

## Phase 4: Operations, Security & Persistence

### Step 4.1 — CSV Report Export (CA-13)
- **Goal**: Allow authorized staff to download attendance reports in standard CSV format.
- **Files Created/Modified**:
  - `app.py`: Route `GET /export/csv`.
- **Validation**: Proper HTTP headers (`Content-Disposition: attachment; filename=attendance_report.csv`), standard RFC 4180 CSV escaping, role check.
- **Verification**: Pytest test downloading CSV, asserting headers and row contents.

### Step 4.2 — System Audit Logging (CA-14)
- **Goal**: Record critical administrative and attendance modifications.
- **Files Created/Modified**:
  - `app.py`: Audit helper function `log_audit(user_id, action, detail)`.
  - `templates/audit.html`: Admin table displaying timestamp, actor username, action, and details.
  - Route `GET /audit`: Accessible only to Admin.
- **Verification**: Trigger login, student creation, attendance mark; confirm corresponding rows appear in `/audit`.

### Step 4.3 — Database Backup & Snapshot Download (CA-15)
- **Goal**: Admin-only feature to generate and download a consistent snapshot of the SQLite database.
- **Files Created/Modified**:
  - `app.py`: Route `GET /backup`.
  - Uses `sqlite3.Connection.backup()` to create a consistent, non-blocking copy.
- **Verification**: Download backup file; restore in a temporary location and verify table contents.

### Step 4.4 — Dockerfile & Container Volume Persistence (CA-17)
- **Goal**: Package the application into a production-ready container with persistent data storage.
- **Files Created/Modified**:
  - `Dockerfile`: Multi-stage or optimized Python 3.11-slim container running Gunicorn.
  - `docker-compose.yml`: App service exposing port 5000 and mounting named volume `cloudattend_data` to `/app/instance`.
- **Verification**:
  - Execute `docker compose up -d --build`.
  - Add a student record, recreate container (`docker compose down && docker compose up -d`).
  - Verify student record persists.

### Step 4.5 — Automated Route & Security Test Suite (CA-18)
- **Goal**: Provide automated test coverage for the entire application.
- **Files Created/Modified**:
  - `tests/test_app.py`:
    - Authentication suite (valid, invalid, logout).
    - RBAC matrix (Admin, Faculty, Student allow/deny).
    - Student IDOR privacy test.
    - Attendance atomic submission test.
    - Aggregation mathematics test.
    - Liveness `/health` test.
- **Verification**: Execute `pytest -v` with 100% passing rate.

### Step 4.6 — Performance & Resource Measurement (CA-19)
- **Goal**: Measure response latency and container resource footprint under simulated workload.
- **Files Created/Modified**:
  - Benchmarking script / test report recording average latency, memory consumption, and CPU usage.
- **Verification**: Document verified latency and memory measurements in project notes.

---

## Phase 5: UI Polish, Accessibility & Final Submission

### Step 5.1 — Responsive Design System & Accessibility (CA-16)
- **Goal**: Apply the design palette, typography, responsive breakpoints, and WCAG accessibility rules.
- **Files Created/Modified**:
  - `static/css/style.css`: Primary Navy (`#17365D`), Primary Blue (`#2874C8`), Accent Teal (`#159A9C`), 8px spacing rhythm.
  - Mobile responsiveness adjustments for tables and forms.
  - Visible focus indicators and ARIA attributes for inputs.
- **Verification**: Check on desktop and mobile viewport widths (360px, 768px, 1200px).

### Step 5.2 — Capstone Documentation & Demo Evidence (CA-20)
- **Goal**: Prepare comprehensive documentation and viva demo runbook.
- **Files Created/Modified**:
  - `README.md`: Architecture diagrams, prerequisites, quickstart instructions (Local & Docker), test commands, and demo credentials.
  - Viva demo walkthrough script.
- **Verification**: Walk through full end-to-end demo flow following the README.
