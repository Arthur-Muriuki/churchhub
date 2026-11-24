# ChurchHub

A Secure Centralized Church Digital Operations System built with Django and PostgreSQL.

## Core Modules
- Dashboard & Administration (RBAC, Audit Logs, Configurable Church Settings)
- Member Management & Demographic Registry
- Baptism & Digital Certificate Generation
- Departments & Ministries Coordination
- Events & Attendance Tracking
- Visitor & Confidential Pastoral Care Follow-Up
- Reports & Analytics
- Internal Announcements & Communication

## Local Setup
1. Create and activate virtual environment: `python -m venv venv`
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure environment variables.
4. Run migrations: `python manage.py migrate`
5. Start server: `python manage.py runserver`