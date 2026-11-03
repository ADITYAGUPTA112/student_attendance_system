# Project Memory & Progress Tracker — CloudAttend

## 1. Project Snapshot
- **Project Name**: CloudAttend — Intelligent Student Attendance & Analytics Platform
- **Course Context**: ENSP401 – Cloud Computing Capstone Project
- **Architecture Stack**: Python 3.11, Flask 3.x, SQLite 3, Pandas 2.x, Bootstrap 5.3, Chart.js 4.x, Gunicorn, Docker Compose, Pytest
- **Primary Roles**: `admin`, `faculty`, `student`
- **Current Phase**: Phase 1 — Foundation & Authentication

---

## 2. Step-by-Step Execution Matrix

### Phase 1: Foundation & Authentication
- [x] **Step 1.1 (CA-01)**: Project Scaffolding & Environment Setup (`requirements.txt`, `.gitignore`, `.env.example`, skeleton `app.py`, test runner)
- [x] **Step 1.2 (CA-02)**: SQLite Schema & Synthetic Seed Data (`users`, `students`, `courses`, `enrollments`, `attendance`, `audit_logs`, FK enforcement)
- [x] **Step 1.3 (CA-03)**: Authentication & Session Lifecycle (`/login`, `/logout`, `check_password_hash`, generic errors)
- [x] **Step 1.4 (CA-04)**: Server-Side RBAC Helpers & Decorators (`@login_required`, `@role_required`, 403 error page)
- [x] **Step 1.5 (CA-05)**: Role-Aware Dashboards & Navigation (Dynamic navbar, Admin/Faculty/Student landing views)

### Phase 2: Academic Record Management
- [ ] **Step 2.1 (CA-06)**: Student Record Management (Admin list/add students, roll number uniqueness)
- [ ] **Step 2.2 (CA-07)**: Course Catalogue Management (Admin/Faculty course view, course code uniqueness)
- [ ] **Step 2.3 (CA-08)**: Student-Course Enrollment Mapping (Composite PK, course rosters)

### Phase 3: Attendance Engine & Analytics
- [ ] **Step 3.1 (CA-09)**: Attendance Entry UI & Backend (Faculty course/date marking, atomic transactions)
- [ ] **Step 3.2 (CA-10)**: Student Personal Attendance View & Privacy (Row-level isolation, zero cross-student leakage)
- [ ] **Step 3.3 (CA-11)**: Attendance Aggregation Service with Pandas (Summary stats, percentages, zero-handling)
- [ ] **Step 3.4 (CA-12)**: Visual Analytics Dashboard with Chart.js (KPI cards, bar/line charts, accessible tables)

### Phase 4: Operations, Security & Persistence
- [ ] **Step 4.1 (CA-13)**: Scoped CSV Report Export (`/export/csv`, RFC 4180 escaping)
- [ ] **Step 4.2 (CA-14)**: System Audit Logging (`audit_logs` tracking, `/audit` admin view)
- [ ] **Step 4.3 (CA-15)**: Database Backup & Snapshot Download (`/backup` using `conn.backup()`)
- [ ] **Step 4.4 (CA-17)**: Dockerfile & Container Volume Persistence (Gunicorn + Compose named volume)
- [ ] **Step 4.5 (CA-18)**: Automated Route & Security Pytest Suite (Full negative & positive test matrix)
- [ ] **Step 4.6 (CA-19)**: Performance & Resource Footprint Benchmark (Latency & memory metrics)

### Phase 5: UI Polish, Accessibility & Final Submission
- [ ] **Step 5.1 (CA-16)**: Responsive Design System & Accessibility (WCAG 4.5:1 contrast, 8px grid, mobile responsiveness)
- [ ] **Step 5.2 (CA-20)**: Final README, Architecture Documentation & Viva Demo Evidence

---

## 3. Key Invariants & Rules
1. **Zero External Cloud Services**: Local SQLite 3 with WAL mode; no Firebase/AWS/Supabase.
2. **Foreign Key Enforcement**: `PRAGMA foreign_keys = ON;` on every DB connection.
3. **Row-Level Privacy**: Student queries MUST strictly filter `WHERE student_id = ?` from session.
4. **Parameterized SQL Only**: Use `?` placeholders; no string concatenation into SQL.
5. **Atomic Attendance Submissions**: Multi-row writes executed in explicit transactions.
6. **Synthetic Demo Data**: Fictional demo accounts and students only.

---

## 4. Current Work Log
- **Phase 1 Complete (Steps 1.1 through 1.5)**:
  - Scaffolding, pinned dependencies, environment configs, health endpoint.
  - SQLite schema (`schema.sql`) and lifecycle/seed module (`db.py`) with FK enforcement and synthetic data.
  - Authentication blueprint (`auth.py`) with secure PBKDF2/scrypt password hashing and session fixation mitigation.
  - Server-side RBAC decorators (`@login_required`, `@role_required`) protecting routes with HTTP 403 Forbidden.
  - Accessible role-aware UI dashboards for Admin, Faculty, and Student with row-level ownership isolation and custom styling (`style.css`).
  - Comprehensive Pytest test suite passing 17/17 tests.
- **Immediate Next Action**: Implement **Phase 2, Step 2.1 (CA-06)**: Student Record Management (`/students` list, search, and validation).
