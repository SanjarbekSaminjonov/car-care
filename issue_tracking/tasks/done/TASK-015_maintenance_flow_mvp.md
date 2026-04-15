# TASK-015: Maintenance add flow (MVP)

## Description

Telegram orqali minimal maintenance yozuvini kiritish flowini yaratish.

---

## Requirements

- car tanlash
- event date, odometer, title input
- minimal line item qo'shish
- confirm step
- `/cancel` qo'llab-quvvatlash

---

## Acceptance Criteria

- maintenance record yaratish bot flow orqali ishlaydi
- kamida bitta line item saqlanadi
- confirm bosqichisiz final write qilinmaydi
- integration test (happy path + invalid input) mavjud

---

## Notes

- audit/service boundaries saqlansin

- Completed:
  - `/addmaintenance` command routing qo'shildi
  - maintenance flow step'lari qo'shildi (plate -> title -> odometer -> item -> amount -> confirm)
  - confirm bo'lmasa final write qilinmaydi (`yes` talab qilinadi)
  - write-side create `services.maintenance_service` orqali transaction ichida bajariladi
  - flow testlari (happy path + invalid odometer + invalid confirmation) qo'shildi
