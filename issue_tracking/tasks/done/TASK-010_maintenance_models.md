# TASK-010: MaintenanceRecord va MaintenanceLineItem modellari

## Description

Servis/remont hodisasini va uning satrlarini saqlash uchun asosiy maintenance modellari.

---

## Requirements

- `MaintenanceRecord`:
  - UUID PK
  - `car` FK
  - `event_date`, `odometer`, `title`, `description`
  - `created_by`, `paid_by_user` (nullable)
  - status (`draft`, `final`)
  - timestamps
- `MaintenanceLineItem`:
  - `maintenance_record` FK
  - item_type (`part`, `labor`, `service`, `fee`, `fluid`, `filter`, `other`)
  - `name`, `quantity`, `unit_price`, `total_price`
  - payer maydonlari (nullable)
  - timestamps

---

## Acceptance Criteria

- Ikkala model migration bilan yaratilgan
- choice maydonlari aniq enum/choices bilan cheklangan
- line item relation ishlaydi (`related_name` bilan)
- model testlarida asosiy create/query flow tekshirilgan

---

## Notes

- transaction orchestration keyingi sprintda service qatlamida qilinadi

- Completed:
  - `apps.maintenance` app yaratildi
  - `MaintenanceRecord` va `MaintenanceLineItem` modellari qo'shildi
  - enum choices, relation (`line_items`) va model/admin testlar qo'shildi
