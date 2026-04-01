# agents.md

## 1. Loyiha haqida umumiy ma’lumot

**Ishchi nom:** CarCare Bot Platform

Ushbu loyiha — bu **Telegram ichida ishlaydigan, production-ready, avtomobil texnik xizmat va xarajatlar hisobi platformasi**. Foydalanuvchi asosiy ishlarning barchasini Telegram’dan chiqmasdan bajaradi. Alohida mobil ilova yoki web kabinet v1 uchun majburiy emas.

Platforma foydalanuvchiga quyidagilarni imkonini beradi:
- bir yoki bir nechta mashina qo‘shish va boshqarish
- texnik xizmat, remont, diagnostika, sarf materiallari va boshqa xarajatlarni kiritish
- rasm, video, hujjat, ovozli xabar kabi media fayllarni biriktirish
- servis tarixi va xarajatlar tarixini ko‘rish
- bir mashinani boshqa foydalanuvchilar bilan ulashish
- bir mashina ustida bir nechta egalar yoki mas’ul shaxslar bilan ishlash
- har bir yozuv bo‘yicha **kim qo‘shgani** va **kim to‘lagani** ni saqlash
- kelajakda aqlli eslatmalar, tavsiyalar, OCR, AI yordamchi va analitika funksiyalarini qo‘shish

Tizim quyidagi biznes modelni qo‘llab-quvvatlashi kerak:
- **bitta user → ko‘p mashina**
- **bitta mashina → ko‘p user**
- kirish huquqi share/invite yoki tasdiqlash oqimi orqali boshqariladi

Tizim Docker ichida quyidagi stack’da quriladi:
- Nginx
- Django
- PostgreSQL
- Telegram bot worker (Django management command ko‘rinishida)
- Celery o‘rniga management command asosidagi background worker(lar)
- media fayllar uchun local volume, keyinroq S3-compatible storage’ga o‘tish imkoniyati bilan

Kod bazasi saqlab yurishga qulay, kengayishga tayyor, kuzatish oson va production deployment uchun mos bo‘lishi shart.

---

## 2. Loyiha maqsadlari

### Asosiy maqsadlar
1. Foydalanuvchiga Telegram’dan chiqmasdan mashina xarajatlari va servis tarixini yuritish imkonini berish.
2. Oddiy chat history emas, **structured data** yig‘ish.
3. Bir mashinaga bir nechta foydalanuvchi bilan xavfsiz ishlash imkonini berish.
4. Harajat, servis va audit tarixini ishonchli saqlash.
5. Bitta VPS’da Docker Compose bilan deploy qilinadigan yechim qurish.
6. Keyinchalik reminders, tavsiyalar, OCR, AI va analitika qo‘shishga tayyor arxitektura yaratish.

### v1 uchun non-goals
1. End-user uchun to‘liq web kabinet.
2. Payment processing.
3. Native mobil ilovalar.
4. Murakkab event-driven microservice arxitekturasi.
5. Real-time websocket dashboard.

---

## 3. Kelajak ko‘rinishi va strategik yo‘nalish

Bu loyiha oddiy “mashina xarajati bot” bo‘lib qolmasligi kerak. Arxitektura kelajakda quyidagilarni qo‘shishga tayyor bo‘lishi kerak:

### 3.1 Aqlli notification va proaktiv bot
Kelajakda bot foydalanuvchiga o‘zi yozishi kerak, masalan:
- “Salom, oxirgi odometr ma’lumoti eskirib qoldi, hozirgi probegni yuboring.”
- “Motor moyi almashtirilganiga 4 800 km bo‘ldi, yaqin orada almashtirish tavsiya qilinadi.”
- “Avtomat karobka moyi va filter bo‘yicha servis intervali yaqinlashmoqda.”
- “So‘nggi 3 oyda eng katta xarajat tormoz tizimiga ketgan.”

### 3.2 Odometrni rasm orqali yangilash
Kelajakda foydalanuvchi mashina paneli rasmini yuboradi va tizim:
- odometr raqamini OCR bilan aniqlaydi
- userga topilgan qiymatni ko‘rsatadi
- tasdiqlansa, odometr tarixiga yozadi

