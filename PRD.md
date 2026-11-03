# Product Requirements Document (PRD) — CloudAttend

## 1. Document Control & Overview
- **Product Name**: CloudAttend — Intelligent Student Attendance & Analytics Platform
- **Document Version**: 1.0
- **Academic Context**: ENSP401 – Cloud Computing Capstone Project
- **Product Stage**: Academic MVP / Prototype
- **Baseline Stack**: Python 3.11, Flask 3.x, SQLite 3, Pandas 2.x, HTML5/CSS3/Bootstrap 5.x, Chart.js 4.x, Docker & Docker Compose, Gunicorn, Pytest
- **Deployment Scope**: Local Docker containerized prototype (public cloud deployment is out of scope for MVP)
- **Data Policy**: Synthetic / fictional demo data only; no real personal data

---

## 2. Problem Statement
Academic institutions, departments, and teachers often record attendance in paper registers or disconnected spreadsheets. This workflow presents several critical issues:
- Retrieving historical attendance records is slow and manual.
- Calculating attendance percentages and generating compliance reports is labor-intensive and prone to arithmetic mistakes.
- Shared spreadsheets lack role boundaries, risking unauthorized edits, accidental deletions, or privacy leaks.
- Students lack immediate self-service visibility into their attendance records and risk falling below minimum attendance thresholds without warning.

---

## 3. Product Vision & Goals
### Vision
Deliver an intuitive, trustworthy, role-governed web application that streamlines classroom attendance recording and delivers real-time analytics to teachers, administrators, and students.

### Strategic Goals
1. **Efficiency**: Reduce time and manual effort required to record and aggregate class attendance.
2. **Consistency**: Provide faculty with a standardized, fast course/date attendance entry workflow.
3. **Transparency & Self-Service**: Give students a personal dashboard to inspect attendance percentages and course history.
4. **Administrative Control**: Enable administrators to manage academic records, review audit trails, and generate system backups.
5. **Portability**: Package the application into a containerized runtime with persistent storage suitable for local evaluation or future cloud migration.

---

## 4. Target Users & Personas

| Role | Profile & Key Tasks | Frustrations Addressed | Primary Screens |
| :--- | :--- | :--- | :--- |
| **Administrator / Office Staff** | Manages system records, student profiles, course catalogue, audit trails, and backups. | Manual record reconciliation, fragmented reports, lack of traceability. | Login, Admin Dashboard, Students, Courses, Audit Logs, Backup. |
| **Faculty Member** | Conducts classes, marks attendance per session, monitors class trends. | Cumbersome paper registers, slow calculations, accidental record overwrites. | Login, Faculty Dashboard, Attendance Marking, Course Analytics. |
| **Student** | Attends lectures, tracks personal attendance percentages and session records. | Lack of visibility into attendance status until end of term. | Login, Student Dashboard, Personal Attendance View. |

---

## 5. Core Features & Priorities

| Feature | Description | Priority |
| :--- | :--- | :--- |
| **Login / Logout** | Authenticate demo users against hashed credentials and maintain secure session cookies. | **MUST** |
| **Role-Based Access Control (RBAC)** | Enforce strict role boundaries (Admin, Faculty, Student) at the server route level. | **MUST** |
| **Student Record Management** | Admin can list and add student profiles with uniqueness and format validation. | **MUST** |
| **Course Catalogue** | Manage course codes and titles with uniqueness constraints. | **MUST** |
| **Attendance Entry** | Faculty selects course and date, then records `Present` or `Absent` for each student. | **MUST** |
| **Personal Student View** | Students can view only their own attendance records, summaries, and percentages. | **MUST** |
| **Attendance Analytics Engine** | Grouped aggregations (present/total counts, %) using Pandas; visual display via Chart.js. | **MUST** |
| **CSV Report Export** | Authorized roles can export attendance reports as formatted CSV files. | **SHOULD** |
| **Audit Logging** | Record key administrative and attendance modifications with actor, action, and timestamp. | **SHOULD** |
| **Database Backup & Download** | Admin can create and download a consistent snapshot of the SQLite database. | **SHOULD** |
| **Responsive UI Design** | Consistent layout across desktop and mobile screen viewports. | **SHOULD** |

---

## 6. MVP Definition
The CloudAttend MVP is the smallest coherent end-to-end release that demonstrates:
1. Secure role-specific authentication and authorization (Admin, Faculty, Student).
2. Administration of student and course entities.
3. Daily attendance entry for faculty.
4. Strict row-level privacy allowing students to access only their own records.
5. Aggregation calculations and browser chart visualizations.
6. Containerized execution via Docker Compose with volume-persisted SQLite database.

---

## 7. User Flows

### Flow A — Faculty Records Attendance
1. Faculty navigates to CloudAttend and logs in.
2. Lands on **Faculty Dashboard** and clicks **Take Attendance**.
3. Selects an assigned Course and Attendance Date (defaults to today, `YYYY-MM-DD`).
4. System displays the roster of enrolled students.
5. Faculty sets status (`Present` / `Absent`) for each student (defaults to `Present`).
6. Faculty submits form; server validates inputs in a single transaction.
7. Server responds with a success flash message and updated session summary.

### Flow B — Student Checks Attendance
1. Student logs in with student credentials.
2. Lands on **Student Dashboard**.
3. Sees overall attendance percentage, total classes held, and attended count.
4. Inspects course-by-course breakdown and date-stamped session log.
5. Queries strictly filter by session `student_id`; access to other students' data is blocked.

### Flow C — Administrator Oversees Operations
1. Administrator logs in.
2. Lands on **Admin Dashboard** with system-wide summary metrics.
3. Adds new students or courses with instant validation.
4. Inspects the **Audit Log** for operational accountability.
5. Generates a database snapshot under **Backup Management**.

---

## 8. Non-Goals (Deliberately Out of Scope for V1)
- Biometric, facial recognition, or RFID attendance hardware integration.
- GPS geofencing or classroom Bluetooth proximity detection.
- Fee collection, timetable scheduling, or exam grading modules.
- Third-party LMS / ERP integrations (Canvas, Blackboard, Moodle).
- SMS / WhatsApp / Email notification dispatch.
- Public cloud hosting claims (deliverable is a local Docker Compose setup).
- Real student personal identifying data.

---

## 9. Success Metrics
1. **Authentication Reliability**: Valid credentials authenticate reliably; invalid credentials fail generically.
2. **Data Integrity**: Attendance writes persist atomically; duplicate submissions on the same date are handled deterministically.
3. **Privacy Enforcement**: 100% pass rate on student data isolation tests (Student A cannot access Student B records via URL tampering).
4. **Accuracy**: Aggregation calculations (counts, percentages) match verified sample test calculations with zero division-by-zero errors.
5. **Persistence**: SQLite database data persists across Docker container stops and recreations when named volume is retained.

