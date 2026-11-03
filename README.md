# AttendX — Intelligent Attendance & Academic Analytics Platform

**ENSP401 – Cloud Computing Capstone Project**  
*Role-Based Academic Attendance Management, Statistical Reporting & Privacy-Enforced Self-Service*

[![Tests](https://img.shields.io/badge/tests-36%20passed-success)](tests/)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/framework-Flask%203.x-lightgrey)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/prototype-academic-orange)]()

---

## 1. Project Overview & Vision
**AttendX** is a role-governed web application built for academic institutions to eliminate manual paper registers and fragmented spreadsheets. It delivers:
- **Administrators**: Centralized student profile creation, course catalogue administration, student-course enrollment rosters, immutable audit logging, and point-in-time database snapshots.
- **Faculty**: Streamlined, fast attendance marking per course and session date, featuring atomic database transactions and real-time class summaries.
- **Students**: Self-service dashboards strictly enforcing row-level ownership isolation (`WHERE student_id = ?`) allowing learners to monitor attendance percentages, attended/missed counts, and class history.
- **Analytics Engine**: Grouped aggregations computed via **Pandas 2.x** and interactive, responsive data visualizations rendered client-side with **Chart.js 4.x**.

---

## 2. Technical Architecture & Stack

```
                      +---------------------------------------+
                      |       Web Browser (Client UI)         |
                      | HTML5 + CSS3 + Bootstrap 5 + Chart.js |
                      +-------------------+-------------------+
                                          | HTTP / HTTPS
                                          v
                      +---------------------------------------+
                      |       Flask Web Application           |
                      | - Session & Auth Management           |
                      | - Role & Ownership Authorization      |
                      | - Student & Course Services           |
                      | - Attendance Transaction Engine       |
                      | - Audit & Backup Services             |
                      +-----------+-------------------+-------+
                                  |                   |
                     Raw SQL / DB |                   | DataFrame Extraction
                                  v                   v
                      +--------------------+  +--------------------+
                      | SQLite 3 Database  |  |  Pandas Analytics  |
                      | (Relational Store) |  | (Aggregations/KPI) |
                      +--------------------+  +--------------------+
                                  |
                                  v
                      +---------------------------------------+
                      | Docker Container (Named Volume Mount) |
                      +---------------------------------------+
```

| Layer | Technology | Details / Implementation |
| :--- | :--- | :--- |
| **Backend Framework** | Python 3.11 / Flask 3.0.3 | Application factory pattern, Jinja2 templating, modular Blueprints. |
| **Authentication & Security** | Werkzeug 3.0.3 | Secure password hashing (`scrypt`/`pbkdf2`), session fixation mitigation, generic errors. |
| **Database** | SQLite 3 | Relational storage with strict foreign keys (`PRAGMA foreign_keys = ON;`) and WAL mode. |
| **Data Analytics** | Pandas 2.2.2 | In-memory aggregations, course comparison rates, timeline trends, at-risk detection ($<75\%$). |
| **Frontend Styling** | Bootstrap 5.3.3 + Custom CSS | Academic design tokens (Navy `#17365D`, Blue `#2874C8`, Teal `#159A9C`), 8px rhythm. |
| **Data Visualizations** | Chart.js 4.4.3 | Responsive bar charts and time-series line trends with accessible table mirrors. |
| **WSGI Server** | Gunicorn 22.0.0 | Production container server with 2 worker processes. |
| **Containerization** | Docker Engine & Compose | Container image with persistent named volume mount (`cloudattend_data`). |
| **Testing Suite** | Pytest 8.2.2 | 36 automated unit, integration, RBAC, IDOR privacy, and latency benchmark tests. |

---

## 3. Demo User Accounts (Synthetic Seed Data)

| Role | Username | Password | Linked Entity / Permissions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Full administrative control: students, courses, enrollments, audit logs, backup. |
| **Faculty** | `prof_smith` | `faculty123` | Class attendance entry, course overview, analytics, CSV exports. |
| **Faculty** | `prof_johnson` | `faculty123` | Secondary faculty account for concurrency testing. |
| **Student** | `alice` | `student123` | Roll No: `CS-001`. Personal self-service attendance dashboard only. |
| **Student** | `bob` | `student123` | Roll No: `CS-002`. Personal self-service attendance dashboard only. |
| **Student** | `charlie` | `student123` | Roll No: `CS-003`. Personal self-service attendance dashboard only. |
| **Student** | `diana` | `student123` | Roll No: `CS-004`. Personal self-service attendance dashboard only. |

---

## 4. End-to-End Evaluation & Demo Runbook

### Flow 1: Faculty Records Daily Attendance
1. Sign in as `prof_smith` with password `faculty123`.
2. Land on the **Faculty Portal** (`/dashboard`).
3. Click **Take Attendance** (`/attendance`).
4. Select course `CS101 — Introduction to Computer Science` and the date.
5. The enrolled student roster loads with `Present`/`Absent` toggles.
6. Use the quick helper button **Mark All Present** or customize individual rows.
7. Click **Save Attendance**. The submission persists atomically in an explicit SQLite transaction with audit trail logging.

### Flow 2: Student Self-Service & Privacy Verification
1. Sign in as `alice` with password `student123`.
2. Notice automatic redirection to **Student Dashboard** (`/student/dashboard`).
3. Observe overall attendance rate (e.g. `80.0%`), attended count, course breakdown, and chronological session logs.
4. Attempt to access administrative routes (e.g. `/students` or `/audit`) $\rightarrow$ immediately blocked with **403 Forbidden**.
5. Switch accounts to `bob` $\rightarrow$ verify Bob only sees Roll `CS-002` and cannot inspect Alice's data.

### Flow 3: Administrator Operations & Backup
1. Sign in as `admin` with password `admin123`.
2. Navigate to **Students** (`/students`) $\rightarrow$ Search existing students or click **Add New Student** with roll number uniqueness enforcement.
3. Navigate to **Courses** (`/courses`) $\rightarrow$ Manage curriculum catalogue and modify enrollment rosters.
4. Navigate to **Analytics** (`/analytics`) $\rightarrow$ Review interactive Chart.js bar and line graphs and export reports via **Export CSV Report** (`/export/csv`).
5. Navigate to **Audit Log** (`/audit`) $\rightarrow$ Inspect immutable system activity log.
6. Navigate to **Backup** (`/backup`) $\rightarrow$ Click **Download Database Snapshot (.db)** to generate a live, consistent snapshot using `conn.backup()`.

---

## 5. Performance & Resource Benchmarks (CA-19)

Empirically measured under test load using Pytest and Python high-precision counters (`time.perf_counter`):
- **Health Liveness (`/health`)**: Average **0.44 ms** latency (Median: **0.32 ms**).
- **Analytics Aggregation (`/analytics`)**: Average **27.85 ms** latency (Median: **24.62 ms**) including full Pandas aggregation and Jinja2 HTML rendering.
- **Process Memory Footprint**: Minimal (~38 MB RSS), well within container limits.

---

## 6. Installation & Execution Guide

### Local Development Setup
```bash
# 1. Clone repository
git clone https://github.com/ADITYAGUPTA112/student_attendance_system.git
cd student_attendance_system

# 2. Create and activate virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# 3. Install pinned dependencies
pip install -r requirements.txt

# 4. Initialize and seed database
flask init-db --seed

# 5. Run the application
python app.py
```
Visit `http://localhost:5000` in your browser.

### Docker Compose Deployment
```bash
docker compose up -d --build
```
- App container runs with production WSGI server **Gunicorn**.
- Health check probes `http://localhost:5000/health`.
- Data is stored on persistent named volume `cloudattend_data` mounted at `/app/instance`.

### Running Automated Test Suite
```bash
pytest -v
```
All **36 tests** covering security, RBAC, schema, privacy, calculations, and benchmarks will execute and pass.