Bu v1’da shart emas, lekin arxitektura bunga tayyor bo‘lishi kerak.

### 3.3 Standartlarga asoslangan tavsiyalar
Kelajakda bot quyidagilar bo‘yicha maslahat bera olishi kerak:
- motor moyi almashtirish intervali
- mexanik karobka moyi intervali
- avtomat karobka moyi va filtri intervali
- tormoz suyuqligi
- antifriz
- GUR / рулевой suyuqlik
- svecha, filtrlar, ремень, цепь kabi elementlar

Bu tavsiyalar umumiy standartlar, mashina markasi/modeli, foydalanuvchi odati va oldingi tarixga asoslanishi mumkin.

### 3.4 Elektromobillarni qo‘llab-quvvatlash
Arxitektura ICE-only bo‘lib qolmasligi kerak. Kelajakda quyidagilarni qo‘shish oson bo‘lishi kerak:
- EV transport turi
- batareya holati
- charging history
- reduction gear / coolant / cabin filter kabi EV servis itemlari
- ICE va EV uchun alohida recommendation engine qoidalari

### 3.5 Usta ekotizimi / service marketplace
Kelajakda platformada faqat mashina egasi emas, **usta / servis nuqta / workshop provider** ham ishtirok eta olishi kerak. Bu qatlam taksi ilovasidagi haydovchi modeli kabi ishlaydi:
- usta o‘z servis profilini yaratadi
- servis nomi, logo, telefon, lokatsiya, ish vaqti, xizmat turlari, narx diapazoni va tavsifini qo‘shadi
- mijozlar ustani topadi, ko‘radi va baholaydi
- mijozlar bajarilgan ish sifati bo‘yicha review qoldiradi
- kelajakda servisga yozilish, navbat, booking va lead generation imkoniyatlari qo‘shilishi mumkin

Muhim talab: bu imkoniyatlar **Telegram botga qattiq bog‘lanmasligi kerak**. Domen logikasi alohida servis qatlamlarida bo‘ladi, bot esa ulardan faqat transport/integratsiya qatlami sifatida foydalanadi.

### 3.6 AI yordamchi
Kelajakda bot:
- foydalanuvchi odatlaridan o‘rganishi
- servis tarixi asosida risklarni ko‘rsatishi
- media receipt / servis orderlardan ma’lumot ajratishi
- “menga oxirgi marta qachon karobka moyi almashtirilganini ayt” kabi savollarga javob bera olishi mumkin
- usta tanlashda review, narx, joylashuv va servis tarixiga qarab tavsiyalar bera olishi mumkin

AI qismi boshidan optional modul sifatida ko‘zda tutiladi. Agar bepul yoki arzon model topilsa, u provider adapter orqali ulanadi. Agar model bo‘lmasa, tizim rule-based rejimda ishlashda davom etadi.

Shu sababli arxitektura boshidan **modulli, domain-driven va kengaytiriladigan** bo‘lishi shart.

---

## 4. Biznes domen

### Asosiy entity’lar
- **User**
- **TelegramAccount**
- **Car**
- **CarMembership**
- **VehicleProfile**
- **MaintenanceRecord**
- **MaintenanceLineItem**
- **ExpenseRecord** (keyinchalik standalone xarajatlar uchun)
- **MediaAsset**
- **ServiceType**
- **Part / Consumable**
- **Workshop / Vendor**
- **WorkshopProfile**
- **WorkshopService**
- **WorkshopLocation**
- **WorkshopReview**
- **OdometerEntry**
- **ReminderRule**
- **RecommendationRule**
- **NotificationEvent**
- **AuditLog**
- **BotConversationState**
- **AIInteractionLog**
- **AIProviderConfig**

### Domen qoidalari
1. User’da bir nechta mashina bo‘lishi mumkin.
2. Bitta mashinani bir nechta user ko‘rishi mumkin.
3. Har bir yozuvda albatta quyidagilar bo‘lishi kerak:
   - kim yaratgan
   - kim to‘lagan
   - qachon yaratilgan
   - qachon o‘zgartirilgan
