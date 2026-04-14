# TASK-013: /start, /help, menu flow

## Description

Botning onboarding entrypointlarini (`/start`, `/help`) va asosiy menyu javoblarini yaratish.

---

## Requirements

- `/start` handler
- `/help` handler
- asosiy menyu keyboard builder
- text formatterlar alohida modulda

---

## Acceptance Criteria

- `/start` va `/help` commandlari alohida handlerlar orqali ishlaydi
- handlerlarda business logic yo'q (service/selector/policy boundary saqlangan)
- menu response testlar bilan qoplangan

---

## Notes

- message matnlari qisqa va yo'naltiruvchi bo'lsin

- Completed:
  - `/start` va `/help` command handlerlari qo'shildi
  - asosiy menyu keyboard builder alohida modulga ajratildi
  - user-facing matnlar formatter modulida ajratildi
  - `UpdateDispatcher` command routing bilan yangilandi
  - handler/dispatcher testlari qo'shildi
