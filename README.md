# JobPortal Web Application

A full-featured, modern Job Portal web application built with **Django 5.x**, **PostgreSQL** (with optional SQLite dev fallback), **Bootstrap 5** with a customized design system, and **jQuery** for asynchronous interactions (live search & filters, async application submissions, bookmarking, and dynamic profile repeaters).

---

## Tech Stack & Architecture

- **Backend**: Python 3.10+ / Django 5.x
- **Database**: PostgreSQL (via `psycopg` 3.x), configurable via `.env` (with automatic SQLite fallback for rapid local dev)
- **Frontend**: HTML5, Bootstrap 5.3, Bootstrap Icons, Google Fonts (*Plus Jakarta Sans*), Custom CSS Design System
- **Client-side Interactivity**: jQuery 3.7.1 (AJAX search/filter, async job application modal, dynamic fields, bookmark toggles)
- **Analytics Visualization**: Chart.js for custom admin dashboard metrics

---

## Core Apps & Modules

1. **`accounts`**:
   - Custom user model `User(AbstractUser)` with role choices: `Job Seeker`, `Employer`, and `Admin`.
   - Automatic permission group assignment via Django signals (`Job Seekers`, `Employers`).
   - `SeekerProfile`: Headline, bio, resume upload, skills, dynamic work experience, and education records.
   - `EmployerProfile`: Company profile, logo, website, industry, company size, and location.
   - Simulated 1-click email verification stub.
2. **`jobs`**:
   - Job listings with rich metadata: Category, employment type (Full-time, Part-time, Remote, Internship, Contract), experience level, salary bands, deadline, and view count tracking.
   - Moderation states: `Pending Moderation`, `Approved / Active`, `Rejected`, `Closed`.
   - `SavedJob` bookmarking engine.
   - Live AJAX search & filtering endpoint without full page reloads.
3. **`applications`**:
   - Candidate application workflow: Resume file upload or reuse profile resume, personalized cover letter, and private hiring notes.
   - Status lifecycle tracking: `Applied` &rarr; `Shortlisted` &rarr; `Hired` / `Rejected`.
   - Asynchronous application submission via jQuery AJAX modal with inline validation.
   - Secure resume download view with role-based permission checks.
4. **`dashboard`**:
   - **Job Seeker Dashboard**: Track applications, view review statuses, manage bookmarked jobs, and view profile completeness.
   - **Employer Dashboard**: Overview of posted positions, candidate counts, job views analytics, and applicant review dashboard.
   - **Custom Admin Dashboard**: Executive view showing site-wide stats (users, jobs, applications, active/pending breakdown), Chart.js visualizations, and an interactive **Moderation Queue** with 1-click AJAX "Approve" and "Reject" buttons.

---

## Quick Setup Instructions

### 1. Prerequisites
- Python 3.10+ installed
- PostgreSQL installed and running (or use SQLite mode for local demo)

### 2. Create Virtual Environment & Install Dependencies
```bash
# Create and activate virtual environment
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

To connect to your PostgreSQL database, open `.env` and set:
```env
USE_POSTGRES=True
DB_NAME=jobportal_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=5432
```
*(If `USE_POSTGRES=False`, Django will automatically run on a local SQLite database for instant development without needing PostgreSQL service running).*

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Seed Database with Realistic Sample Data
Populate categories, companies, realistic jobs, seekers, and test applications:
```bash
python manage.py seed_data
```

### 6. Start Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## Pre-Configured Demo Accounts

| Role | Username | Password | Email | Notes |
|---|---|---|---|---|
| **System Admin** | `admin` | `admin123` | `admin@jobportal.local` | Access to `/dashboard/admin/` & `/admin/` |
| **Employer 1** | `cloudscale` | `pass123` | `hiring@cloudscale.io` | CloudScale Technologies (3 jobs, applicants) |
| **Employer 2** | `pulsefin` | `pass123` | `talent@pulsefin.com` | Pulse Financial (Fintech jobs & applicants) |
| **Job Seeker 1** | `alex_dev` | `pass123` | `alex.rivera@example.com` | Senior Backend Engineer (applied & saved jobs) |
| **Job Seeker 2** | `sarah_ux` | `pass123` | `sarah.chen@example.com` | Lead Product Designer (Hired status) |

---

## Running Automated Tests

Run the full Django test suite covering accounts, jobs, applications, and dashboards:
```bash
python manage.py test
```

---

## Key Endpoints & Features

- `/` — Homepage with hero search, stats counter, category cards, featured jobs, and testimonials.
- `/jobs/` — Live AJAX job listings with search, category pills, employment type, location, and salary filter.
- `/jobs/<slug>/` — Job detail page, company overview, view counter, bookmark button, and AJAX application modal.
- `/accounts/register/` — Registration with role selection (Job Seeker vs Employer).
- `/accounts/login/` — Authentication with automatic role-based redirect.
- `/accounts/profile/seeker/` — Profile editor with dynamic "Add Experience" and "Add Education" field repeaters.
- `/dashboard/seeker/` — Seeker dashboard (applied jobs, saved jobs, completion meter).
- `/dashboard/employer/` — Employer dashboard (job listings, views count, applicant count).
- `/dashboard/employer/jobs/<slug>/applicants/` — Candidate review interface with resume download and AJAX status changer.
- `/dashboard/admin/` — Custom platform administration dashboard with Chart.js analytics and Moderation Queue.
- `/admin/` — Django standard admin site with custom filters, search fields, and moderation actions.
