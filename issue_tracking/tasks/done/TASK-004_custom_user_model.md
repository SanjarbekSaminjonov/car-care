# TASK-004: Custom User model

## Description

Custom User model yaratish.

---

## Requirements

- AbstractUser yoki AbstractBaseUser
- email-based yoki minimal user

---

## Acceptance Criteria

- custom user ishlaydi
- admin’da ko‘rinadi
- migration to‘g‘ri

---

## Notes

- django.md ga amal qilish

- Completed:
  - `apps.users.models.User` modeli `AbstractUser` asosida yaratilgan holda saqlanmoqda
  - `AUTH_USER_MODEL = 'users.User'` konfiguratsiyasi settings'da mavjud
  - `User` admin registratsiyasi va initial migration mavjud
  - custom user bo'yicha smoke testlar mavjud
