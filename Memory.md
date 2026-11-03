# Project Memory & Progress Tracker — CloudAttend

## 1. Project Snapshot
- **Project Name**: CloudAttend — Intelligent Student Attendance & Analytics Platform
- **Course Context**: ENSP401 – Cloud Computing Capstone Project
- **Architecture Stack**: Python 3.11, Flask 3.x, SQLite 3, Pandas 2.x, Bootstrap 5.3, Chart.js 4.x, Gunicorn, Docker Compose, Pytest
- **Primary Roles**: `admin`, `faculty`, `student`
- **Current Status**: **ALL 5 PHASES / 20 TICKETS FULLY IMPLEMENTED & VERIFIED** (36/36 Pytest tests passing)

---

## 2. Step-by-Step Execution Matrix

### Phase 1: Foundation & Authentication (Sprint 1)
- [x] **Step 1.1 (CA-01)**: Project Scaffolding & Environment Setup (`requirements.txt`, `.gitignore`, `.env.example`, skeleton `app.py`, test runner)
- [x] **Step 1.2 (CA-02)**: SQLite Schema & Synthetic Seed Data (`users`, `students`, `courses`, `enrollments`, `attendance`, `audit_logs`, FK enforcement)
- [x] **Step 1.3 (CA-03)**: Authentication & Session Lifecycle (`/login`, `/logout`, `check_password_hash`, generic errors)
- [x] **Step 1.4 (CA-04)**: Server-Side RBAC Helpers & Decorators (`@login_required`, `@role_required`, 403 error page)
- [x] **Step 1.5 (CA-05)**: Role-Aware Dashboards & Navigation (Dynamic navbar, Admin/Faculty/Student landing views)

### Phase 2: Academic Record Management (Sprint 2)
- [x] **Step 2.1 (CA-06)**: Student Record Management (Admin list/add students, roll number uniqueness)
- [x] **Step 2.2 (CA-07)**: Course Catalogue Management (Admin/Faculty course view, course code uniqueness)
- [x] **Step 2.3 (CA-08)**: Student-Course Enrollment Mapping (Composite PK, course rosters)

### Phase 3: Attendance Engine & Analytics (Sprint 3)
- [x] **Step 3.1 (CA-09)**: Attendance Entry UI & Backend (Faculty course/date marking, atomic transactions)
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

### Phase 5: UI Polish, Accessibility & Final Submission (Sprint 5)
- [x] **Step 5.1 (CA-16)**: Responsive Design System & Accessibility (WCAG 4.5:1 contrast, 8px grid, mobile responsiveness)
- [x] **Step 5.2 (CA-20)**: Final README, Architecture Documentation & Viva Demo Evidence
- [x] **Step 5.3 (Stitch UI)**: Google Stitch MCP Integration & Modern UI Overhaul (Plus Jakarta Sans typography, deep navy header, segmented status controls, real-time roster counter, responsive KPI cards)
- [x] **Step 5.4 (Stitch Sunset Redesign)**: Premium Sunset Orange + Navy Blue Glassmorphism Login Gateway (`#101D3A`, `#FF9D32`, `#FF7628`, high-fidelity SVG campus architecture silhouette, ambient floating sunset particles, glowing glass login card with eye toggle, 1-click interactive demo accounts auto-fill)

---

## 3. Key Invariants & Architectural Rules
1. **Zero External Cloud Services**: Local SQLite 3 with WAL mode; zero dependency on Firebase, Supabase, or AWS for MVP.
2. **Foreign Key Enforcement**: `PRAGMA foreign_keys = ON;` executed on every single database connection.
3. **Row-Level Security**: Server query strictly injects `WHERE student_id = ?` using `session['student_id']`.
4. **Parameterized SQL Only**: Strict prohibition against SQL string concatenation (`?` placeholders used).
5. **Atomic Attendance Submissions**: Multi-row writes executed in explicit database transactions with rollback protection.
6. **No Real PII**: 100% synthetic demo records and test data.

---

## 4. Current Work Log
- **Phase 1 Complete**: Foundation, scaffolding, SQLite schema, authentication, RBAC decorators, role-aware dashboards.
- **Phase 2 Complete**: Student management, course catalogue, and student-course enrollment rosters.
- **Phase 3 Complete**: Daily attendance entry with atomic transactions, student self-service dashboard, Pandas aggregation engine, Chart.js visual charts.
- **Phase 4 Complete**: CSV report export, audit log inspection, SQLite online snapshot backup and download, Dockerfile & Docker Compose with persistent volume, comprehensive security and route tests.
- **Phase 5 Complete**: Custom Design System (`style.css`), benchmark latency testing (0.44ms health, 27.85ms analytics), comprehensive evaluation runbook in `README.md`.
- **Google Stitch UI Complete**: Generated modern interface designs via Stitch MCP project (`projects/17369063258270635857`), extracted UI tokens, and updated attendance entry, admin, and student dashboards with live status badges, segmented controls, and client-side filtering.
- **All 36 Pytest tests passing**: 100% test pass rate.
