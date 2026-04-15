# 🚀 Sprint 1 — Core Domain

## Sprint goal
Telegram-first platformaning asosiy domen modelini (Car/Membership/Maintenance/Odometer) production-ready foundation darajasida tayyorlash.

## Status
- Completed (core models + admin + migrations + smoke tests)

## Scope
- `cars` app skeleton + `Car` modeli
- `car_membership` modeli (role/status bilan)
- `maintenance` app: `MaintenanceRecord` + `MaintenanceLineItem`
- `odometer` app: `OdometerEntry`
- minimal admin registratsiya va smoke/model testlar

## Planned tasks
- TASK-007 — Car model ✅
- TASK-008 — Car membership model ✅
- TASK-009 — Odometer entry model ✅
- TASK-010 — Maintenance record va line item ✅
- TASK-011 — Core domain admin setup ✅

## Definition of sprint done
- Yuqoridagi tasklar `done`ga o'tgan bo'lishi
- Migrations izchil va conflict'siz bo'lishi
- `python3 src/manage.py check` va `python3 src/manage.py test` yashil bo'lishi
