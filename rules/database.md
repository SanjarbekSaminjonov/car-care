# Database Rules

## 1. Maqsad

Ushbu hujjat ma’lumotlar bazasini (PostgreSQL) production-ready, izchil va kengaytiriladigan tarzda loyihalash va ishlatish qoidalarini belgilaydi.

Talablar:
- data integrity
- aniq schema
- izchil naming
- samarali indekslash
- transaction-safe yozuvlar
- audit va idempotency bilan moslik
- future extensibility (AI, OCR, marketplace, analytics)

---

## 2. Asosiy prinsiplar

1. **Schema — contract**: DB schema backend va kelajak clientlar uchun contract hisoblanadi.
2. **Source of truth**: Canonical jadval(lar) aniq bo‘ladi; cache fieldlar truth emas.
3. **Append > mutate** (zarur joyda): Odometer, audit, event kabi oqimlar append-onlyga yaqin bo‘ladi.
4. **Explicitness**: status/source/type fieldlar aniq enum bilan.
5. **Idempotency**: tashqi eventlar (Telegram) uchun dedup mexanizmi.
6. **Performance-aware design**: indekslar va query patternlar boshidan o‘ylanadi.

---

## 3. Engine va umumiy sozlamalar

- DB: PostgreSQL (>= 13 tavsiya)
- Charset: UTF-8
- Timezone: UTC
- Connection pooling (keyinroq): pgbouncer yoki gunicorn worker tuning

---

## 4. Naming qoidalari

### 4.1 Jadval nomlari
- `snake_case`, ko‘plik shakli ixtiyoriy, lekin izchil bo‘lsin (tavsiya: ko‘plik)
- misol: `cars`, `maintenance_records`, `workshop_profiles`

### 4.2 Ustun nomlari
- `snake_case`
- FK: `<entity>_id`
- vaqt: `created_at`, `updated_at`, `deleted_at`

### 4.3 Constraint nomlari
- `uq_<table>_<cols>`
- `idx_<table>_<cols>`
- `fk_<table>_<ref_table>_<col>`

---

## 5. Asosiy entitylar (qisqa)

- users
- telegram_accounts
- cars
- car_memberships
- maintenance_records
- maintenance_line_items
- odometer_entries
- media_assets
- workshops / workshop_profiles / workshop_services / workshop_locations
- workshop_reviews
- notifications / notification_events
- reminder_rules / recommendation_rules
- audit_logs
- bot_conversation_states
- ai_interactions / ai_provider_configs

---

## 6. Primary key va identifikatsiya

- Muhim entitylar: UUID PK (`uuid_generate_v4()` yoki app-level UUID)
- Internal lookup: integer PK mumkin
- Tashqi eventlar uchun: `external_id` / `source_event_id`

---

## 7. Relatsiyalar

- FKlar aniq va `on_delete` semantikasi o‘ylangan:
  - `PROTECT` (ko‘p hollarda)
  - `SET NULL` (optional bog‘lanish)
  - `CASCADE` faqat to‘liq bog‘liq bolalar uchun
- Many-to-many o‘rniga explicit through model (masalan `car_memberships`)

---

## 8. Status va enumlar

- `TextChoices`/enum bilan:
  - `status`
  - `source`
  - `role`
- Boolean bilan murakkab state ifodalashdan qochish

---

## 9. Timestamplar

- `created_at` (default now)
- `updated_at` (auto)
- Event jadvalda faqat `created_at` yetarli bo‘lishi mumkin
- Timezone-aware (UTC)

---

## 10. Soft delete

- Default emas
- Qo‘llansa:
  - `deleted_at` ishlatiladi
  - selectorlar filtrlaydi
  - unique constraintlar partial index bilan hal qilinadi

---

## 11. Indekslar

### 11.1 Asosiy indekslar
- FK ustunlar
- `created_at` bo‘yicha timeline
- tez-tez filtrlanadigan fieldlar (`status`, `car_id`, `user_id`)

### 11.2 Composite indekslar
- `(car_id, created_at desc)`
- `(status, scheduled_for)`
- `(workshop_profile_id, created_at desc)`

### 11.3 Partial indekslar
- faqat `status='pending'` notificationlar
- `deleted_at IS NULL` soft delete holatlari

---

