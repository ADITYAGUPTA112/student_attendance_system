# Engineering Rules & AI Boundaries — CloudAttend

## 1. Core Directives
These rules are non-negotiable architectural and engineering boundaries. Every feature, refactoring, and code change must strictly comply with them.

---

## 2. Technology & Library Boundaries

### Allowed Technologies
- **Python**: 3.11+
- **Backend Framework**: Flask 3.x with Jinja2 templates
- **Database**: SQLite 3 using standard library `sqlite3`
- **Data Analytics**: Pandas 2.x
- **Frontend**: HTML5, CSS3, Bootstrap 5.3.x, Chart.js 4.x
- **Containerization**: Docker, Dockerfile, Docker Compose
- **WSGI Server**: Gunicorn (in Docker container)
- **Testing**: Pytest 8.x

### Prohibited Technologies
- **NO Heavy ORMs**: Do NOT introduce SQLAlchemy or Django ORM. Use explicit, parameterized SQL queries via `sqlite3` to maintain transparency and direct control over foreign keys and indexes.
- **NO Third-Party Cloud Services**: Do NOT introduce Firebase, AWS DynamoDB, Supabase, Auth0, Stripe, Twilio, SendGrid, or external AI/LLM API calls.
- **NO Client-Side Only Authorization**: Do NOT rely on JavaScript or hiding CSS elements to enforce security. Server-side checks are strictly mandatory.

---

## 3. Security & Access Rules

### 1. Server-Side Role Enforcement
- Every non-public route must verify authentication via Flask session.
- Role checks (`admin`, `faculty`, `student`) must be validated in python decorators or helper functions before executing route handlers.
- Unauthorized access must immediately return `HTTP 403 Forbidden` or redirect to login.

### 2. Row-Level & Ownership Isolation
- SQLite has no built-in Row-Level Security (RLS). Flask must enforce ownership inside query clauses.
- **Student Privacy**: When a student accesses attendance data, the query MUST filter by `student_id = :session_student_id`.
- **Never Trust Client-Supplied Identifiers**: Never allow a student or faculty member to pass `?student_id=X` in a URL or payload to access another user's records.

### 3. Parameterized SQL Queries Only
- Every SQL query incorporating dynamic parameters must use SQLite query parameter placeholders (`?`).
- **Never concatenate or format strings into SQL queries**:
  ```python
  # CORRECT:
  cursor.execute("SELECT * FROM students WHERE roll_no = ?", (roll_no,))

  # FORBIDDEN:
  cursor.execute(f"SELECT * FROM students WHERE roll_no = '{roll_no}'")
  ```

### 4. Password Security
- Never store raw or plaintext passwords.
- Use `werkzeug.security.generate_password_hash` and `werkzeug.security.check_password_hash` (using PBKDF2/scrypt).
- On login success, regenerate/refresh session to mitigate session fixation.
- Generic login error message must always be: `"Invalid username or password."` (never reveal whether a username exists).

### 5. Secrets & Environment
- Never hardcode production secrets, passwords, or encryption keys in source files or git history.
- Read `SECRET_KEY` from environment variables, with a safe fallback only in local debug/testing mode.

---

## 4. Data Integrity & Validation Rules

### 1. Foreign Key Enforcement
- SQLite connections disable foreign keys by default.
- Every database connection initialized in the application MUST execute:
  ```python
  conn.execute("PRAGMA foreign_keys = ON;")
  ```

### 2. Allow-List Input Validation
- **Attendance Status**: Strictly allowed values are `'Present'` and `'Absent'`. Any other status must be rejected with validation errors.
- **Dates**: Normalize all dates to ISO 8601 string format: `YYYY-MM-DD`. Disallow invalid dates.
- **Text Fields**: Strip leading and trailing whitespace. Reject inputs that consist solely of whitespace.

### 3. Atomic Multi-Row Operations
- Submitting attendance for an entire classroom writes multiple student rows.
- This submission MUST be executed within a single database transaction (`BEGIN TRANSACTION` / `COMMIT`). If any row fails, the entire batch must rollback.

### 4. Synthetic Demo Data Policy
- Never use real student names, genuine email addresses, or actual institutional identifiers.
- Seed data must be synthetic, deterministic, and safe for public academic demonstration.

---

## 5. Error Handling & Logging Rules

### 1. Information Disclosure Prevention
- In production mode (`FLASK_ENV=production`), never display raw Python stack traces, file system paths, or SQL queries to end users.
- Present clean, human-readable error pages for 400, 403, 404, and 500 errors.

### 2. Audit Trail Discipline
- Critical events to log in `audit_logs`:
  - User login / logout
  - New student or course creation
  - Attendance submission and updates
  - Database backup generation
- Never log passwords, raw session cookies, or secret tokens into audit records or console outputs.

---

## 6. Development & AI Workflow Rules

1. **Incremental Ticket Implementation**: Implement one feature ticket at a time as outlined in `Phases.md`.
2. **Preserve Working Code**: Inspect existing code before modifying. Never overwrite working features with untested rewrites.
3. **Automated Test Requirement**: Any route or logic modification must be accompanied or validated by a Pytest test case in `tests/test_app.py`.
4. **Update `Memory.md`**: Whenever a ticket is completed, record the change, passing tests, and updated status in `Memory.md`.

