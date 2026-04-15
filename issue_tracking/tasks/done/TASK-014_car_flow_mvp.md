# TASK-014: Car add/list flow (MVP)

## Description

Telegram orqali car qo'shish va userning car ro'yxatini ko'rsatish flowini yaratish.

---

## Requirements

- add car conversation flow (step-by-step)
- list cars handler
- cancel handling (`/cancel`)
- Car va CarMembership yozuvlarini service orqali yaratish

---

## Acceptance Criteria

- user botdan car qo'sha oladi
- user o'z car ro'yxatini ko'ra oladi
- invalid input recovery mavjud
- flow testlari mavjud (happy path + cancel)

---

## Notes

- car creation direct handler write qilinmasin, service qatlamidan o'tsin

- Completed:
  - `/addcar`, `/cars`, `/cancel` command routing qo'shildi
  - step-by-step car flow handler (plate -> brand -> model -> year) qo'shildi
  - write-side create `services.car_service` orqali transaction ichida bajariladi
  - read-side list `selectors.car_selector` orqali ajratildi
  - flow testlari (happy path, cancel, invalid year) qo'shildi
