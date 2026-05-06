# PROJECT CONTEXT

## 1. Project Overview

Bu loyiha — avtomobillar uchun service/harajat/maintenance tracking platforma.

Asosiy maqsad:

* foydalanuvchilar mashina tarixini yuritishi
* servis va xarajatlarni kuzatish
* odometr tracking
* kelajakda:

  * reminder system
  * AI assistant
  * OCR (rasmdan odometr o‘qish)
  * workshop marketplace

---

## 2. Architecture

Loyiha **service-oriented architecture** asosida qurilgan.

Asosiy qatlamlar:

* Django (backend)
* Service layer (business logic)
* Selector layer (read logic)
* Policy layer (authorization)
* Telegram bot (client/transport)
* Worker (background processing)

Bot:

* faqat interface
* barcha logic service’da

---

## 3. Tech Stack

* Backend: Django
* Database: PostgreSQL
* Runtime: Docker + Docker Compose
* Reverse proxy: Nginx
* Bot: Telegram (management command orqali)
* Future:

  * AI (LLM)
  * OCR
  * Object storage (S3/MinIO)

---

## 4. Rules

Loyiha qat’iy rules asosida ishlaydi:

* backend.md
* django.md
* database.md
* telegram_bot.md
* security.md
* testing.md
* docker_ops.md

⚠️ Bu rules buzilmasligi kerak

---

## 5. Project Structure

* agents.md — loyiha arxitekturasi
* rules/ — development qoidalari
* issue_tracking/ — task va sprint boshqaruvi
* src/ — asosiy kod

---

## 6. Current State

* Current sprint: 3 (Production Ready Launch)
* Status: Deployable MVP foundation delivered, local stack running with `web`, `bot`, and `db`
* Test status: full Django suite passing (`77 tests OK` as of 2026-04-30)
* Completed:

  * Rules system
  * Issue tracking structure
  * TASK-001 (Django init)
  * TASK-002 (Docker setup)
  * TASK-003 (Postgres integration)
  * TASK-004 (Custom User model)
  * TASK-005 (TelegramAccount model)
  * TASK-006 (Basic admin setup)
  * Split settings (`base`, `local`, `production`)
  * `/health/` smoke endpoint
  * `/ready/` DB readiness endpoint
  * Default project-level smoke test discovery
  * Docker-based local stack (`web` + `db`)
  * Telegram update idempotency
  * Car access policy enforcement
  * Odometer monotonic validation + current odometer cache
  * Maintenance record + line item + odometer history transaction
  * Audit log foundation
  * Notification/reminder foundation + Telegram delivery worker
  * AI assistant integration with OpenAI-compatible provider adapter
  * Production Docker Compose stack (`web`, `bot`, `notification-worker`, `db`, `nginx`)
  * Local Docker bot service (`docker compose up -d bot`)
  * Invite/share flow (`/share`, `/join`)
  * Service history view (`/history`)
  * Telegram media metadata attachment for maintenance records (`/attachmedia`)
  * Telegram inline confirmation buttons for odometer and maintenance save/cancel
  * Telegram callback query polling and immediate `answerCallbackQuery`
  * Manageable car selector for odometer and maintenance flows
  * Historical maintenance support: service date is user-confirmed and can be backdated
  * Lower historical maintenance odometer is allowed without lowering `Car.current_odometer`
  * Telegram Mini App / Web App MVP:
    * `/app/` dashboard
    * `/app/login/` Telegram initData auth + DEBUG dev login
    * `/app/maintenance/new/` service creation UI
    * Web App button through `/app` command and `TELEGRAM_WEBAPP_URL`

* Next in queue:

  * Set real public HTTPS `TELEGRAM_WEBAPP_URL` and verify Web App inside Telegram
  * Production `.env`ni real secretlar bilan to'ldirish
  * Telegram tokenni rotate qilish
  * Production stackni VPS'da ko'tarish
  * End-to-end smoke: `/start`, `/app`, add car, add maintenance, odometer, `/ask`
  * Invite management UX: revoke/list active invites
  * Web App media upload/preview and Telegram file download/storage layer
  * Web App invite management and member roles UI
  * Maintenance history details page + filters
  * Integration/e2e testlarni kengaytirish

---

## 7. Roadmap (High-level)

### Phase 1 (MVP) — mostly delivered

* User
* Car
* Maintenance
* Odometer
* Bot basic flows
* Telegram Web App MVP

### Phase 2 — launch hardening

* Sharing system
* Notifications
* Reminder engine
* Web App UX completion
* Media storage
* Production observability

### Phase 3

* Workshop marketplace
* Reviews

### Phase 4

* AI assistant
* OCR

---

## 8. Key Design Decisions

* Bot = client, backend = platform
* Business logic faqat service layer’da
* Telegram chat flow bazaviy funksiyalar uchun qoladi
* Murakkab servis/history/media UX Telegram Web App orqali beriladi
* Web App auth faqat Telegram `initData` HMAC validation orqali productionda qabul qilinadi
* DB schema extensible bo‘lishi shart
* AI optional layer (`AI_ASSISTANT_ENABLED`)

---

## 9. Next Steps

1. Production HTTPS domain tayyorlash va `TELEGRAM_WEBAPP_URL=https://domain/app/` sozlash.
2. Telegram tokenni rotate qilish va `.env.production` secretlarini real qiymatlar bilan to'ldirish.
3. VPS deploy: `docker-compose.production.yml` orqali `web`, `bot`, `notification-worker`, `db`, `nginx`.
4. Telegram Web App smoke:
   * `/start`
   * `🌐 CarCare App`
   * Web App login
   * dashboard
   * service create with historical date
5. Web App Phase 2:
   * car create/edit UI
   * maintenance details/history filters
   * media upload/preview
   * invite/member management
6. Reminder scheduling UX:
   * oil/spark plug/filter presets
   * km/time based reminder rules
   * notification preferences
7. Observability:
   * structured error logging
   * production backup restore drill
   * CI pipeline

---

## 10. Update Rules

Bu fayl faqat quyidagi holatlarda yangilanadi:

* yangi sprint boshlansa
* arxitektura o‘zgarsa
* yangi katta feature qo‘shilsa
* loyiha yo‘nalishi o‘zgarsa

❌ Har kichik task uchun yangilanmaydi

---

## 11. Principle

Bu fayl:
👉 loyiha holatini 1-2 daqiqada tushunish uchun

Agar bu faylni o‘qib loyiha tushunilmasa:
→ u noto‘g‘ri yozilgan
