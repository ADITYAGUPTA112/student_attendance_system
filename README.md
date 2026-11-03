# CloudAttend — Intelligent Student Attendance & Analytics Platform

**ENSP401 – Cloud Computing Capstone Project**  
*Role-Based Academic Attendance Management, Statistical Reporting & Privacy-Enforced Self-Service*

---

## Overview
**CloudAttend** is a role-governed web application built for educational institutions to eliminate paper registers and disconnected spreadsheets. It provides:
- **Administrators**: Comprehensive record management, audit tracking, and database backup utilities.
- **Faculty**: Streamlined, fast attendance marking per course and date, with atomic database writes.
- **Students**: Strict row-level privacy self-service dashboards to inspect attendance history and percentages.
- **Analytics Engine**: Real-time aggregation via Pandas and visual interactive charts via Chart.js.

---

## Technical Stack
- **Backend**: Python 3.11, Flask 3.x
- **WSGI Server**: Gunicorn
- **Database**: SQLite 3 (with `PRAGMA foreign_keys = ON;`)
- **Data Analytics**: Pandas 2.x
- **Frontend**: HTML5, CSS3, Bootstrap 5.3.x, Chart.js 4.x
- **Containerization**: Docker & Docker Compose
- **Testing**: Pytest

---

## Project Specification Documents
- [**`PRD.md`**](PRD.md) — Product Requirements Document (features, personas, user flows, success metrics).
- [**`Architecture.md`**](Architecture.md) — Technical architecture, database schema, route contracts, deployment topology.
- [**`Rules.md`**](Rules.md) — AI and engineering boundaries, security rules, parameterization, and validation policies.
- [**`Phases.md`**](Phases.md) — 5-phase, 20-step execution roadmap (CA-01 through CA-20).
- [**`Design.md`**](Design.md) — Frontend design tokens, color palette, typography, spacing rhythm, and UI components.
- [**`Memory.md`**](Memory.md) — Active context tracker, ticket checklist, and architectural invariants.

---

## Setup & Execution (Quickstart)

### Local Environment
```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database and start the app
python app.py
```

### Docker Compose
```bash
docker compose up -d --build
```
Access the application at `http://localhost:5000`.
