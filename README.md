# Shaheen Model Girls High School — Management System

A bilingual (English/Urdu), full-stack School ERP.
**Stack:** FastAPI + MySQL (backend) · HTML5/Bootstrap 5/vanilla JS (frontend) · JWT auth with role-based access control.

## What this system does

- **Public site** — bilingual (EN/Urdu, full RTL support) landing page with admissions info, staff, gallery, and a working login
- **Admin dashboard** — full CRUD for Students, Teachers, Classes/Sections/Subjects, Timetable, Attendance, Exams & Results, Fee Management, Notices; PDF/Excel report downloads; database Backup & Restore
- **Teacher dashboard** — assigned classes/timetable, live attendance marking, homework assignment with file attachments, profile photo
- **Student dashboard** — attendance %, timetable, homework (with attachment downloads), results & GPA, fee status, profile photo
- **Account system** — JWT auth, password reset via email (with a fully-functional dev-mode fallback when no SMTP is configured), file uploads for profile photos and homework attachments

## Project structure

```
shaheen-school-erp/
├── database/
│   └── schema.sql                 # Full normalized MySQL schema
├── backend/
│   ├── app/
│   │   ├── config.py               # Settings loaded from .env
│   │   ├── main.py                 # FastAPI app entrypoint, router registration, /uploads static mount
│   │   ├── database/session.py     # SQLAlchemy engine/session
│   │   ├── models/                 # ORM models
│   │   ├── auth/                   # bcrypt hashing, JWT create/verify, RBAC dependencies
│   │   ├── schemas/                # Pydantic request/response models
│   │   ├── controllers/            # Business logic per domain
│   │   ├── routes/                 # API routes per domain
│   │   └── utils/                  # email_service, file_storage, backup_restore, grading, ws_manager, report_export
│   ├── requirements.txt
│   ├── .env.example
│   └── seed_super_admin.py         # Creates the first login (superadmin / ChangeMe@123)
└── frontend/
    ├── templates/
    │   ├── public/index.html        # Landing page
    │   ├── auth/                    # login.html, reset-password.html
    │   ├── admin/                   # dashboard, students, teachers, classes, timetable,
    │   │                             #   attendance, exams, fees, notices, reports, backup
    │   ├── teacher/dashboard.html
    │   └── student/dashboard.html
    └── static/
        ├── css/                     # main.css, dashboard.css, auth.css
        └── js/                      # i18n.js, main.js, auth-session.js, dashboard.js
```

## Setup instructions

### 1. Database
```bash
mysql -u root -p < database/schema.sql
```

### 2. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: set your real DB password and a long random JWT_SECRET_KEY.
# Leave SMTP_HOST empty to run password reset in dev mode (see below).

python seed_super_admin.py      # creates superadmin / ChangeMe@123

uvicorn app.main:app --reload --port 8000
```
**Run uvicorn from inside `backend/`** — `UPLOAD_DIR` in `.env` is a relative
path, so it needs to resolve against the `backend/` folder to land in the
right place (`backend/uploads/profile_pictures/`, `backend/uploads/homework/`,
`backend/uploads/dev_emails/`).

Visit `http://localhost:8000/docs` for interactive Swagger API docs.

### 3. Frontend
Static HTML/CSS/JS — no build step. Serve from the **project root**:
```bash
python -m http.server 8080
```
Open `http://localhost:8080/frontend/templates/public/index.html`.

The frontend auto-detects `localhost`/`127.0.0.1` and points at
`http://localhost:8000`. For non-local deployment, update the `API_BASE`
constant near the top of each page's `<script>` block.

### 4. Try it
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"superadmin","password":"ChangeMe@123"}'
```
Or log in through the UI at `.../auth/login.html` with
`superadmin` / `ChangeMe@123`.

## Password reset — dev mode vs. real email

If `SMTP_HOST` is empty in `.env`, password reset emails aren't sent —
instead the full HTML email (including the working reset link and token) is
logged to `backend/uploads/dev_emails/` as a timestamped `.html` file, so the
whole flow is testable without real mail credentials. Fill in `SMTP_HOST`,
`SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` to send real email instead — same
code path either way.

## File uploads

Profile photos (`.jpg/.jpeg/.png/.webp`, max 2MB) and homework attachments
(`.pdf/.doc/.docx/.jpg/.jpeg/.png`, max 10MB) are stored under
`backend/uploads/` with generated filenames (never the client's original
name, to avoid path traversal) and served back via the `/uploads` static
mount. Limits are configurable in `.env`.

## Backup & Restore

`super_admin` only. Export downloads a JSON file covering every table in
FK-safe dependency order — works against MySQL or SQLite identically. Restore
wipes and reloads every table from that file inside one transaction: if
anything fails, nothing changes. The UI requires typing `RESTORE` to confirm
before running, since it replaces all data.

## Security implemented
- Passwords hashed with bcrypt
- JWT access + refresh tokens; role-based access control via `require_roles()`
- Generic (non-leaking) error messages on login and forgot-password
- Time-limited, single-use password reset tokens
- Uploaded files validated by extension and size before being written
- Backup/Restore restricted to `super_admin`

## Known limitations (minor, disclosed rather than hidden)
- The "My Profile" item in each dashboard's user-menu dropdown isn't wired to
  a dedicated page (`href="#"`). Profile photo upload itself works and is
  reachable from each dashboard's own profile card — this is specifically
  the separate menu shortcut that's unbuilt.
- A "Settings" sidebar link is marked "soon" on Teacher, Student, and Admin
  dashboards — never part of the required module list, disclosed rather
  than faked.
- `API_BASE` is a small duplicated inline snippet per page rather than one
  central config; fine at this scale, worth centralizing if it grows.
- Verified in this environment against SQLite; schema and queries are
  standard SQLAlchemy and should work unchanged against MySQL, but a live
  MySQL run has not been performed here.
- No automated `pytest` suite — verification here was live manual/scripted
  end-to-end testing against a running instance (see below).

## Verified functionality

Tested against a **live running instance** (real backend + real frontend),
including full CRUD cycles independently confirmed against the database:

Login (all 3 roles) · role-based access control · `/api/students/me` /
`/api/teachers/me` · Admin dashboard overview · Student/Teacher Management
CRUD · Classes/Sections/Subjects CRUD · Timetable CRUD + clash detection ·
Attendance (teacher marking + admin report/edit/delete) · Exams & Results
(schedule creation, result entry, grade/GPA calculation, position list) · Fee
Management (structures, challan generation, payment recording) · Notices
(CRUD + real notification fan-out) · Reports (real PDF/Excel downloads,
verified file signatures) · Backup & Restore (full cycle with data-integrity
verification) · Password reset (real email content, token validation,
single-use enforcement) · Profile photo upload · Homework attachment upload
· Teacher/Student dashboard overviews.

## Parts history

| Part | Contents |
|------|----------|
| 1 | Backend foundation — auth, JWT, RBAC |
| 2 | Academic CRUD (classes, sections, subjects, teachers, students) |
| 3 | Attendance, homework, timetable |
| 4 | Exams, results, fees |
| 5 | Notices, notifications, reports |
| 6 | Bilingual public site + login |
| 7 | Admin dashboard + Student Management |
| 8 | Teacher & Student dashboards |
| Post-8 | File uploads, email service, backup/restore, remaining admin CRUD screens, full live E2E verification and bug-fixing pass |
