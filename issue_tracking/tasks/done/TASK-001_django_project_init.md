# TASK-001: Django project init

## Description

Yangi Django project yaratish va asosiy strukturani tashkil qilish.

---

## Requirements

- src/ structure
- config module
- apps folder
- settings split (base, local, prod)

---

## Acceptance Criteria

- manage.py ishlaydi
- project run bo‘ladi
- settings split mavjud
- src-based layout ishlaydi

---

## Notes

- django.md ga amal qilish
- Completed:
  - `src/` asosidagi Django project foundation yaratildi
  - `config/settings/base.py`, `local.py`, `production.py` split qilindi
  - minimal custom user foundation qo'shildi
  - `python3 src/manage.py check` fresh local bootstrap bilan muvaffaqiyatli o'tadi
  - `python3 src/manage.py test` default discovery orqali smoke testlarni topadi va muvaffaqiyatli o'tadi
  - project-level smoke testlar `src/tests/` ostida default Django test workflow bilan ishlaydi
  - Verification (2026-04-09):
    - `python3 src/manage.py check` -> `System check identified no issues (0 silenced).`
    - `python3 src/manage.py test` -> `Ran 7 tests ... OK` va `Found 7 test(s).`