4. Media fayllar tegishli yozuvga mustahkam bog‘langan bo‘lishi kerak.
5. Odometr servis yozuvlari ichida ham, mustaqil tarix sifatida ham yuritilishi mumkin.
6. Mashina access huquqi role-based bo‘lishi kerak.
7. Tizim doim quyidagi savollarga javob bera olishi kerak:
   - buni kim qo‘shgan?
   - buni kim to‘lagan?
   - bu qaysi mashinaga tegishli?
   - nima o‘zgargan?
8. Telegram holatlari DB’da saqlanishi kerak, bot restart bo‘lsa ham flow yo‘qolmasligi kerak.

---

## 5. User story’lar

### Onboarding
- Telegram user botni boshlab, avtomatik account yaratishni xohlaydi.
- User mashinasini davlat raqami va metadata bilan qo‘shishni xohlaydi.
- User o‘z mashinalarini tez ko‘rishni xohlaydi.

### Birgalikda boshqarish
- User mashinasini boshqa user bilan ulashishni xohlaydi.
- Yangi user invite token yoki tasdiqlash oqimi orqali access olishni xohlaydi.
- Share qilingan user ham tarixni ko‘ra olishi kerak.
- Owner kim edit qila olishi, kim faqat ko‘rishini boshqarishni xohlaydi.

### Servis kiritish
- User Telegram ichida step-by-step servis yozuvi kiritishni xohlaydi.
- User sana, odometr, servis turi, izoh, workshop, summalar va note qo‘shishni xohlaydi.
- User rasm/video/hujjat biriktirishni xohlaydi.
- User part cost va labor cost’ni alohida kiritishni xohlaydi.
- User yozuvni o‘zi qo‘shgan bo‘lsa ham, to‘lovni boshqa odam nomiga yozishni xohlaydi.

### Tarix va hisobot
- User har bir mashina bo‘yicha timeline ko‘rishni xohlaydi.
- User date range, service type yoki keyword bo‘yicha filter qilishni xohlaydi.
- User jami xarajatni ko‘rishni xohlaydi.
- User workshop, detal nomi yoki probeg bo‘yicha qidirishni xohlaydi.

### Aqlli yordam
- User botning o‘zi eslatma yuborishini xohlaydi.
- User mashina paneli rasmini yuborib odometr yangilashni xohlaydi.
- User servis tavsiyalarini olishni xohlaydi.
- User kelajakda elektromobil uchun ham bir xil qulaylikni xohlaydi.

---

## 6. Yuqori darajadagi arxitektura

### Arxitektura prinsipi
Loyiha **bot-first**, lekin **bot-bound** bo‘lmasligi kerak.

Ya’ni:
- business logic Telegram handler ichida yashamaydi
- barcha muhim use-case’lar service layer orqali bajariladi
- bot, web, mobile app yoki admin panel bir xil service/policy/selectorga tayanadi
- Telegram faqat birinchi client/interface bo‘ladi

### Runtime komponentlar
1. **nginx**
   - reverse proxy
   - static/media serving
   - TLS termination
   - Django app’ga routing

2. **django app**
   - Django REST Framework API
   - Django admin
   - domain logic
   - auth / permissions
   - bot orchestration uchun ichki servislar
   - webhook endpoint’lar (keyinroq kerak bo‘lsa)
   - management command entrypoint’lar

3. **postgres**
   - asosiy relational ma’lumotlar ombori
   - transactional consistency

4. **telegram bot worker**
   - dastlab polling yoki keyin webhook
   - Django management command sifatida ishlaydi
   - update qabul qiladi, handler’larga uzatadi, flow state boshqaradi, javob qaytaradi

5. **background worker**
   - Django management command sifatida ishlaydi
   - reminder, notification, cleanup, OCR queue, recommendation queue kabi ishlarni bajaradi

6. **AI adapter layer (optional)**
   - provider abstraction
   - free/local model yoki tashqi API’ga ulanish imkoniyati
   - rule-based fallback bilan birga ishlashi

