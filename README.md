# Student Management System

## 🚀 Ready for Render Deployment

This project is fully configured and ready to deploy on Render.com!

- ✅ SQLite database (no external DB required)
- ✅ Single `app.py` entry point
- ✅ `gunicorn` for production
- ✅ Login system with session management
- ✅ Student CRUD operations
- ✅ CSV import/export
- ✅ Analytics dashboard

## Render Settings
- **Start Command**: `gunicorn app:app`
- **Build Command**: `pip install -r requirements.txt`
- **Python Version**: 3.x

**Note**: No Procfile needed (Render uses the start command from web interface).

## Overview
This project is a Flask-based student management system using SQLite.

- Uses `app.py` as the single application entry point
- Stores student data in `students.db`
- Creates the database and `students` table automatically on first run
- Deploys on Render with `gunicorn app:app`

## What changed
- Replaced MySQL with SQLite
- Removed MySQL-only helper files
- Kept a single runnable app in `app.py`
- Updated dependencies to only `Flask` and `gunicorn`

## Features
- Add, update, delete student records
- Search students by name, roll number, or email
- Export students to CSV
- Bulk import students from CSV
- Simple analytics on student data

## Technology Stack
- **Backend**: Flask (Python)
- **Database**: SQLite (`students.db`)
- **Frontend**: HTML, CSS
- **Deployment**: Render with `gunicorn`

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd mini
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run locally
```bash
python app.py
```
Open `http://localhost:5000`

### 4. First-time setup
On first run, the app will create `students.db` and the `students` table automatically.

## Render Deployment
- Start Command: `gunicorn app:app`
- Build Command: `pip install -r requirements.txt`

## Important notes
- `students.db` is created automatically
- No MySQL server is required
- No `.env` database credentials are needed for SQLite

## File structure
```
mini/
├── app.py
├── requirements.txt
├── Procfile
├── README.md
├── .env.example
├── students.db   # created automatically on first run
├── static/
└── templates/
```

## Remove obsolete files
If you still have the old MySQL files in your repo, delete them:
- `student_app.py`
- `insert_user.py`
- `config.py`

## Notes
This project is now simplified for Render deployment and SQLite usage. If you see any old MySQL setup files or instructions, they are obsolete and should be removed.

