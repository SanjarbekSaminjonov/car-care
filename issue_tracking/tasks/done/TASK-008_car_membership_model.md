# TASK-008: CarMembership model

## Description

User va car o'rtasidagi many-to-many aloqani explicit `CarMembership` modeli bilan yaratish.

---

## Requirements

- `car` FK
- `user` FK
- role (`owner`, `manager`, `viewer`)
- status (`active`, `pending`, `revoked`)
- invited_by (nullable FK to user)
- joined_at + timestamps

---

## Acceptance Criteria

- `(car, user)` bo'yicha unique constraint bor
- role/status choices orqali cheklangan
- migration qo'shilgan
- model testlarida uniqueness va choice validation tekshirilgan

---

## Notes

- permission modeli keyingi policy qatlamiga tayyor bo'lishi kerak

- Completed:
  - `CarMembership` modeli `cars` app ichida qo'shildi
  - role/status choices va `(car, user)` unique constraint qo'llandi
  - migration hamda uniqueness testi yozildi