### Deploy modeli
Bitta VPS, Docker Compose asosida.

### Tavsiya qilinadigan container’lar
- `nginx`
- `web` (gunicorn + Django)
- `bot`
- `worker`
- `db`
- keyinroq `backup` yoki `cron` container qo‘shilishi mumkin

## 7. Repository strukturasi

```text
repo/
├── agents.md
├── README.md
├── .env.example
├── docker-compose.yml
├── infra/
│   ├── nginx/
│   │   ├── nginx.conf
│   │   └── conf.d/
│   ├── postgres/
│   └── scripts/
├── src/
│   ├── manage.py
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── local.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/
│   │   ├── users/
│   │   ├── telegram/
│   │   ├── cars/
│   │   ├── maintenance/
│   │   ├── expenses/
│   │   ├── media_assets/
│   │   ├── workshops/
│   │   ├── reminders/
│   │   ├── recommendations/
│   │   ├── odometer/
│   │   ├── notifications/
│   │   ├── audit/
│   │   └── common/
│   ├── services/
│   ├── selectors/
│   ├── policies/
│   ├── bot/
│   │   ├── handlers/
│   │   ├── keyboards/
│   │   ├── flows/
│   │   ├── formatters/
│   │   └── routers/
│   └── templates/
├── rules/
│   ├── backend.md
│   ├── django.md
│   ├── telegram_bot.md
│   ├── database.md
│   ├── docker_ops.md
│   ├── security.md
│   ├── testing.md
│   └── product_rules.md
└── issue_tracking/
    ├── tasks/
    │   ├── todo/
    │   ├── active/
    │   └── done/
    ├── sprints/
    │   ├── sprint-001-foundation.md
    │   ├── sprint-002-core-domain.md
    │   └── sprint-003-bot-v1.md
    ├── backlog.md
    ├── roadmap.md
    └── conventions.md
```

---

## 8. Domen model draft

### 8.1 User
Ilova user’i.

Maydonlar:
- id
- full_name
- phone_number (boshlanishida optional)
- is_active
- created_at
- updated_at

### 8.2 TelegramAccount
Telegram identifikatori bilan local user mapping.

Maydonlar:
- id
- user
- telegram_user_id (unique)
- username
- first_name
- last_name
- language_code
- chat_id
- is_blocked
- last_seen_at
- created_at
- updated_at

### 8.3 Car
Mashina.

Maydonlar:
- id (UUID)
- plate_number
- normalized_plate_number
- brand
- model
- generation
- year
- vin (optional)
- nickname (optional)
- powertrain_type (`ice`, `hybrid`, `ev`)
- current_odometer
- color (optional)
- notes
- is_active
- created_at
- updated_at

Cheklovlar:
- normalized plate indexed bo‘lishi kerak
- vin bo‘lsa unique bo‘lishi kerak
- powertrain type kelajakdagi EV support uchun hozirdanoq mavjud bo‘lsin

### 8.4 VehicleProfile
Mashina turi bo‘yicha tavsiyalar va servis qoidalari uchun metadata profili.

Maydonlar:
- id
- car
- engine_type
- transmission_type (`manual`, `automatic`, `cvt`, `dct`, `ev_reducer`, `other`)
- engine_displacement
- fuel_type
- drivetrain
- battery_capacity (EV uchun optional)
- custom_notes
- created_at
- updated_at

Bu entity recommendation engine uchun kerak bo‘ladi.

### 8.5 CarMembership
User va car o‘rtasidagi many-to-many bog‘lanish.

Maydonlar:
- id
- car
- user
- role (`owner`, `manager`, `viewer`)
- status (`active`, `pending`, `revoked`)
- invited_by
- joined_at
- created_at
- updated_at

Qoidalar:
- ko‘p owner bo‘lishi mumkin
- access role’ga asoslangan
- membership o‘zgarishlari audit qilinadi

### 8.6 MaintenanceRecord
Bitta servis yoki remont hodisasi.

