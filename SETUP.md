# 🚀 AttendX - Quick Setup & Installation Guide

Welcome to **AttendX** (Intelligent Attendance & Academic Analytics Platform). Follow this simple guide to run the project on your local machine in under **2 minutes**.

---

## 📋 Prerequisites
Before starting, ensure your system has:
1. **Python 3.10, 3.11, or 3.12** installed on your PC.  
   *(⚠️ Important: During Python installation on Windows, ensure the box **"Add Python to PATH"** is checked!)*
2. **Git** (optional, if cloning via GitHub).

---

## ⚡ Method 1: Quick Setup with Python (Recommended)

### Step 1: Open Terminal in Project Folder
Open **PowerShell**, **Command Prompt (CMD)**, or **VS Code Terminal** inside the `student_attendance_system` folder.

### Step 2: Create a Virtual Environment
```bash
python -m venv .venv
```

### Step 3: Activate the Virtual Environment
* **On Windows (PowerShell / CMD)**:
  ```powershell
  .\.venv\Scripts\activate
  ```
  *(If PowerShell shows an execution policy error, see Troubleshooting below).*

* **On macOS / Linux**:
  ```bash
  source .venv/bin/activate
  ```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Initialize Database & Sample Data
```bash
flask init-db --seed
```

### Step 6: Start the Application!
```bash
python app.py
```

### Step 7: Open in Browser
Open your browser and navigate to:  
👉 **[http://localhost:5000](http://localhost:5000)** (or `http://127.0.0.1:5000`)

---

## 🐳 Method 2: One-Click Setup with Docker

If you have **Docker Desktop** installed on your PC, you can run the entire project with a single command:

```bash
docker compose up --build
```
Once started, visit: **[http://localhost:5000](http://localhost:5000)**.

---

## 🔑 Demo Login Accounts

Use these pre-configured accounts to explore different roles and portals:

| Role | Username | Password | Features to Explore |
| :--- | :--- | :--- | :--- |
| **🛡️ Administrator** | `admin` | `adminpassword` | Create new teachers & students, reset passwords, view audit logs, create database backups. |
| **👨‍🏫 Teacher (Faculty)** | `prof_sharma` | `password123` | Select a course, mark attendance atomically (`Present`/`Absent`/`Late`), view records. |
| **🎓 Student** | `2024CS001` | `password123` | View personal attendance percentage, course breakdown, and attendance status alerts. |

---

## 🧪 Verify Your Setup (Run Automated Tests)

AttendX includes a comprehensive automated test suite. To verify that everything is running correctly on your computer:

```bash
pytest -v
```
*(You will see all **58 tests pass** with a 100% success rate!)*

---

## 🛠️ Common Troubleshooting & FAQs

### Q1: PowerShell error: *"running scripts is disabled on this system"*?
**Solution**: Run this command in your PowerShell window, then try activating again:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\activate
```

### Q2: *"python is not recognized as an internal or external command"*?
**Solution**: Python was not added to your Windows PATH. 
1. Re-run the Python installer, select **Modify**, and check **"Add Python to PATH"**.
2. Or use the full path to python (e.g., `C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python311\python.exe -m venv .venv`).

### Q3: Port 5000 is already in use?
**Solution**: Run the application on an alternate port:
```bash
flask run --port=5001
```
And access it at `http://localhost:5001`.

---

🎉 **You are all set! Enjoy using AttendX.**
