# CarCare Production Deployment

This file is the runbook for a single-VPS Docker Compose deployment.

## 1. Prepare Environment

```bash
cp .env.production.example .env
```

Set real values in `.env`:

- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `POSTGRES_PASSWORD`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_WEBAPP_URL` (`https://your-domain/app/`)
- `AI_PROVIDER_*` if AI is enabled

Do not commit `.env`.

## 2. Build And Start

```bash
docker compose -f docker-compose.production.yml up -d --build
```

The `web` container waits for PostgreSQL, runs migrations, collects static files,
then starts Gunicorn. The `bot` container runs the Telegram polling worker.

## 3. Health Checks

```bash
curl http://localhost/health/
curl http://localhost/ready/
```

- `/health/` verifies that Django responds.
- `/ready/` verifies that Django can query PostgreSQL.

## 4. Logs

```bash
docker compose -f docker-compose.production.yml logs -f web
docker compose -f docker-compose.production.yml logs -f bot
docker compose -f docker-compose.production.yml logs -f notification-worker
docker compose -f docker-compose.production.yml logs -f nginx
```

## 5. Database Backup

```bash
docker compose -f docker-compose.production.yml exec db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup.sql
```

Store backups outside the server and test restore before relying on them.

## 6. Update Deployment

```bash
git pull
docker compose -f docker-compose.production.yml up -d --build
docker compose -f docker-compose.production.yml ps
```

## 7. Rollback

Rollback requires a known good Git commit and a database backup if migrations were applied:

```bash
git checkout <known-good-commit>
docker compose -f docker-compose.production.yml up -d --build
```
