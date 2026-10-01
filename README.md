# Online Examination and Result Management System 🎓
> A Complete, Test-Ready Web Application Built for Software Testing Engineering & Quality Assurance Demonstration

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.2-green.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://www.mysql.com/)
[![Selenium](https://img.shields.io/badge/Selenium-4.18.1-red.svg)](https://www.selenium.dev/)
[![Pytest](https://img.shields.io/badge/Pytest-8.0.2-yellow.svg)](https://docs.pytest.org/)

---

## 📌 Project Overview

This application is an end-to-end **Online Examination and Result Management System** designed specifically for academic software testing, manual QA, and automated regression testing demonstrations. 

### Key Features
- **Student Module**: Account registration, secure login, password reset (demo mode), student profile view, published exam catalog, interactive exam taking with live countdown timer, auto-submit on timeout, single attempt constraint enforcement, and instant scorecard calculation.
- **Admin Module**: Executive statistics dashboard, student account management (block/unblock/delete), course management (CRUD), exam creation with duration boundary enforcement (5 to 180 mins), MCQ question authoring with 4 options, exam publishing toggle, and student result management.
- **Security & Integrity**: Parameterized SQL queries via `mysql-connector-python`, `werkzeug` password hashing, RBAC session authorization decorators, and XSS input sanitization.
- **Automated Test Suite**: Full Page Object Model (POM) Selenium WebDriver + `pytest` suite with `pytest-html` report generation and automatic failure screenshot capture.

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, Vanilla JavaScript, Custom Glassmorphic Dark CSS Design System (No heavy JS frameworks for maximum testability).
- **Backend**: Python 3.9+ REST API with Flask & Flask-CORS.
- **Database**: MySQL 8.0+ / MariaDB / XAMPP (`mysql-connector-python` parameterized queries).
- **Test Automation**: Python `pytest`, Selenium WebDriver, `pytest-html`, `webdriver-manager`.

---

## 🚀 Quick Setup & Installation Guide

### Prerequisites
1. **Python 3.9 or higher** installed on your system.
2. **MySQL Server** (MySQL 8.0+, XAMPP, or MariaDB) running locally on port `3306`.

### Step 1: Install Python Dependencies
Open your terminal in the root directory of the project and execute:
```bash
py -m pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Verify `.env` configuration file in the project root:
```env
FLASK_ENV=development
SECRET_KEY=super-secret-exam-system-key-2026
PORT=5000
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=online_exam_db
DB_PORT=3306
```
*(Adjust `DB_PASSWORD` if your local MySQL instance requires a password).*

### Step 3: Initialize & Seed Database
Execute the database initialization script to create tables (`schema.sql`) and populate initial seed data (`seed.sql`):
```bash
py db/init_db.py
```

### Step 4: Run the Web Application
Start the Flask web server:
```bash
py app.py
```
Open your browser and navigate to: **`http://localhost:5000`**

---

## 🔑 Pre-Configured Test Credentials

| Role | Username | Password | Notes / Status |
|---|---|---|---|
| **Admin** | `admin` | `Admin@123` | System Administrator |
| **Sub-Admin** | `subadmin` | `Admin@456` | Academic Controller |
| **Active Student 1** | `alice1` | `Student@123` | Student ID: `STU001` (Course: SE301) |
| **Active Student 2** | `bob2` | `Student@123` | Student ID: `STU002` (Course: SE301) |
| **Blocked Student** | `charlie3` | `Student@123` | Student ID: `STU003` (Status: `blocked`) |

---

## 🧪 Automated Testing Suite Execution

The automated test suite uses **Selenium WebDriver**, **pytest**, and the **Page Object Model (POM)** pattern.

### Step 1: Ensure Server is Running
Before starting tests, make sure `py app.py` is running in a terminal window.

### Step 2: Run Pytest Automation Suite
In a second terminal window, run:
```bash
py -m pytest tests/ --html=report.html --self-contained-html
```

### Test Artifacts Generated:
- **`report.html`**: Comprehensive HTML execution report containing test status, execution time, and assertions.
- **`tests/screenshots/`**: Screenshots automatically captured for any failing test cases.

---

## 🐛 Bug-Injection Switch Guide (For QA Demos)

To demonstrate how the automated Selenium regression test suite catches software bugs, 3 clearly marked **Bug-Injection Spots** are provided in the codebase. By default, the codebase is 100% bug-free. You can toggle any of these switches to simulate software defects:

### 📍 Bug Spot 1: Boundary Value Analysis (BVA) Bypass
- **File**: [`utils/validators.py`](file:///c:/Users/anura/Downloads/Software%20Testing/utils/validators.py#L110)
- **Normal Code**:
  ```python
  if duration_val < 5 or duration_val > 180:
      errors["duration_minutes"] = "Exam duration must be between 5 and 180 minutes."
  ```
- **Bug Injection**: Comment out the `< 5` check:
  ```python
  # BUG INJECTION SPOT 1: Allows invalid 4-minute exams
  if duration_val > 180:
      pass
  ```
- **Regression Test Affected**: `TC-ADM-05` in `tests/test_admin.py` will fail, catching the defect!

---

### 📍 Bug Spot 2: Single-Attempt Constraint Bypass
- **File**: [`routes/student_routes.py`](file:///c:/Users/anura/Downloads/Software%20Testing/routes/student_routes.py#L65)
- **Normal Code**:
  ```python
  if existing_result and existing_result["is_submitted"] == 1:
      return jsonify({"status": "error", "message": "You have already attempted this exam."}), 403
  ```
- **Bug Injection**: Comment out the single attempt guard:
  ```python
  # BUG INJECTION SPOT 2: Allows students to re-attempt exams
  # if existing_result and existing_result["is_submitted"] == 1:
  #     return jsonify({"status": "error", "message": "Already attempted"}), 403
  ```
- **Regression Test Affected**: `TC-STU-05` in `tests/test_student.py` will fail!

---

### 📍 Bug Spot 3: Scoring Calculation Defect
- **File**: [`routes/student_routes.py`](file:///c:/Users/anura/Downloads/Software%20Testing/routes/student_routes.py#L140)
- **Normal Code**:
  ```python
  percentage = (score_obtained / total_possible_score * 100.0) if total_possible_score > 0 else 0.0
  ```
- **Bug Injection**: Introduce incorrect multiplier logic:
  ```python
  # BUG INJECTION SPOT 3: Miscalculates percentage
  percentage = (score_obtained / total_possible_score * 50.0)
  ```
- **Regression Test Affected**: `TC-STU-04` scorecard percentage assertion will fail!

---

## 📑 Software Testing Documentation & Artifacts

- [Phase 1 QA Report & Deliverables](file:///C:/Users/anura/.gemini/antigravity/brain/3d2a2a4b-0716-4aa5-b797-045960171d87/phase1_testing_deliverables.md)
- [Phase 2 QA Report & Admin Deliverables](file:///C:/Users/anura/.gemini/antigravity/brain/3d2a2a4b-0716-4aa5-b797-045960171d87/phase2_testing_deliverables.md)
- [Phase 3 QA Report & Student Deliverables](file:///C:/Users/anura/.gemini/antigravity/brain/3d2a2a4b-0716-4aa5-b797-045960171d87/phase3_testing_deliverables.md)
- [System Architecture Walkthrough](file:///C:/Users/anura/.gemini/antigravity/brain/3d2a2a4b-0716-4aa5-b797-045960171d87/walkthrough.md)
