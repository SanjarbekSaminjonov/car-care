# TASK-007: Car model

## Description

`cars` domen app'ida `Car` modelini yaratish.

---

## Requirements

- UUID primary key
- plate_number + normalized_plate_number
- brand, model, year, vin (optional)
- powertrain_type (`ice`, `hybrid`, `ev`)
- timestamps
- index/constraintlar

---

## Acceptance Criteria

- `Car` modeli migration bilan yaratilgan
- `normalized_plate_number` bo'yicha index mavjud
- `vin` nullable, lekin bo'lsa unique
- model smoke testlar qo'shilgan

---

## Notes

- `database.md` va `django.md` ga amal qilish
- plate normalization deterministic bo'lishi kerak

- Completed:
  - `apps.cars` app yaratildi va `Car` modeli qo'shildi
  - UUID PK, plate normalization, powertrain choices, VIN unique constraint qo'shildi
  - model migration va model/admin testlar yozildi
