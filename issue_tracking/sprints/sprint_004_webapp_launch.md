# Sprint 004 - Telegram Web App Launch

## Goal

Turn the Telegram Mini App MVP into the primary user experience for service
tracking while keeping Telegram chat commands for basic and fallback actions.

## Current Baseline

- Django server-rendered Web App routes exist under `/app/`
- Telegram `initData` authentication is implemented
- Dashboard shows cars and recent maintenance records
- Maintenance create form supports historical service dates
- Bot exposes `/app` and optional `🌐 CarCare App` button via `TELEGRAM_WEBAPP_URL`

## Scope

- Configure public HTTPS `TELEGRAM_WEBAPP_URL`
- Verify Web App launch inside Telegram client
- Add Web App car create/edit UI
- Add maintenance detail/history filters
- Add media upload/preview UX
- Add invite/member management screens
- Keep chat bot commands as fallback for core flows

## Quality Gates

- `python src/manage.py check`
- `python src/manage.py test`
- `/app/login/` loads locally
- `/app/` redirects to login when unauthenticated
- Telegram Web App opens from `/app` button in real Telegram
- Service creation saves `event_date`, odometer entry, and line item correctly

## Launch Checklist

- Rotate Telegram bot token before production
- Set `TELEGRAM_WEBAPP_URL=https://<domain>/app/`
- Add domain to `DJANGO_ALLOWED_HOSTS`
- Add HTTPS origin to `DJANGO_CSRF_TRUSTED_ORIGINS`
- Restart `web` and `bot`
- Smoke test:
  - `/start`
  - `/app`
  - Web App login
  - Dashboard
  - Add historical service
  - Verify `/history`

## Next Backlog After Launch

- Service reminder presets by model/year/part type
- Media binary storage instead of Telegram file metadata only
- AI maintenance recommendations using service history context
- E2E browser tests for Web App flows
