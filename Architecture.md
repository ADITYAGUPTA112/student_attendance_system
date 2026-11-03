# Technical Architecture Document — AttendX

## 1. Architecture Overview
AttendX follows a classic layered, server-rendered web architecture.
- **Client Tier**: Web browser rendering server-generated HTML5 with Bootstrap 5.x styling and Chart.js 4.x for client-side analytics rendering.
- **Application Tier**: Python 3.11 with Flask 3.x providing session-based authentication, role-based authorization, route handling, input validation, and business logic.
- **Analytics Tier**: Pandas 2.x for tabular data processing, aggregation, grouping, and percentage computations.
- **Data Tier**: SQLite 3 relational database running in WAL mode with active foreign key enforcement (`PRAGMA foreign_keys = ON`).
- **Container / Deployment Tier**: Docker Engine & Docker Compose with Gunicorn WSGI server and a named persistent volume for SQLite storage.

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

---

## 2. Technology Stack

| Layer | Component | Version / Baseline | Justification |
| :--- | :--- | :--- | :--- |
| **Language** | Python | 3.11 | Modern typing, high performance, broad ecosystem support. |
| **Web Framework** | Flask | 3.x | Lightweight, explicit routing, flexible template integration. |
| **WSGI Server** | Gunicorn | 21.x / 22.x | Production-grade WSGI server for container deployment. |
| **Database** | SQLite 3 | Embedded | Zero-configuration, file-based relational store suitable for MVP. |
| **Data Analysis** | Pandas | 2.x | High-performance tabular aggregation and grouping logic. |
| **Styling & UI** | Bootstrap | 5.3.x | Clean, responsive grid, accessible UI components. |
| **Charting** | Chart.js | 4.x | Fast, canvas-rendered responsive client-side data visualization. |
| **Containerization**| Docker & Compose | Engine 24+ | Hermetic, reproducible environment with volume persistence. |
| **Testing** | Pytest | 8.x | Robust test runner for unit, integration, and security checks. |

---

## 3. Directory & File Structure

```text
Student_Attendance_System/
├── app.py                     # Main Flask application entrypoint & route definitions
├── requirements.txt           # Pinned Python package dependencies
├── Dockerfile                 # Container build instructions
├── docker-compose.yml         # Container service and persistent volume definition
├── .dockerignore              # Exclusions for container builds
├── .gitignore                 # Version control exclusions (instance/, __pycache__, etc.)
├── .env.example               # Template for required environment variables
├── README.md                  # Setup, operational instructions, and documentation
├── PRD.md                     # Product requirements document
├── Architecture.md            # System architecture and data models
├── Rules.md                   # Engineering boundaries and coding rules
├── Phases.md                  # Project delivery milestones and ticket breakdown
├── Design.md                  # UI/UX design tokens, layout, and component guide
├── Memory.md                  # AI implementation state and progress tracking
├── instance/                  # Local runtime data directory (contains SQLite database; gitignored)
├── static/
│   ├── css/
│   │   └── style.css          # Custom styling and design tokens
│   └── js/
│       └── charts.js          # Chart.js initialization logic
├── templates/
│   ├── base.html              # Shared base layout with navbar and flash messages
│   ├── login.html             # Authentication login screen
│   ├── dashboard.html         # Administrator & staff overview dashboard
│   ├── faculty_dashboard.html # Faculty course dashboard
│   ├── student_dashboard.html # Student self-service dashboard
│   ├── students.html          # Student management and registration table
│   ├── courses.html           # Course catalogue management
│   ├── attendance.html        # Daily attendance entry and submission form
│   ├── analytics.html         # Visual analytics, KPIs, and charts
│   ├── audit.html             # System audit log viewer
│   └── error.html             # Generic error template (403, 404, 500)
└── tests/
    ├── conftest.py            # Pytest fixtures, test database setup, and mock clients
    └── test_app.py            # Route, authorization, calculation, and security test suite
```

---

## 4. Database Schema Design (SQLite 3)

Foreign key enforcement is mandatory on every SQLite database connection:
```sql
PRAGMA foreign_keys = ON;
```

### Table Definitions

#### `users`
Stores authentication credentials and roles.
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'faculty', 'student')) NOT NULL,
    student_id INTEGER NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL
);
```

#### `students`
Stores student academic profiles.
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `courses`
Stores academic course offerings.
```sql
CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `enrollments`
Many-to-many relationship linking students to courses.
```sql
CREATE TABLE enrollments (
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);
```

#### `attendance`
Individual attendance event per student, course, and date.
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    attendance_date DATE NOT NULL,
    status TEXT CHECK(status IN ('Present', 'Absent')) NOT NULL,
    marked_by INTEGER NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (student_id, course_id, attendance_date),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (marked_by) REFERENCES users(id) ON DELETE RESTRICT
);
```

#### `audit_logs`
System activity tracking for critical administrative and modification events.
```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NULL,
    action TEXT NOT NULL,
    detail TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);
```

---

## 5. API & Route Baseline Contract

| Route | Method | Purpose | Role Authorization |
| :--- | :--- | :--- | :--- |
| `/login` | `GET`, `POST` | Render login form / authenticate session | Public |
| `/logout` | `GET` | Terminate session and redirect to `/login` | Authenticated |
| `/` | `GET` | Role-aware landing routing to appropriate dashboard | Authenticated |
| `/dashboard` | `GET` | Admin / Faculty primary overview | Admin, Faculty |
| `/student/dashboard` | `GET` | Student personal attendance dashboard | Student |
| `/students` | `GET`, `POST` | List all students / Register new student | Admin |
| `/courses` | `GET`, `POST` | List courses / Add new course | Admin (Write), Faculty (Read) |
| `/attendance` | `GET`, `POST` | Load roster for date / Submit daily attendance | Faculty, Admin |
| `/analytics` | `GET` | Aggregated attendance statistics & charts | Admin, Faculty, Student (scoped) |
| `/export/csv` | `GET` | Download scoped attendance report as CSV | Admin, Faculty |
| `/audit` | `GET` | View administrative audit log | Admin |
| `/backup` | `GET` | Create and download consistent SQLite backup | Admin |
| `/health` | `GET` | Application health and liveness check | Public |

---

## 6. Environment & Configuration

| Variable | Default Value | Required in Production | Purpose |
| :--- | :--- | :--- | :--- |
| `SECRET_KEY` | `dev-secret-key-change-in-prod` | Yes | Secures Flask signed session cookies. |
| `DATABASE_PATH` | `instance/cloudattend.db` | No | Absolute or relative path to SQLite database. |
| `FLASK_ENV` | `production` | Yes | Controls debug mode; debug must be off in production. |
| `PORT` | `5000` | No | Port on which the Gunicorn server listens. |

