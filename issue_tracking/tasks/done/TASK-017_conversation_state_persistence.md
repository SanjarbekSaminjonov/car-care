# TASK-017: Conversation state persistence

## Description

Bot multi-step flowlarining holatini DB'da saqlash uchun foundation qo'shish.

---

## Requirements

- `BotConversationState` modeli
- flow_name/state_name/state_payload maydonlari
- expiry timestamp
- state save/load/clear service helperlar

---

## Acceptance Criteria

- state restart-safe holda DB'dan tiklanadi
- bir user/chat uchun active state o'qilishi mumkin
- expired state cleanup uchun minimal helper mavjud
- model/service testlar yozilgan

---

## Notes

- RAM-only state qabul qilinmaydi

- Completed:
  - `BotConversationState` modeli qo'shildi (flow_name/state_name/payload/expires_at)
  - state service helperlar qo'shildi (`save/get/clear/cleanup`)
  - car/maintenance/odometer flowlar state'ni DB service orqali boshqaradigan qilindi
  - conversation state service testlari qo'shildi
