# TASK-016: Manual odometer update flow

## Description

Telegram orqali odometr qiymatini qo'lda kiritish va `OdometerEntry` saqlash flowini yaratish.

---

## Requirements

- car tanlash
- value input parse/validation
- confirmation step
- success summary response

---

## Acceptance Criteria

- odometer entry bot orqali yaratiladi
- noto'g'ri qiymatlar uchun aniq recovery message bor
- cancel ishlaydi
- flow testlari mavjud

---

## Notes

- OCR task bu sprint scope'ida emas (manual only)

- Completed:
  - `/addodometer` command routing qo'shildi
  - manual odometer flow qo'shildi (plate -> value -> confirm)
  - value parse/validation va recovery message qo'shildi
  - odometer write `services.odometer_service` orqali bajariladi
  - flow testlari qo'shildi
