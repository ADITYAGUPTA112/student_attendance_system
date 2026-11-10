# Project Memory & Progress Tracker — CloudAttend

## 1. Project Snapshot
- **Project Name**: CloudAttend (AttendX) — Intelligent Student Attendance & Analytics Platform
- **Course Context**: ENSP401 – Computational Services in the Cloud Capstone Project
- **Architecture Stack**: Python 3.11, Flask 3.x, SQLite 3 (WAL Mode) / PostgreSQL-ready, Pandas 2.x, Bootstrap 5.3, Chart.js 4.x, Gunicorn 22.x, Docker & Docker Compose, Pytest
- **Primary Roles**: `admin`, `faculty`, `student`
- **Live Production URL**: [https://student-attendance-system-5gdl.onrender.com](https://student-attendance-system-5gdl.onrender.com)
- **Current Status**: **PRODUCTION DEPLOYED ON RENDER & ALL 40 AUTOMATED TESTS PASSING** (100% pass rate)

---

## 2. Step-by-Step Execution Matrix

### Phase 1: Foundation & Authentication (Sprint 1)
- [x] **Step 1.1 (CA-01)**: Project Scaffolding & Environment Setup (`requirements.txt`, `.gitignore`, `.env.example`, skeleton `app.py`, test runner)
- [x] **Step 1.2 (CA-02)**: SQLite Schema & Synthetic Seed Data (`users`, `students`, `courses`, `enrollments`, `attendance`, `audit_logs`, FK enforcement)
- [x] **Step 1.3 (CA-03)**: Authentication & Session Lifecycle (`/login`, `/logout`, `check_password_hash`, generic error messages)
- [x] **Step 1.4 (CA-04)**: Server-Side RBAC Helpers & Decorators (`@login_required`, `@role_required`, 403 error handler)
- [x] **Step 1.5 (CA-05)**: Role-Aware Dashboards & Navigation (Dynamic navbar, Admin/Faculty/Student landing views)

### Phase 2: Academic Record Management (Sprint 2)
- [x] **Step 2.1 (CA-06)**: Student Record Management (Admin list/add students, roll number uniqueness validation)
- [x] **Step 2.2 (CA-07)**: Course Catalogue Management (Admin/Faculty course view, course code uniqueness)
- [x] **Step 2.3 (CA-08)**: Student-Course Enrollment Mapping (Composite PK, course rosters)

### Phase 3: Attendance Engine & Analytics (Sprint 3)
- [x] **Step 3.1 (CA-09)**: Attendance Entry UI & Backend (Faculty course/date marking, atomic multi-row transactions)
- [x] **Step 3.2 (CA-10)**: Student Personal Attendance View & Privacy (Row-level isolation, zero cross-student leakage)
- [x] **Step 3.3 (CA-11)**: Attendance Aggregation Service with Pandas (Summary stats, percentages, zero-handling)
- [x] **Step 3.4 (CA-12)**: Visual Analytics Dashboard with Chart.js (KPI cards, bar/line charts, accessible tables)

### Phase 4: Operations, Security & Persistence (Sprint 4)
- [x] **Step 4.1 (CA-13)**: Scoped CSV Report Export (`/export/csv`, RFC 4180 escaping)
- [x] **Step 4.2 (CA-14)**: System Audit Logging (`audit_logs` tracking, `/audit` admin view)
- [x] **Step 4.3 (CA-15)**: Database Backup & Snapshot Download (`/backup` using `conn.backup()`)
- [x] **Step 4.4 (CA-17)**: Dockerfile & Container Volume Persistence (Gunicorn + Compose named volume)
- [x] **Step 4.5 (CA-18)**: Automated Route & Security Pytest Suite (Full negative & positive test matrix)
- [x] **Step 4.6 (CA-19)**: Performance & Resource Footprint Benchmark (Measured 0.44ms health, 27.85ms analytics)

### Phase 5: UI Polish, Accessibility & Modernization (Sprint 5)
- [x] **Step 5.1 (CA-16)**: Responsive Design System & Accessibility (WCAG 4.5:1 contrast, 8px grid, mobile drawer)
- [x] **Step 5.2 (CA-20)**: Final README, Architecture Documentation & Viva Demo Evidence
- [x] **Step 5.3 (Stitch UI)**: Modern UI overhaul with Plus Jakarta Sans & Space Grotesk typography, segmented status controls, real-time roster counter, responsive KPI cards.
- [x] **Step 5.4 (Sidebar Navigation)**: Migrated primary navigation from top header to a modern collapsible left sidebar with desktop mini-mode (`76px`, persisted in `localStorage`) and mobile drawer. Removed Command Palette search launcher per user request.

### Phase 6: Cloud Services, MapReduce & 2-Way Sync (Sprint 6)
- [x] **Step 6.1 (Cloud Deployment)**: Deployed production web service on **Render Cloud PaaS** (`https://student-attendance-system-5gdl.onrender.com`) running multi-worker Gunicorn WSGI behind Cloudflare CDN. Added Vercel Serverless configurations (`vercel.json`, `api/index.py`).
- [x] **Step 6.2 (Cloud MapReduce Engine)**: Implemented [`mapreduce_engine.py`](file:///c:/Student_Attendance_System/mapreduce_engine.py) executing Map -> Shuffle & Sort -> Reduce pipeline to compute daily and course-wise totals. Added interactive MapReduce telemetry card on `/analytics` and JSON endpoint `/api/analytics/mapreduce`.
- [x] **Step 6.3 (2-Way Data Sync)**: Added 1-Click Database Restore & Upload (`/backup/restore`) in `app.py` and `backup.html` allowing seamless data portability between local development and cloud deployment.
- [x] **Step 6.4 (Test Expansion)**: Expanded automated test suite from 36 to **40 automated tests**, all passing in ~18s.
- [x] **Step 6.5 (Cloud PostgreSQL Setup)**: Initiated Render Managed PostgreSQL instance provisioning for zero-maintenance permanent cloud storage.

---

## 3. Key Invariants & Architectural Rules
1. **Relational Data Integrity**: SQLite 3 with WAL mode; foreign key enforcement (`PRAGMA foreign_keys = ON;`) on every connection.
2. **Row-Level Security**: Student queries strictly inject `WHERE student_id = ?` using `session['student_id']`.
3. **Parameterized SQL Only**: Strict prohibition against SQL string concatenation (`?` placeholders used throughout).
4. **Atomic Transactions**: Attendance submissions executed in multi-row atomic transactions with rollback protection.
5. **No Real PII**: 100% synthetic demo records and test data.
6. **Cloud Architecture Compliance**: Adheres to the three pillars of "Computational Services in the Cloud": Cloud Applications (Docker, Gunicorn, Render PaaS), Data Processing (Pandas + MapReduce aggregation), and Security (PBKDF2 hashing, RBAC, tamper-evident audit logs).

---

## 4. Current Work Log & Milestones
- **Production Live**: `https://student-attendance-system-5gdl.onrender.com`
- **MapReduce Pipeline**: Active and verified via unit tests and REST API (`/api/analytics/mapreduce`).
- **Database Backup & Restore**: Active for 2-way sync (Download `.db` / Upload `.db`).
- **Pytest Suite**: **40 passed in 18.35s** (100% pass rate).
