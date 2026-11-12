# AttendX — Intelligent Attendance & Academic Analytics Platform

**Cloud Computing & Distributed Systems Capstone Project**  
*Cloud-Native Role-Governed Attendance Management, Distributed MapReduce Telemetry & Containerized Infrastructure*

---

## Table of Contents
1. [Overview](#overview)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Project Structure](#project-structure)
5. [Getting Started](#getting-started)
6. [Environment Variables](#environment-variables)
7. [CI/CD](#cicd)
8. [Docker & Cloud Deployment](#docker--cloud-deployment)

---

## Overview

**AttendX** is a cloud-native, role-governed academic platform engineered to demonstrate core principles of **Cloud Computational Services**, distributed batch processing, and 12-factor application architecture. Built for universities and enterprise institutions, AttendX replaces manual attendance logs and fragmented spreadsheets with a high-concurrency, containerized web system.

### Cloud Computational Principles Demonstrated
- **Distributed MapReduce Processing**: Real-time batch aggregation engine implementing functional `Mapper -> Shuffle & Sort -> Reducer` pipelines for multi-course and daily institutional attendance metrics.
- **Stateless Compute & Decoupled Storage**: Decoupled application tier managed by a production multi-worker WSGI server (Gunicorn) with persistent state isolated to named container storage volumes.
- **Multitenant Security & Row-Level Isolation**: Cryptographically enforced Role-Based Access Control (RBAC) and tenant privacy boundaries (`WHERE student_id = ?`) preventing unauthorized inter-student data leakage (IDOR mitigation).
- **Point-in-Time Cloud Snapshot Recovery**: Online zero-downtime database snapshot generation and one-click restore engine to ensure disaster recovery and high availability across cloud instances.
- **High-Throughput Telemetry**: Sub-millisecond container health monitoring probes (`/health`) and vectorized in-memory analytics (Pandas 2.x) serving responsive Chart.js visual telemetry.

---

## Key Features

- **Cloud MapReduce Aggregation Engine**:
  - Implements the distributed `MapReduce` paradigm with dedicated `mapper_course_totals`, `mapper_daily_totals`, and `mapper_student_totals` functional stages.
  - Intermediate key-value partition grouping via an in-memory `shuffle_and_sort` phase.
  - Parallel aggregation reducers producing total enrollments, presence counts, and exact turnout percentages in sub-millisecond execution times.
- **Role-Based Academic Portals (RBAC)**:
  - **Administrator Console**: Full institutional governance, student & faculty directory provisioning, custom credential creation/reset, course catalogue administration, immutable audit logging, and automated database backups.
  - **Faculty Workspace**: Streamlined course attendance entry, batch student status toggles (Present/Absent), atomic SQLite transaction commits, and attendance telemetry.
  - **Student Self-Service Portal**: Secure, privacy-enforced dashboard showing personal turnout velocity, course-wise breakdowns, and academic standing alerts (Eligible, Borderline, At-Risk < 75%).
- **Governance, Security & Audit Traceability**:
  - Salting and cryptographic password hashing via `Werkzeug` PBKDF2/scrypt.
  - Immutable system-wide audit ledger recording all administrative, faculty, and authentication events with actor attribution and IP tracking.
- **Obsidian Black Mirror UI & Generative 3D Canvas**:
  - Interactive WebGL 3D dynamic neon canvas with real-time mouse tracking and color randomization.
  - Accessible, WCAG-compliant design tokens with auto-switching dark/light transparent branding assets (`attendx-icon.png`, `attendx-wordmark.png`).

---

## System Architecture

```
                                  +---------------------------------------+
                                  |       Client Web Browser              |
                                  | (HTML5 + Tailwind/Obsidian + WebGL)   |
                                  +-------------------+-------------------+
                                                      |
                                                      | HTTP / HTTPS (Port 5000)
                                                      v
                                  +---------------------------------------+
                                  |     Reverse Proxy / Cloud Gateway     |
                                  |          (Nginx / Cloud Load Balancer)|
                                  +-------------------+-------------------+
                                                      |
                                                      | WSGI Interface
                                                      v
      +-----------------------------------------------------------------------------------+
      |                        Docker Container (cloudattend_app)                         |
      |                                                                                   |
      |   +---------------------------------------------------------------------------+   |
      |   |                      Gunicorn WSGI Master Process                         |   |
      |   |            +------------------------------+------------------------------+ |   |
      |   |            | Worker Process 1 (Flask App) | Worker Process 2 (Flask App) | |   |
      |   |            +------------------------------+------------------------------+ |   |
      |   +-------------------------------------+-------------------------------------+   |
      |                                         |                                         |
      |               +-------------------------+-------------------------+               |
      |               |                                                   |               |
      |               v                                                   v               |
      |   +-----------------------+                           +-----------------------+   |
      |   |    Flask Core App     |                           |   Cloud MapReduce     |   |
      |   | - Session & Auth RBAC |                           |   Distributed Engine  |   |
      |   | - Student & Faculty   |                           | - Mapper Stages       |   |
      |   | - Atomic Transactions |                           | - Shuffle & Sort      |   |
      |   | - Health Probe API    |                           | - Reducer Aggregators |   |
      |   +-----------+-----------+                           +-----------+-----------+   |
      |               |                                                   |               |
      |               +-------------------------+-------------------------+               |
      |                                         |                                         |
      +-----------------------------------------|-----------------------------------------+
                                                |
                                                | Direct I/O (WAL Mode)
                                                v
                              +-----------------------------------+
                              |       Persistent Storage Layer    |
                              | Docker Named Volume Mount         |
                              | (`cloudattend_sqlite_data` mount) |
                              | File: /app/instance/cloudattend.db|
                              +-----------------------------------+
```

### Architectural Layering
1. **Presentation Tier**: Responsive HTML5, Tailwind CSS, Lucide icons, and Chart.js dashboards rendering client-side telemetry.
2. **Application & Compute Tier**: Containerized Flask 3.0.3 execution runtime managed by Gunicorn workers running Python 3.11-slim.
3. **Analytics Engine Tier**: Hybrid data plane combining in-memory Pandas 2.x vectorized aggregations with a custom MapReduce distributed compute engine.
4. **Persistence Tier**: SQLite 3 configured with Write-Ahead Logging (`PRAGMA journal_mode = WAL;`) and immediate transaction locking, mounted to a persistent Docker named volume.

---

## Project Structure

```text
student_attendance_system/
├── api/                             # Modular REST API endpoints and blueprint routes
│   └── __init__.py
├── instance/                        # Persistent database storage mount directory
│   └── cloudattend.db               # SQLite 3 relational database
├── static/                          # Static assets and frontend styling
│   ├── css/
│   │   ├── attendx-login.css        # High-fidelity glassmorphism login styling
│   │   └── style.css                # Base portal styles
│   └── images/
│       ├── attendx-icon.png         # Transparent logo icon (dark/light neutral)
│       ├── attendx-wordmark.png     # Transparent wordmark (dark mode)
│       └── attendx-wordmark-light.png # Transparent wordmark (light mode)
├── templates/                       # Jinja2 Obsidian Black Mirror UI templates
│   ├── obsidian_base.html           # Unified Obsidian master shell with role navigation
│   ├── obsidian_admin_base.html     # Administrative shell extension
│   ├── admin_dashboard.html         # Administrator Overview & operations ledger
│   ├── faculty_dashboard.html       # Faculty teaching console & turnout metrics
│   ├── student_dashboard.html       # Student self-service dashboard (isolated privacy)
│   ├── obsidian_attendance.html     # Class attendance entry (dual grid/list view)
│   ├── obsidian_courses.html        # Course catalogue & enrollment management
│   ├── obsidian_analytics.html      # Chart.js analytics & MapReduce aggregation engine
│   ├── teachers.html                # Administrator faculty directory & credential management
│   ├── students.html                # Administrator student directory & credential management
│   ├── audit.html                   # Governance & audit traceability log
│   ├── backup.html                  # Database snapshot download & 1-click restore
│   └── login.html                   # Interactive 3D WebGL Sign-In page
├── tests/                           # Pytest automated test suite (58 tests)
│   ├── test_academic_records.py     # Student & Course CRUD operations tests
│   ├── test_admin_phase1.py         # Admin portal, teachers directory & RBAC tests
│   ├── test_app.py                  # Health check, config & branding tests
│   ├── test_attendance_and_analytics.py # Attendance submission & MapReduce unit tests
│   ├── test_auth.py                 # Authentication, logout & RBAC security tests
│   ├── test_db.py                   # Schema constraints & foreign key tests
│   ├── test_faculty_phase2.py       # Faculty portal & course roster tests
│   ├── test_operations_and_security.py # Audit logging & backup snapshot tests
│   ├── test_performance.py          # High-precision latency benchmarks
│   └── test_student_phase3.py       # Student privacy isolation & standing calculation tests
├── analytics_service.py             # Pandas in-memory vectorized analytics service
├── app.py                           # Application entry point & core route controllers
├── auth.py                          # Session authentication & @role_required RBAC decorators
├── db.py                            # SQLite database connection & seed initialization
├── mapreduce_engine.py              # Cloud MapReduce distributed aggregation engine
├── schema.sql                       # Relational DDL schema & table constraints
├── Dockerfile                       # Multi-stage production container definition
├── docker-compose.yml               # Multi-container orchestration & volume definition
├── render.yaml                      # Declarative Cloud PaaS deployment blueprint
├── vercel.json                      # Serverless cloud configuration
├── requirements.txt                 # Pinned application dependencies
├── pytest.ini                       # Test suite discovery configuration
├── .env.example                     # Environment configuration template
└── README.md                        # Project documentation
```

---

## Getting Started

### Prerequisites
- **Python**: Version `3.11.x`
- **Docker & Docker Compose** (for containerized execution)
- **Git**

### Local Development Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ADITYAGUPTA112/student_attendance_system.git
   cd student_attendance_system
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   # Linux / macOS:
   python3 -m venv .venv
   source .venv/bin/activate

   # Windows (PowerShell):
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Initialize and Seed the Database**:
   ```bash
   flask init-db --seed
   ```

5. **Start the Development Server**:
   ```bash
   python app.py
   ```
   Access the portal at `http://localhost:5000`.

### Running Automated Test Suite
AttendX includes **58 comprehensive automated tests** validating RBAC security, MapReduce correctness, student privacy isolation, and sub-millisecond response benchmarks.
```bash
pytest -v
```

---

## Environment Variables

AttendX adheres to 12-Factor App design principles by externalizing configuration into environment variables. Configure these variables in a local `.env` file or within your cloud provider's secret management console:

| Variable Name | Required | Default Value | Description |
| :--- | :---: | :--- | :--- |
| `FLASK_APP` | Yes | `app.py` | Python application module entry point. |
| `FLASK_ENV` | No | `production` | Runtime mode (`development` or `production`). |
| `SECRET_KEY` | Yes | *Required in Prod* | Cryptographic key used for session cookie signing. |
| `DATABASE_PATH` | No | `instance/cloudattend.db` | Absolute or relative file path to the SQLite relational database. |
| `PORT` | No | `5000` | Port bound by the Gunicorn web server or Flask development server. |
| `PYTHONUNBUFFERED` | No | `1` | Forces real-time container log streaming without stdout buffer delay. |
| `PYTHONDONTWRITEBYTECODE` | No | `1` | Prevents Python from writing `.pyc` files inside ephemeral containers. |

---

## CI/CD

AttendX implements an automated Continuous Integration and Continuous Deployment (CI/CD) delivery model designed for cloud reliability:

```
+------------------+      +--------------------+      +--------------------+      +--------------------+
|   Code Commit    | ---> |    Automated CI    | ---> |  Container Build   | ---> |  Cloud Deployment  |
| (Feature Branch) |      | (58 Pytest Tests)  |      |  (Docker Image)    |      | (Render / Cloud VM)|
+------------------+      +--------------------+      +--------------------+      +--------------------+
```

### Pipeline Stages
1. **Continuous Integration (Build & Verify)**:
   - Automated environment bootstrapping on Python 3.11.
   - Pinned dependency installation with integrity checking (`requirements.txt`).
   - Execution of the full test suite (`pytest -v`):
     - **Authentication & RBAC**: Strict verification that student accounts receive HTTP 403 on administrative routes.
     - **Multi-Tenant Privacy**: Verification of tenant row-level data isolation (`WHERE student_id = ?`).
     - **MapReduce Accuracy**: Functional validation of mapper, shuffler, and reducer output.
     - **Performance Benchmarks**: Latency assertion ensuring critical endpoints respond under strict thresholds.
2. **Container Image Packaging**:
   - Automated Docker build packaging the lightweight `python:3.11-slim` runtime.
   - Non-root instance directory provisioning and security hardening.
3. **Continuous Deployment (CD)**:
   - Declarative deployment via `render.yaml` triggering zero-downtime rolling deploys upon Git push to `main`.
   - Healthcheck probing (`/health`) validating container readiness before traffic routing.

---

## Docker & Cloud Deployment

### Multi-Stage Container Architecture
The platform is containerized using Docker to achieve complete environment parity across development, staging, and cloud production environments.

#### Dockerfile Overview
- **Base Image**: `python:3.11-slim` (minimal security attack surface).
- **Embedded Health Probe**: Docker `HEALTHCHECK` queries the `/health` endpoint every 30 seconds with a 5-second timeout.
- **Production Server**: 2 Gunicorn worker processes bound to `0.0.0.0:5000`.

### Running with Docker Compose

To build and start the containerized service with automatic persistent volume binding:

```bash
# Build and launch in detached mode
docker compose up -d --build

# View container logs in real time
docker compose logs -f

# Verify container health status
docker ps --filter "name=cloudattend_app"

# Stop and gracefully terminate containers
docker compose down
```

### Persistent Volume Architecture
SQLite state is preserved across container restarts, image updates, and host reboots via the named Docker volume:
```yaml
volumes:
  - cloudattend_data:/app/instance
```
The named volume `cloudattend_sqlite_data` ensures that user credentials, student rosters, and attendance records remain durable and independent of ephemeral container lifecycles.

### Cloud Platform Deployment Options
- **Docker Compose / Cloud VM (AWS EC2, GCP Compute Engine, Azure VM)**: Run via `docker compose up -d` behind an Nginx or cloud application load balancer.
- **Managed PaaS (Render / Railway)**: Deploy directly using the provided `render.yaml` infrastructure-as-code blueprint with automated SSL termination and continuous git deployment.
