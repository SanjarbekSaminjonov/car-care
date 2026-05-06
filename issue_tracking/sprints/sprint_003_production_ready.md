# Sprint 003 - Production Ready Launch

## Goal

Bring the Telegram-first CarCare platform to a deployable MVP with production
runtime wiring, durable bot state, access control, auditability, notifications,
and AI assistant integration.

## Scope

- Docker production stack: Django web, Telegram bot worker, PostgreSQL, Nginx
- Gunicorn-based Django runtime
- `/health/` and `/ready/` checks
- Telegram account sync and restart-safe conversation state
- Telegram update idempotency
- Car access policy enforcement
- Odometer monotonic validation and `Car.current_odometer`
- Maintenance record creation with line item and odometer history
- Audit log foundation
- Notification/reminder event foundation
- AI assistant provider adapter and interaction logging
- Focused service, policy, selector, bot, and worker tests

## Quality Gates

- `python src/manage.py check`
- `python src/manage.py makemigrations --check --dry-run`
- `python src/manage.py test`
- Production compose config validates
- New migrations apply cleanly

## Launch Checklist

- Rotate any exposed Telegram token before launch
- Fill `.env` from `.env.production.example`
- Build and start `docker-compose.production.yml`
- Verify `/health/` and `/ready/`
- Verify `/start`, add car, add maintenance, odometer update
- Verify bot logs have no unhandled exceptions
- Verify database backup command works
