# Ajay A — Portfolio Website

Professional, mobile-responsive portfolio built with Django. Includes admin dashboard with full CRUD, resume upload, visitor tracking, user management, and contact form with email delivery.

## Features

- **Public portfolio** — Hero, About, Skills, Experience, Projects, Education, Contact
- **Contact form** — Messages saved in DB and emailed to `ajayhkr2002@gmail.com`
- **Resume upload & download** — Upload PDF from dashboard; visitors can download
- **Admin dashboard** — Manage profile, experience, projects, education
- **User management** — Create, edit, delete staff users
- **Visitor tracking** — View who visited your site
- **Fully responsive** — Works on mobile, tablet, and desktop

## Quick Start

```bash
cd C:\Users\User\Projects\ajay-portfolio

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations and load resume data
python manage.py migrate
python manage.py load_initial_data

# Start server
python manage.py runserver
```

Open **http://127.0.0.1:8000** for the portfolio.

## Admin Access

| URL | Purpose |
|-----|---------|
| `/login/` | Dashboard login |
| `/dashboard/` | Admin panel |
| `/admin/` | Django admin |

**Default credentials:** `admin` / `admin123` (change after first login)

## Email Setup (Production)

Copy `.env.example` to `.env` and configure Gmail App Password:

```env
DEBUG=False
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

For Gmail: Google Account → Security → 2-Step Verification → App passwords.

In development (`DEBUG=True`), emails print to the console instead of sending.

## Dashboard Guide

1. **Profile & Resume** — Update info, upload profile photo and resume PDF
2. **Experience / Projects / Education** — Full CRUD (Create, Read, Update, Delete)
3. **Messages** — View contact form submissions
4. **Visitors** — See site visitor logs
5. **Users** — Manage admin users

## Tech Stack

- Python, Django 5
- SQLite (default)
- WhiteNoise (static files)
- Responsive CSS (no framework dependency)

## Deploy

Works on Render, Railway, PythonAnywhere, or any VPS with:

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn config.wsgi:application
```

Set `DEBUG=False`, `SECRET_KEY`, and email env vars in production.
