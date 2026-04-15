# TASK-005: TelegramAccount model

## Description

Telegram user identity model yaratish.

---

## Requirements

- user FK
- telegram_user_id
- chat_id
- username

---

## Acceptance Criteria

- model ishlaydi
- user bilan bog‘langan
- unique constraint mavjud

---

## Notes

- telegram_bot.md ga amal qilish

- Completed:
  - `apps.telegram` domen app'i yaratildi (`TelegramAccount` modeli bilan)
  - `TelegramAccount` uchun `user` FK, `telegram_user_id` (unique), `chat_id`, `username` va qo'shimcha metadata fieldlari qo'shildi
  - model admin registratsiyasi va qidiruv/filter konfiguratsiyasi qo'shildi
  - model hamda admin registratsiyasi uchun testlar yozildi
  - initial migration (`0001_initial.py`) qo'shildi

