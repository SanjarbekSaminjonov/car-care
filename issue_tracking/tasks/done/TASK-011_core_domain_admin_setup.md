# TASK-011: Core domain admin setup

## Description

Yangi core domain modellari uchun minimal usable admin konfiguratsiyalarini qo'shish.

---

## Requirements

- `Car` admin
- `CarMembership` admin
- `OdometerEntry` admin
- `MaintenanceRecord` admin
- `MaintenanceLineItem` admin

---

## Acceptance Criteria

- Har bir model admin'da ro'yxatdan o'tgan
- `list_display`, `search_fields`, `list_filter` minimal darajada mavjud
- FK-heavy adminlarda `list_select_related` yoki `autocomplete_fields` ishlatilgan
- admin smoke testlari qo'shilgan

---

## Notes

- admin production tool sifatida ko'rilsin (`django.md`)

- Completed:
  - `Car`, `CarMembership`, `OdometerEntry`, `MaintenanceRecord`, `MaintenanceLineItem` adminlari registratsiya qilindi
  - list/search/filter/read-only/autocomplete konfiguratsiyalari qo'shildi
  - admin registratsiya smoke testlari yozildi