Maydonlar:
- id (UUID)
- car
- service_type
- event_date
- odometer
- title
- description
- workshop
- total_amount_cached
- created_by
- paid_by_user (nullable)
- paid_by_label (nullable)
- source (`telegram`, `admin`, `system`)
- status (`draft`, `final`)
- created_at
- updated_at

### 8.7 MaintenanceLineItem
Servis ichidagi alohida qatorlar.

Maydonlar:
- id
- maintenance_record
- item_type (`part`, `labor`, `service`, `fee`, `fluid`, `filter`, `other`)
- name
- quantity
- unit_price
- total_price
- paid_by_user (nullable)
- paid_by_label (nullable)
- notes
- created_at
- updated_at

Maqsad:
- part / labor split
- bir event ichida ko‘p item saqlash
- kelajakda recommendation engine bilan bog‘lash

### 8.8 OdometerEntry
Odometr tarixini alohida yuritish.

Maydonlar:
- id
- car
- value
- entry_date
- source (`manual`, `maintenance_record`, `ocr`, `system`)
- image (nullable)
- confidence_score (OCR uchun nullable)
- created_by
- created_at

Bu keyinchalik panel rasmidan update qilish uchun juda muhim.

### 8.9 ReminderRule
Eslatma qoidalari.

Maydonlar:
- id
- car
- service_type
- trigger_type (`mileage`, `days`, `months`, `hybrid`)
- threshold_value
- lead_value
- is_active
- created_at
- updated_at

### 8.10 RecommendationRule
Tavsiyalar engine’i uchun qoida.

Maydonlar:
- id
- powertrain_type
- transmission_type
- service_code
- min_interval_km
- max_interval_km
- min_interval_days
- max_interval_days
- severity
- description
- is_active
- created_at
- updated_at

Bu qoida orqali masalan motor moyi, ATF, filterlar bo‘yicha tavsiya berish mumkin bo‘ladi.

### 8.11 NotificationEvent
Bot yuborgan yoki yuboriladigan notificationlar.

Maydonlar:
- id
- user
- car
- notification_type
- title
- body
- payload (JSON)
- status (`pending`, `sent`, `failed`, `cancelled`)
- scheduled_for
- sent_at
- created_at

### 8.12 MediaAsset
Media fayllar.

Maydonlar:
- id (UUID)
- owner_user
- uploaded_by
- file
- media_type (`image`, `video`, `document`, `audio`, `voice`)
- file_size
- mime_type
- checksum
- telegram_file_id (nullable)
- telegram_file_unique_id (nullable)
- linked_content_type
- linked_object_id
- caption
- created_at

### 8.13 Workshop
Ustaxona / vendor.

Maydonlar:
- id
- name
- phone_number
- address
- notes
- created_by
- created_at
- updated_at

### 8.14 WorkshopProfile
Usta yoki servis provider’ning ommaviy profili.

Maydonlar:
- id
- owner_user
- display_name
- logo
- description
- phone_number
- telegram_contact
- is_verified
- average_rating_cached
- total_reviews_cached
- created_at
- updated_at

### 8.15 WorkshopLocation
Servis joylashuvi.

Maydonlar:
- id
- workshop_profile
- title
- address
- latitude
- longitude
- landmark
- is_active
- created_at
- updated_at

### 8.16 WorkshopService
Usta ko‘rsatadigan xizmatlar katalogi.

Maydonlar:
- id
- workshop_profile
- service_code
- title
- description
- base_price_from
- base_price_to
- is_active
- created_at
- updated_at

### 8.17 WorkshopReview
Mijozlar bahosi.

Maydonlar:
- id
- workshop_profile
- user
- car (nullable)
- rating
- comment
- related_maintenance_record (nullable)
- created_at
- updated_at

Qoidalar:
- review’lar moderatsiya qilinishi mumkin
- cached rating async yoki transaction ichida yangilanadi
- future’da verified-review mexanizmi qo‘shilishi mumkin

### 8.18 AuditLog
Audit trail.

Maydonlar:
- id
- actor_user
- actor_telegram_account
- action
- target_type
- target_id
- before_snapshot (JSON)
- after_snapshot (JSON)
- request_id / correlation_id
- created_at

