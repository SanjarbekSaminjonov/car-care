# CarCare Bot Platform

Telegram-first avtomobil servis/xarajat tracking platformasi.

## Local Docker setup

1. `.env.example` dan nusxa oling:

```bash
cp .env.example .env
```

2. Docker stackni ishga tushiring:

```bash
docker compose up --build
```

3. Alohida terminalda migration bajaring:

```bash
docker compose exec web python src/manage.py migrate
```

4. Health endpoint tekshiruvi:

```bash
curl http://localhost:8000/health/
```

## Services

- `web`: Django app (`runserver`) + healthcheck
- `db`: PostgreSQL 16 + persistent volume

## Environment

Asosiy sozlamalar `.env` orqali beriladi. Namuna qiymatlar `.env.example` faylida mavjud.
