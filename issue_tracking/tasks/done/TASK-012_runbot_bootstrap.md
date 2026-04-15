# TASK-012: runbot bootstrap

## Description

Telegram bot uchun management command va minimal bootstrap qatlamini qo'shish.

---

## Requirements

- `python src/manage.py runbot` command
- bot config env orqali (`TELEGRAM_BOT_TOKEN`)
- graceful startup/shutdown logging
- basic polling loop skeleti

---

## Acceptance Criteria

- `runbot` command import/xatolarsiz ishga tushadi
- token bo'lmasa aniq xato qaytaradi
- lifecycle loglari mavjud (`started`, `stopped`, `error`)

---

## Notes

- `telegram_bot.md` qoidalariga qat'iy amal qilish
- business logic handlerlarda bo'ladi, commandda emas

- Completed:
  - `runbot` management command qo'shildi
  - `TELEGRAM_BOT_TOKEN` bo'lmasa `CommandError` bilan aniq xato qaytariladi
  - polling loop skeleti (`TelegramBotClient` + `UpdateDispatcher`) qo'shildi
  - lifecycle loglari (`started`, `stopped`, `error`) qo'shildi
  - bot token config helper va test qo'shildi
