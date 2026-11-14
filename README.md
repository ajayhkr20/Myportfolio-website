# Ajay A — Portfolio Website

Professional, mobile-responsive portfolio built with Django. Includes admin dashboard with full CRUD, resume upload, visitor tracking, user management, and contact form with email delivery.

## Features

- **Public portfolio** — Hero, About, Skills, Experience, Projects, Education, Contact
- **Contact form** — Messages saved in DB and emailed to `ajayhkr2002@gmail.com`
- **Resume upload & download** — Upload PDF from dashboard; visitors can download
- **Admin dashboard** — Manage profile, experience, projects, education
- **User management** — Create, edit, delete staff users
- **Visitor tracking** — Record homepage visits; logs are available only to signed-in staff in the dashboard
- **Visitor blocking** — Block or unblock visitor IP addresses from the staff dashboard
- **Portfolio assistant** — Public chat assistant uses the current profile, skills, projects, experience, and education data
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
python manage.py createsuperuser

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

Create your own administrator account with `python manage.py createsuperuser`. No default administrator credentials are created.

## Email Setup (Production)

Copy `.env.example` to `.env` and configure Gmail App Password:

```env
DEBUG=False
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

For Gmail: Google Account → Security → 2-Step Verification → App passwords.

In development (`DEBUG=True`), emails print to the console instead of sending.

The example file contains placeholders only. If credentials from an older version were used, revoke and rotate them before deploying.

Uploads use local `media/` storage when Cloudinary credentials are not configured.
For persistent uploads in production, set all three `CLOUDINARY_CLOUD_NAME`,
`CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET` values to real credentials.

## Dashboard Guide

1. **Profile & Resume** — Update info, upload profile photo and resume PDF
2. **Skills** — Create categories, then add or edit skills one at a time under each category
3. **Experience / Projects / Education** — Full CRUD (Create, Read, Update, Delete)
4. **Messages** — View contact form submissions
5. **Visitors** — See site visitor logs and block or unblock visitor IP addresses
6. **Appearance** — Switch between dark and light themes; the selection is saved in this browser

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
Configure a persistent PostgreSQL `DATABASE_URL` for production so visitor logs,
blocked IPs, and portfolio updates survive redeployments. File uploads also need
persistent media storage such as the configured Cloudinary integration. The
dashboard visitor page records homepage visits and provides IP block/unblock
controls; IP blocking applies to the address seen by the server, so shared or
changing network addresses may affect multiple visitors or require a new block.
