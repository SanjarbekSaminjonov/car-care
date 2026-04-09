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

* Current sprint: 0 (Setup)
* Status: Sprint 0 foundation ready
* Completed:

  * Rules system
  * Issue tracking structure
  * TASK-001 (Django init)
  * Split settings (`base`, `local`, `production`)
  * Custom User foundation
  * `/health/` smoke endpoint
  * Default project-level smoke test discovery
  * Local bootstrap for `manage.py check/test` (process env + local-safe defaults)
  * Verification snapshot (2026-04-09):
    * `python3 src/manage.py check` -> no issues
    * `python3 src/manage.py test` -> 7 tests passed
* Next in queue:

  * TASK-002 (Docker setup)
  * TASK-003 (Postgres integration)

---

## 7. Roadmap (High-level)

### Phase 1 (MVP)

* User
* Car
* Maintenance
* Odometer
* Bot basic flows

### Phase 2

* Sharing system
* Notifications
* Reminder engine

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
* ViewSet ishlatilmaydi (GenericAPIView)
* DB schema extensible bo‘lishi shart
* AI optional layer

---

## 9. Next Steps

* TASK-002: Docker setup
* TASK-003: Postgres integration
* TASK-004: Custom user refinement

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