## 12. Uniqueness va constraintlar

- `normalized_plate_number` unique (yoki country+plate)
- `car_memberships (car_id, user_id)` unique
- idempotency uchun:
  - `(source, external_id)` unique
- review policy bo‘lsa:
  - `(user_id, workshop_profile_id, related_maintenance_record)` unique (agar kerak)

---

## 13. Idempotency

- Telegram update uchun:
  - `processed_updates` jadvali yoki event_id saqlash
- Notification:
  - dedup key (masalan `(user_id, car_id, rule_id, period)`)

---

## 14. Transactionlar

- Multi-step write har doim transaction ichida
- DB write → commit → tashqi side-effect (send/AI/OCR)
- Long-running external call transaction ichida qilinmaydi

---

## 15. Audit

- `audit_logs`:
  - `actor_user_id`
  - `action`
  - `target_type`, `target_id`
  - `before_snapshot`, `after_snapshot`
  - `correlation_id`
  - `created_at`
- Snapshotlar ixcham, lekin tushunarli

---

## 16. Odometer modeli

- `odometer_entries` append-only
- constraint:
  - yangi qiymat avvalgisidan kichik bo‘lmasligi (service-level)
- `cars.current_odometer` — cache field

---

## 17. Media

- DB’da metadata:
  - `file_path`
  - `mime_type`
  - `size`
  - `checksum`
- Storage almashuviga tayyor (local → S3/MinIO)

---

## 18. Notification modeli

- `notification_events`:
  - `status`: pending/sent/failed/cancelled
  - `scheduled_for`
  - `dedup_key`
- Worker yuboradi, handler emas

---

## 19. Performance

- N+1 yo‘q (selector orqali prefetch)
- Pagination majburiy (list endpoint/flowlarda)
- Heavy aggregation cached bo‘lishi mumkin

---

## 20. Migration strategiyasi

- Har schema o‘zgarishi migration bilan
- Migration ko‘rib chiqiladi (rename/drop ehtiyotkor)
- Katta jadval o‘zgarishlari:
  - backfill/batch
  - downtime baholash
- Data migration alohida reja bilan

---

## 21. Backup va recovery

- Muntazam backup (daily snapshot)
- Restore testlari vaqti-vaqti bilan tekshiriladi
- Muhim o‘zgarishlar oldidan qo‘lda backup

---

## 22. Security

- Least privilege DB user
- Credentials env orqali
- Audit va loglarda maxfiy ma’lumotlar chiqmaydi
- PII minimal saqlanadi (kerakli darajada)

---

## 23. AI agentlar uchun qoidalar

1. Schema’ni “tezroq bo‘lsin” deb soddalashtirib buzma.
2. Enum o‘rniga random string ishlatma.
3. Unique/constraintlarni unutma.
4. N+1 keltirib chiqaradigan query yozma (selector ishlat).
5. Idempotencyni e’tiborsiz qoldirma.
6. Migrationni tekshirmasdan commit qilma.
7. Soft delete’ni hamma joyga qo‘llama.
8. FK `on_delete`ni ongli tanla.
9. Audit talab qilingan joyda audit yozilishini unutma.
10. Future (AI/OCR/marketplace) kengayishini bloklaydigan schema qaror qabul qilma.

---

## 24. Anti-patternlar

- “misc_data” yoki JSON ichiga hamma narsani tiqish
- FK o‘rniga string id saqlash
- constraintlarsiz schema
- statusni boolean bilan ifodalash
- migrationni tekshirmasdan qo‘shish
- duplicate eventlarni nazorat qilmaslik

---

## 25. Definition of database done

Done hisoblanadi, agar:
1. Schema aniq va izchil
2. Indekslar o‘ylangan
3. Constraintlar qo‘llangan
4. Transaction boundary to‘g‘ri
5. Idempotency ko‘rib chiqilgan
6. Audit mavjud
7. Migration to‘g‘ri yozilgan
8. Future kengayish uchun joy qoldirilgan

---

## 26. Yakuniy prinsip

Database — tizimning eng barqaror qatlami.

Har bir qaror quyidagiga javob berishi kerak:

**Bu schema keyinchalik yangi feature qo‘shishni osonlashtiryaptimi yoki qiyinlashtiryaptimi?**
