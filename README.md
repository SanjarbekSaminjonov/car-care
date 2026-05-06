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
- `bot`: Telegram polling worker (`python src/manage.py runbot`)
- `db`: PostgreSQL 16 + persistent volume

## Production deployment

Single-VPS production stack uchun:

```bash
cp .env.production.example .env
docker compose -f docker-compose.production.yml up -d --build
```

Production compose quyidagilarni ko'taradi:

- `web`: Django + Gunicorn
- `bot`: Telegram polling worker
- `notification-worker`: reminder/notification worker
- `db`: PostgreSQL
- `nginx`: reverse proxy + static/media serving

To'liq runbook: [DEPLOYMENT.md](DEPLOYMENT.md).

## Telegram MVP commands

- `/start` — account sync va main menu
- `/app` — CarCare Telegram Web App
- `/cars` — mashinalar ro'yxati
- `/addcar` — mashina qo'shish
- `/addmaintenance` — servis yozuvi qo'shish
- `/history [davlat raqami]` — servis tarixi
- `/share [davlat raqami] [viewer|manager]` — invite yaratish
- `/join [invite-kod]` — invite orqali mashinaga qo'shilish
- `/attachmedia [davlat raqami]` — oxirgi servis yozuviga Telegram media biriktirish
- `/addodometer` — odometrni qo'lda yangilash
- `/ask savol` yoki `/ai savol` — AI assistant

## Environment

Asosiy sozlamalar `.env` orqali beriladi. Namuna qiymatlar `.env.example` faylida mavjud.
Telegram Web App uchun `TELEGRAM_WEBAPP_URL` public HTTPS `/app/` URL bo'lishi kerak.
Local preview: `http://localhost:8000/app/login/`.
