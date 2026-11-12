# 🩵 SkyHire - Job Application Tracker & ATS

A full-stack web application designed for modern recruitment and candidate transparency. Built with **Flask**, **SQLite / SQLAlchemy**, and styled with an elegant **light blue and white** design system.

---

## 🌟 Key Features

### 👑 1. For Administrators / Recruiters
- **Requisition Management**:
  - Post new jobs with department, location (remote/hybrid/onsite), job type, experience level, salary range, responsibilities, requirements, and benefits.
  - Edit job listings or toggle visibility (`Active`, `Draft`, `Closed`).
  - Delete postings and manage Requisition lifecycles.
- **Applicant Tracking System (ATS) Pipeline**:
  - View all applicants across jobs or filter by specific vacancy, candidate name, or hiring stage.
  - Detailed candidate dossier: view contact details, portfolio/LinkedIn links, and cover letters.
  - **Resume Inspection & Download**: Direct download of uploaded resumes with security checks.
  - **Pipeline Stage Progression**: Move candidates seamlessly across milestones:
    - `Application Submitted` ➔ `Under Review` ➔ `Interview Scheduled` ➔ `Offer Extended` ➔ `Accepted & Hired` (or `Not Selected`).
  - **Recruiter Feedback Channel**: Write personalized updates or interview invitations that appear immediately on the candidate's tracking dashboard.
  - **Private Internal Notes**: Add internal interview notes visible only to the hiring panel.
  - **Full Audit Timeline**: Every milestone change is logged with timestamps.

### 👤 2. For Normal Users / Candidates
- **Job Board**:
  - Search jobs by keyword, title, department, employment type, experience, and location.
  - Clear indicator badges showing jobs already applied for.
  - **Multi-Platform Job Sharing**: 1-click share modal to copy direct link or share directly to LinkedIn, X (Twitter), WhatsApp, Email, or device share sheet.
- **Streamlined Application Process**:
  - Apply with 1 click using profile details or custom inputs.
  - Drag-and-drop file upload for Resumes / CVs (PDF, DOCX, TXT).
  - Cover letter submission.
- **Interactive Application Tracker ("My Applications")**:
  - **Visual Status Progress Bar**: Real-time visual progress stepper tracing the 4 core phases (`Submitted` ➔ `In Review` ➔ `Interview` ➔ `Decision`).
  - **Recruiter Updates Banner**: Immediate visibility into interview schedules, recruiter notes, and feedback.
  - **Timeline Event History**: Expandable audit log of every step taken on the application.
  - **Resume Access**: Re-download the uploaded resume at any time.
  - **Voluntary Withdrawal**: Ability to withdraw active applications if desired.

---

## 🎨 Brand Design: Light Blue & White

The UI is built around an airy, clean, and trustworthy **Light Blue & White** palette:
- **Primary Sky Blue**: `#0ea5e9` / `#0284c7`
- **Soft Pastel Backgrounds**: `#f0f9ff` / `#e0f2fe` / `#f8fbfe`
- **Crisp Surfaces**: Pure `#ffffff` cards with subtle `#bae6fd` borders and soft shadows
- **Typography**: Clean, readable sans-serif (*Plus Jakarta Sans*) with modern rounded badges and Lucide icons

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure Python 3.10+ is installed on your machine.

### 2. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Initialize & Seed Database
Pre-populates the database with realistic jobs, users, and candidate applications:
```bash
python seed_data.py
```

### 4. Run the Application
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🔑 Demo Accounts & Quick Login

The application includes a **1-Click Demo Switcher** bar at the very top of every page, as well as demo shortcut buttons on the Sign In page:

| Role | Email | Password | What You Can Test |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@jobtracker.com` | `admin123` | Post jobs, manage requisitions, review candidate pipeline, advance statuses, leave feedback |
| **Candidate** | `sarah.miller@example.com` | `user123` | Browse jobs, apply with resume, check live application progress tracker & interview notes |

*(You can also click **Get Started / Register** to create brand new candidate or admin accounts!)*

---

## 📁 Project Architecture

```
job-tracker-app/
├── app.py                     # Core Flask app, routing & controllers
├── models.py                  # SQLAlchemy models (User, Job, Application, TimelineEvent)
├── config.py                  # Application configuration & upload constraints
├── seed_data.py               # Database seeder with sample jobs and applications
├── test_app.py                # Automated unit and integration test suite
├── requirements.txt           # Python package dependencies
├── README.md                  # Project documentation
├── uploads/
│   └── resumes/               # Secure directory for applicant resumes
├── static/
│   ├── css/
│   │   └── custom.css         # Brand styling (light blue & white accents)
│   └── js/
│       └── app.js             # Drag-and-drop upload & interactive UI helpers
└── templates/
    ├── base.html              # Base layout with navbar, demo bar, and footer
    ├── index.html             # Homepage with hero, metrics, and featured jobs
    ├── jobs.html              # Searchable and filterable job board
    ├── job_detail.html        # Job overview & requirements
    ├── apply.html             # Application form with resume upload
    ├── my_applications.html   # Candidate tracking center with visual progress stepper
    ├── login.html             # Sign in with 1-click demo buttons
    ├── register.html          # Registration with Candidate vs Admin role toggle
    ├── admin/
    │   ├── dashboard.html     # ATS overview, hiring stats, and quick actions
    │   ├── jobs.html          # Job requisition management table
    │   ├── job_form.html      # Create / edit job requisition form
    │   ├── applications.html  # Candidate pipeline table with search and filters
    │   └── application_detail.html # Candidate dossier, resume viewer, status updater & notes
    └── errors/
        ├── 404.html           # Custom 404 error page
        └── 500.html           # Custom 500 error page
```

---

## 🧪 Running the Automated Tests

To execute the unit and integration test suite:
```bash
python -m unittest test_app.py
```
All 5 comprehensive test suites cover public routes, candidate application workflow, resume upload, admin job creation, status updates, and candidate tracker reflection.