### 8.19 AIProviderConfig
AI provider konfiguratsiyasi.

Maydonlar:
- id
- provider_code
- model_name
- endpoint
- is_active
- priority
- settings_json
- created_at
- updated_at

### 8.20 AIInteractionLog
AI bilan bo‘lgan interaction log’lari.

Maydonlar:
- id
- user
- car (nullable)
- interaction_type
- input_payload
- output_payload
- provider_code
- model_name
- status
- created_at

### 8.21 BotConversationState
Telegram flow state.

Maydonlar:
- id
- telegram_account
- flow_name
- state_name
- state_payload (JSON)
- expires_at
- created_at
- updated_at

---

## 9. Telegram interaction modeli

### Asosiy menyu
- Mening mashinalarim
- Mashina qo‘shish
- Servis qo‘shish
- Tarix
- Xarajatlar
- Odometr yangilash
- Ulashish
- Eslatmalar
- Tavsiyalar
- Sozlamalar
- Yordam

### Servis kiritish flow
1. User mashinani tanlaydi.
2. Bot servis sanasini so‘raydi.
3. Bot odometrni so‘raydi.
4. Bot servis kategoriyasini so‘raydi.
5. Bot qisqa sarlavha yoki izohni so‘raydi.
6. Bot line item’larni so‘raydi:
   - part / labor / fluid / filter / other
   - amount
   - optional payer
7. Bot workshop’ni so‘raydi.
8. Bot qo‘shimcha note’ni so‘raydi.
9. Bot media fayllarni qabul qiladi.
10. Bot summary ko‘rsatadi.
11. User tasdiqlaydi.
12. Record final bo‘ladi va audit log yoziladi.

### Odometr yangilash flow (v1 / future-ready)
#### v1
- user odometrni qo‘lda kiritadi
- tizim OdometerEntry yaratadi

#### future
- user panel rasmini yuboradi
- OCR queue’ga tushadi
- tizim topgan qiymatni tasdiqlash uchun yuboradi
- tasdiqlansa OdometerEntry yoziladi

### Access ulashish flow
v1 uchun tavsiya:
1. Telegram deep link token orqali invite
2. Mashina uchun time-limited share token
3. Plate bo‘yicha request yuborish + owner tasdiqlashi

Muhim: **faqat bir xil davlat raqami kiritgani uchun avtomatik access berilmaydi**. Bu security/privacy risk.

---

## 10. Permission modeli

### Owner
Qila oladi:
- mashinani ko‘rish
- mashinani edit qilish
- membership boshqarish
- record qo‘shish/edit/delete qilish
- barcha media va xarajatlarni ko‘rish
- reminder sozlash

### Manager
Qila oladi:
- mashinani ko‘rish
- record qo‘shish/edit qilish
- media yuklash
- tarixni ko‘rish
- reminderlarni ko‘rish
- owner’larni boshqara olmaydi

### Viewer
Qila oladi:
- mashinani ko‘rish
- tarix va media’ni ko‘rish
- edit qila olmaydi

Barcha write action’lar object-level authorization bilan tekshiriladi.

---

## 11. Bot processing strategiyasi

### Update ingestion
Bitta token uchun bitta update consumer.

Talablar:
- idempotent processing
- duplicate update protection
- restart-safe ishlash
- structured exception logging
- Telegram API transient xatolari uchun retry

### Management command’lar
Boshlang‘ich command’lar:
- `runbot` — Telegram update loop
- `runworker` — scheduled va queued ishlar
- `send_notifications` — pending notificationlarni yuborish
- `process_reminders` — reminder event yaratish
- `cleanup_expired_states` — eski state’larni tozalash
- `process_odometer_ocr` — keyinroq OCR queue uchun
- `process_recommendations` — keyinroq tavsiyalar hisoblash uchun

### Celery’siz background ishlar
Worker quyidagilarni qila olishi kerak:
- simple scheduler loop
- DB-backed job queue’ni o‘qish
- reminder task’lar
- cleanup task’lar
- media post-processing
- OCR task’lar
- recommendation refresh task’lar

