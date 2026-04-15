# TASK-002: Docker setup

## Description

Docker va docker-compose orqali loyiha muhitini yaratish.

---

## Requirements

- Dockerfile
- docker-compose.yml
- web service
- db service

---

## Acceptance Criteria

- docker compose up ishlaydi
- web container ishga tushadi
- db container ishlaydi
- Django db ga ulanadi

---

## Notes

- docker_ops.md ga amal qilish

- Completed:
  - `Dockerfile` qo'shildi (Python 3.12 slim, base dependency install, non-root user)
  - `docker-compose.yml` qo'shildi (`web` + `db` servislar, healthcheck, volumes)
  - PostgreSQL readiness uchun `infra/scripts/wait_for_postgres.py` qo'shildi
  - local ishga tushirish bo'yicha `README.md` va `.dockerignore` qo'shildi
