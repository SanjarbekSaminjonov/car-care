# TASK-003: PostgreSQL integration

## Description

Django’ni PostgreSQL bilan ulash.

---

## Requirements

- psycopg2 yoki equivalent
- env orqali config

---

## Acceptance Criteria

- migrate ishlaydi
- db bilan connection bor
- sqlite ishlatilmaydi

---

## Notes

- database.md ga amal qilish

- Completed:
  - PostgreSQL drayver dependency `psycopg[binary]` bazaviy requirementlarda mavjudligi tasdiqlandi
  - settings darajasida default DB engine PostgreSQL ekanligi saqlanib qoldi
  - Docker Compose `db` servisi va `web -> db` ulanish konfiguratsiyasi qo'shildi
  - settings smoke testga DB engine `django.db.backends.postgresql` assertion qo'shildi