Talablar:
- restart-safe
- iloji boricha idempotent
- health/logging hook’lari bor
- correctness uchun faqat RAM ichidagi state’ga bog‘lanmagan bo‘lishi kerak

---

## 12. Ichki qatlamlar va kod chegaralari

Django ichida qatlamlar aniq ajratiladi.

### Models
- persistence schema
- minimal logika

### Services
- write-side orchestration
- transaction boshqaruvi
- business qoidalar

### Selectors
- read-side query logika
- optimized queryset’lar

### Policies
- permission decision’lar
- role check’lar
- access qoidalari

### Bot handlers
- faqat Telegram interaction qatlami
- business logic handler ichida bo‘lmaydi
- handler faqat service / selector / policy chaqiradi

### Tavsiya etiladigan service modullari
- `car_service`
- `membership_service`
- `maintenance_service`
- `expense_service`
- `odometer_service`
- `media_service`
- `notification_service`
- `reminder_service`
- `recommendation_service`
- `workshop_service`
- `review_service`
- `ai_service`

### Future extension modules
Quyidagilarni keyin qo‘shish oson bo‘lishi kerak:
- OCR provider adapter’lari
- recommendation engine
- EV-specific service rules
- AI summary / assistant layer
- usta marketplace va booking layer
- export modul

Bu ajratish maintainability uchun majburiy.

---

## 13. Media handling talablari

Qo‘llab-quvvatlanadigan media:
- image
- video
- document
- voice/audio

v1 strategiya:
- media local persistent Docker volume’da saqlanadi
- DB’da metadata yoziladi
- Telegram file metadata saqlanadi

Qoidalar:
- file size va type validation
- filename sanitization
- client yuborgan MIME’ga to‘liq ishonilmaydi
- deterministic storage path
- Nginx media’ni xavfsiz serve qiladi

Future-ready:
- S3/MinIO’ga o‘tish qiyin bo‘lmasligi kerak
- OCR pipeline media metadata’dan foydalana olishi kerak

---

## 14. Data integrity va consistency talablari

1. Muhim write’lar transaction ichida bajariladi.
2. Plate normalization deterministic bo‘lishi kerak.
3. Telegram duplicate update sababli bir xil maintenance record ikki marta yaratilmasligi kerak.
4. Kritik business record’lar uchun soft-delete afzal.
5. Audit trail append-only bo‘lishi kerak.
6. Car’dagi `current_odometer` cached bo‘lishi mumkin, lekin source of truth — odometer history.
7. Membership o‘zgarishlari explicit va audit qilinadigan bo‘lishi kerak.
8. Reminder va notification event’lar ikki marta yuborilmasligi kerak.

---

## 15. Non-functional talablar

### Xavfsizlik
- secret’lar `.env` orqali
- production’da debug o‘chiq
- admin himoyalangan
- HTTPS majburiy
- upload validation majburiy
- least privilege
- rate limiting ko‘rib chiqiladi

### Ishonchlilik
- web/bot/worker healthcheck
- structured logs
- restart-safe loop’lar
- migration’lar nazorat ostida
- backup strategiya documented

### Performance
- ko‘p ishlatiladigan query’lar optimallashtiriladi
- plate, telegram_user_id, membership, event_date, odometer, notification status uchun index’lar
- N+1 yo‘q
- history paginated

### Kuzatuvchanlik
- request/correlation ID
- container log’lari aniq ajratilgan
- bot log’larida kerakli context bor
- secret leak bo‘lmaydi

### Maintainability
- strict code review qoidalari
- typed Python imkon qadar
- shared utility’lar markazlashgan
- business logic testlanadi
- markdown hujjatlar doim yangilanadi

---

## 16. Bosqichma-bosqich milestone’lar

### Milestone 1 — Foundation
- repo strukturasi
- Docker Compose
- Django bootstrap
- PostgreSQL integration
- settings split
- nginx config
- health endpoint’lar
- base user va Telegram account modellari

### Milestone 2 — Core domain
- car model
- membership
- maintenance record
- line item’lar
- media asset
- odometer entry
- admin setup
- audit log

