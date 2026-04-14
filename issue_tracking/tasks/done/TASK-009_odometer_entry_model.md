# TASK-009: OdometerEntry model

## Description

Mashina odometr tarixini append-only ko'rinishda saqlaydigan model qo'shish.

---

## Requirements

- `car` FK
- `value` (musbat son)
- `entry_date`
- source (`manual`, `maintenance_record`, `ocr`, `system`)
- `created_by` FK (nullable)
- `created_at`

---

## Acceptance Criteria

- `OdometerEntry` modeli migration bilan yaratilgan
- `(car, entry_date)` uchun index mavjud
- source choices bilan cheklangan
- model testlarida source/value basic validation tekshirilgan

---

## Notes

- source of truth odometer history bo'lishi kerak

- Completed:
  - `apps.odometer` app yaratilib `OdometerEntry` modeli qo'shildi
  - source choices, `(car, entry_date)` index va create testlar qo'shildi
  - admin registratsiyasi va smoke test qo'shildi