### Milestone 3 — Telegram bot v1
- start/help/menu
- add car flow
- list cars
- add maintenance flow
- history flow
- media upload flow
- odometer manual update flow

### Milestone 4 — Collaboration
- invite/share flow
- role-based access
- payer vs creator tracking
- history visibility

### Milestone 5 — Reminder engine
- reminder rule
- reminder evaluation
- notification event yaratish
- Telegram notification yuborish

### Milestone 6 — Smart features foundation
- OdometerEntry source model tayyor
- OCR pipeline uchun queue skeleti
- recommendation rule modeli
- vehicle profile metadata
- ICE / EV extensibility

### Milestone 7 — Hardening
- testlar
- seed data
- backup script’lar
- deployment docs
- operational runbook’lar

---

## 17. Definition of done

Task yoki feature done hisoblanadi, agar:
1. kod yozilgan bo‘lsa
2. migration yaratilgan bo‘lsa
3. kerakli joylarda admin integration bo‘lsa
4. testlar qo‘shilgan yoki yangilangan bo‘lsa
5. docs yangilangan bo‘lsa
6. logging va error handling qoniqarli bo‘lsa
7. permission tekshiruvlari mavjud bo‘lsa
8. edge case’lar ko‘rib chiqilgan bo‘lsa
9. Docker local muhitida ishlasa
10. issue tracking ichida holati to‘g‘ri yangilangan bo‘lsa

---

## 18. AI agentlar uchun ishlash qoidalari

AI agentlar ushbu loyihada quyidagilarga rioya qilishi kerak:
1. Handler, service, selector, policy qatlamlarini aralashtirmaslik.
2. Business rule’larni Telegram handler ichiga yozmaslik.
3. Celery qo‘shmaslik, agar alohida tasdiq bo‘lmasa.
4. Keraksiz microservice arxitekturaga ketmaslik.
5. Sensitive write action’larda audit log’ni chetlab o‘tmaslik.
6. Davlat raqamini authorization isboti sifatida yakka ishlatmaslik.
7. Multi-step write’larda explicit transaction ishlatish.
8. Tashqi/business identifier’lar uchun UUID afzal ko‘rish.
9. Demo-style emas, production-style kod yozish.
10. Har bir katta o‘zgarish issue tracking task’iga bog‘langan bo‘lishi.
11. Future feature’lar uchun extensibility’ni buzadigan shortcut’lardan qochish.

---

## 19. Keyin hal qilinadigan ochiq savollar

1. Davlat raqami formati country-specific bo‘ladimi yoki generic?
2. v1’da nechta til bo‘ladi?
3. Reminder’lar mileage-based, time-based yoki ikkalasi bo‘ladimi?
4. Standalone expense (yoqilg‘i, sug‘urta, jarima, soliq) v1’da bo‘ladimi?
5. OCR uchun qaysi provider yoki local model ishlatiladi?
6. Recommendation data manual rule-based bo‘ladimi yoki tashqi dataset bo‘ladimi?
7. EV support qaysi milestone’da boshlanadi?
8. Workshop marketplace qaysi milestone’da ochiladi?
9. Review’lar faqat servisdan keyin qoldiriladimi yoki umumiy ham bo‘ladimi?
10. AI provider sifatida local model, free hosted API yoki gibrid variant ishlatiladimi?

## 20. Yakuniy engineering pozitsiya

Bu tizim oddiy demo bot emas. U bitta VPS’da ishlaydigan, lekin ichki arxitekturasi toza, kengaytiriladigan va audit qilinadigan **Telegram-first automotive maintenance platform** bo‘lishi kerak.

Har bir texnik qaror quyidagi mezonlar bo‘yicha baholanadi:
- toza domain boundary
- xavfsiz collaboration
- recoverable operation
- future extensibility
- auditability
- Telegram-first UX
- smart feature’larni keyin qo‘shishda og‘riq bermaslik

Loyiha hozirdan shunday qurilishi kerakki, keyin reminders, OCR, recommendation engine, EV support va AI layer qo‘shilganda arxitektura sinib ketmasin.
