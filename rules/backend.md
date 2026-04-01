# Backend Rules

## 1. Maqsad

Ushbu hujjat loyiha backend qismini production-ready, kengaytiriladigan va aniq qoidalarga asoslangan holda yozish uchun asosiy texnik standartlarni belgilaydi.

Bu loyiha:
- demo emas
- faqat Telegram bot emas
- faqat CRUD panel emas
- keyinchalik web, mobile, AI, OCR, workshop marketplace va analytics qo‘shilishi mumkin bo‘lgan platforma

Shu sababli backend kodi:
- qatlamlarga ajratilgan
- use-case markazida yozilgan
- testlanadigan
- transportdan mustaqil
- transaction-safe
- audit qilinadigan
- idempotent
- extensible

bo‘lishi shart.

Bu hujjat AI agentlar, developerlar va review qiluvchilar uchun majburiy standart hisoblanadi.

---

## 2. Asosiy arxitektura tamoyili

### 2.1 Transport qatlamlari domen logikasidan ajralgan bo‘lishi shart

Telegram bot, admin action, management command worker va keyinchalik API endpointlar — bularning barchasi **transport / orchestration entrypoint** hisoblanadi.

Ular:
- input oladi
- uni normalizatsiya qiladi
- kerakli service yoki selector’ni chaqiradi
- natijani formatlaydi
- user yoki tashqi tizimga qaytaradi

Ular quyidagilarni qilmasligi kerak:
- murakkab business rule saqlamasligi
- katta write orchestration qilmasligi
- query optimizatsiya logikasini o‘zida saqlamasligi
- permission qarorini mustaqil yozmasligi
- boshqa transport qatlami uchun qayta ishlatib bo‘lmaydigan logika saqlamasligi

### 2.2 Core business logic service layer’da bo‘ladi

Barcha write/use-case logikasi service qatlamida yashaydi.

Misollar:
- mashina yaratish
- mashinaga access berish
- servis yozuvi yaratish
- line item qo‘shish
- odometr qiymatini yangilash
- reminder event yaratish
- notification yaratish
- workshop profili ochish
- review yozish
- AI/OCR natijasini saqlash
- tavsiya hisoblash

### 2.3 Read logic selector qatlamida bo‘ladi

Read/query logikasi selector’larda bo‘ladi.

Selector’lar:
- queryset yig‘adi
- filter qiladi
- annotate qiladi
- prefetch/select_related qiladi
- pagination uchun tayyorlaydi
- read model qaytaradi

Selector’lar write qilmaydi.

### 2.4 Authorization policy qatlamida bo‘ladi

Permission va access qarorlari policy qatlamida bo‘ladi.

Masalan:
- user bu mashinani ko‘ra oladimi
- user bu yozuvni edit qila oladimi
- user boshqa userga share bera oladimi
- user workshop review yozishga haqlimi
- worker bu action’ni user nomidan bajara oladimi

Policy logikasi takror yozilmaydi.

---

## 3. Tavsiya etilgan qatlamlar va javobgarlik chegaralari

Loyiha quyidagi qatlamlarga bo‘linadi:

- `apps/` — Django app’lar va persistence modeli
- `services/` — write/use-case orchestration
- `selectors/` — read/query logic
- `policies/` — authorization va access qoidalari
- `bot/handlers/` — Telegram update handlerlari
- `bot/flows/` — state machine / conversation flow
- `bot/formatters/` — Telegram response formatting
- `bot/keyboards/` — keyboard va interaction elementlari
- `common/` — shared helpers, types, base abstractions
- `integrations/` yoki `gateways/` — Telegram, OCR, AI, storage va boshqa provider adapterlari
- `audit/` — audit log yozish va snapshot yordamchilari
- `notifications/` — notification dispatch logikasi
- `tasks/` yoki service’lar bilan integratsiyalashgan worker logic — background task orchestration

Har bir qavatning mas’uliyati aniq bo‘lishi kerak. Qavatlar bir-birining ishini bosib ketmasligi kerak.

---

## 4. Hozirgi bosqichda API roli

### 4.1 Hozir API majburiy emas

Joriy bosqichda to‘liq public yoki internal HTTP API majburiy emas.

Sabab:
- asosiy interface — Telegram bot
- bot management command orqali ishlaydi
- worker management command orqali ishlaydi
- admin support/internal tool sifatida ishlaydi
- use-case’lar service layer orqali bajariladi

Demak hozirgi asosiy oqim:

- bot -> services
- worker -> services
- admin/internal flows -> services

### 4.2 Lekin arxitektura API-ready bo‘lishi shart

Kelajakda quyidagilar qo‘shilishi mumkin:
- mobile app
- web app
- public API
- internal partner integrations
- dashboard / backoffice

Shu sababli:
- business logic bot ichida qolib ketmasligi kerak
- response formatga bog‘lanmagan bo‘lishi kerak
- service layer transportdan mustaqil bo‘lishi kerak
- selector/policy qatlamlari qayta ishlatiladigan bo‘lishi kerak

### 4.3 API yozilsa ViewSet default bo‘lmaydi

Loyiha uchun default yondashuv:
- `ModelViewSet` ishlatmaslik
- `ViewSet` ishlatmaslik
- action’lar avtomatik yashirin bo‘lib ketadigan strukturadan qochish

Sabab:
- endpoint behavior nazorati susayadi
- permission handling tarqaladi
- serializer tanlash chalkashadi
- use-case markazi yo‘qoladi
- AI agentlar keraksiz “CRUD generator” uslubiga ketib qoladi

### 4.4 API yozilsa GenericAPIView oilasi ishlatiladi

API kerak bo‘lganda quyidagilar afzal:
- `CreateAPIView`
- `RetrieveAPIView`
- `ListAPIView`
- `UpdateAPIView`
- `DestroyAPIView`

yoki:

- `GenericAPIView`
- explicit `get/post/patch/delete`

Bu yondashuv:
- endpoint semantikasini aniq qiladi
- permissionlarni boshqarishni osonlashtiradi
- serializer tanlashni nazorat ostida ushlaydi
- use-case oriented API’ni qo‘llab-quvvatlaydi

### 4.5 API view’lar service adapter bo‘ladi

API view:
- request qabul qiladi
- serializer validate qiladi
- service chaqiradi
- response qaytaradi

API view ichida:
- murakkab business logic
- ko‘p model write orchestration
- qo‘lda transaction boshqaruvi
- bot yoki UI’ga xos text generation

bo‘lmasligi kerak.

---

## 5. Service layer qoidalari

### 5.1 Service nima

Service — bu bitta business use-case’ni bajaradigan qatlam.

Masalan:
- `create_car`
- `request_car_access`
- `approve_car_access_request`
- `create_maintenance_record`
- `register_odometer_entry`
- `create_workshop_review`
- `create_notification_event`
- `evaluate_reminder_rules`
- `accept_ai_extracted_odometer`

Service use-case markazida yoziladi, model markazida emas.

### 5.2 Service vazifalari

Service:
- input oladi
- kerakli policy’ni chaqiradi
- business validation qiladi
- transaction ochadi
- kerakli modellarni yaratadi yoki yangilaydi
- derived/cached field’larni yangilaydi
- audit log yozadi
- kerak bo‘lsa notification/job/event yaratadi
- natijani qaytaradi

### 5.3 Service nomlash qoidasi

Service nomi fe’l bilan boshlanishi kerak va use-case ni ifodalashi kerak.

Yaxshi:
- `create_car`
- `share_car_via_invite`
- `finalize_maintenance_record`
- `register_manual_odometer_entry`
- `schedule_due_notifications`

Yomon:
- `save_car`
- `process_data`
- `handle_everything`
- `update_stuff`

### 5.4 Service ichida nima bo‘lishi mumkin

Service ichida bo‘lishi mumkin:
- input normalization
- policy check
- business validation
- transaction
- model write
- audit log
- task/event yaratish
- cache refresh
- domain side-effectlarni rejalashtirish

### 5.5 Service ichida nima bo‘lmasligi kerak

Service ichida bo‘lmasligi kerak:
- Telegram message matnini formatlash
- inline keyboard qurish
- HTTP request parsing
- raw request object bilan ishlash
- HTML/JSON response yasash
- bot state rendering
- unrelated bulky query logic
- global mutable state

### 5.6 Service input/output standartlari

Service inputlari aniq bo‘lishi kerak:
- explicit keyword args
- typed params
- kerak bo‘lsa dataclass / DTO

Service result’lari ham aniq bo‘lishi kerak:
- model instance
- result dataclass/object
- yoki aniq documented return structure

Noaniq `dict` qaytarish default usul emas.

### 5.7 Service bir use-case uchun javobgar bo‘lsin

Bir service bir nechta aloqasiz use-case ni bajarmasligi kerak.

Masalan:
- `create_maintenance_record_and_send_message_and_update_all_stats_and_generate_dashboard`

kabi service qabul qilinmaydi.

Agar use-case katta bo‘lsa:
- orchestration service
- pastki service/helperlar

ga bo‘linadi, lekin chegaralar aniq bo‘ladi.

---

## 6. Selector qoidalari

### 6.1 Selector nima

Selector — read-only query qatlami.

Misollar:
- `get_user_cars`
- `get_car_detail_for_user`
- `list_car_maintenance_records`
- `get_latest_odometer_entry`
- `list_due_reminders`
- `search_workshops`
- `get_workshop_rating_summary`

### 6.2 Selector vazifalari

Selector:
- queryset quradi
- filtering qiladi
- ordering qiladi
- annotate qiladi
- aggregate qiladi
- `select_related` / `prefetch_related` ishlatadi
- read model yoki queryset qaytaradi

### 6.3 Selector write qilmaydi

Selector:
- `save()` qilmaydi
- audit log yozmaydi
- task yaratmaydi
- notification queue’ga yozmaydi
- model update qilmaydi

### 6.4 Murakkab query service ichida bo‘lmaydi

Service ichida query yig‘ib yuborish o‘rniga selector chaqiriladi.

Bu:
- testlashni osonlashtiradi
- reuse’ni oshiradi
- N+1 va performance nazoratini markazlashtiradi

---

## 7. Policy qoidalari

### 7.1 Policy majburiy

Object-level access bo‘lgan barcha use-case’larda policy ishlatiladi.

Masalan:
- user mashinani ko‘rishi
- user servis yozuvi yaratishi
- user share request approve qilishi
- user workshop profilini tahrirlashi
- user review qoldirishi

### 7.2 Policy natijasi

Policy:
- `True/False`
- yoki decision object
- yoki custom exception raise qiluvchi helper

ko‘rinishida bo‘lishi mumkin.

Murakkab joylarda decision object afzal.

### 7.3 Permission logikasi takror yozilmaydi

Bitta permission qoidasi:
- bot handlerda alohida
- API view’da alohida
- admin’da alohida

yozilmaydi.

Barchasi policy qatlamiga tayanadi.

### 7.4 Policy biznes qoidalar bilan yaqin, lekin service emas

Policy:
- “mumkinmi yoki yo‘qmi”ni hal qiladi

Service:
- “qanday bajariladi”ni hal qiladi

Bu ikki qatlam aralashib ketmasligi kerak.

---

## 8. Transaction qoidalari

### 8.1 Multi-step write transaction ichida bo‘ladi

Quyidagi holatlar transaction ichida bo‘lishi shart:
- maintenance record + line item + odometer + audit log
- access request approve + membership update + audit log
- review yaratish + rating cache yangilash
- reminder evaluation + notification event yaratish
- AI/OCR natijasini qabul qilish + odometer entry yozish

### 8.2 Transaction boundary service ichida bo‘ladi

Transaction:
- bot handler’da ochilmaydi
- API view’da ochilmaydi
- selector’da bo‘lmaydi

Transaction service qatlamida boshqariladi.

### 8.3 Tashqi servis chaqiruvi transaction ichida minimal bo‘lsin

Telegram API, AI provider, OCR provider, storage, geocoding kabi tashqi chaqiruvlar:
- timeout bo‘lishi mumkin
- rollback semantikasini buzishi mumkin
- transactionni uzoq ushlab turishi mumkin

Shu sababli:
- iloji bo‘lsa avval DB write
- keyin event/task yaratish
- keyin transactiondan tashqarida provider bilan ishlash

### 8.4 Transaction va side-effect ajratiladi

“Database truth” birinchi o‘rinda turadi. Tashqi side-effectlar unga bog‘langan holda keyin ishlanadi.

Agar kerak bo‘lsa:
- outboxga yaqin pattern
- pending task/event modeli
- status field bilan qayta ishlash

ishlatiladi.

---

## 9. Idempotency va duplicate protection

### 9.1 Telegram duplicate update bo‘lishi mumkin

Telegram polling/webhook muhitida bir update qayta kelishi mumkin.

Shu sababli:
- bir xil maintenance record ikki marta yaratilmasligi kerak
- bir xil odometer entry takror yozilmasligi kerak
- bir xil notification qayta yuborilmasligi kerak

### 9.2 Idempotency mexanizmlari

Quyidagi yondashuvlar qo‘llaniladi:
- unique constraint
- processed update registry
- source_event_id / external_id saqlash
- status state machine
- deterministic deduplication key
- optimistic yoki pessimistic lock (zarur joyda)

### 9.3 Worker task’lar qayta ishlanishi xavfsiz bo‘lishi kerak

Agar worker task’ni qayta olsa:
- natija buzilmasligi kerak
- duplicate effect bo‘lmasligi kerak
- task statusi aniq bo‘lishi kerak

### 9.4 Notification ikki marta yuborilmasligi kerak

Notification dispatch qatlamida kamida quyidagilar hisobga olinadi:
- `pending`
- `sent`
- `failed`
- `cancelled`

Statussiz “send and hope” yondashuvi taqiqlanadi.

---

## 10. Audit log qoidalari

### 10.1 Audit majburiy bo‘lgan actionlar

Kamida quyidagilar audit qilinadi:
- car create/update/archive
- membership create/update/revoke
- maintenance record create/update/delete
- line item o‘zgarishlari
- odometer entry yaratish yoki correction
- reminder rule o‘zgarishi
- workshop profile edit
- review moderation
- access approval/rejection
- AI/OCR natijasi qabul qilinishi yoki rad etilishi

### 10.2 Audit minimal tarkibi

Audit log kamida quyidagilarni saqlaydi:
- actor_user
- actor_transport_identity (kerak bo‘lsa telegram account)
- action
- target_type
- target_id
- before_snapshot
- after_snapshot
- correlation_id / request_id
- created_at

### 10.3 Audit bypass taqiqlanadi

Sensitive write action service’lari audit yozmasdan tugamasligi kerak.

### 10.4 Audit snapshot ma’noli bo‘lishi kerak

`before_snapshot` va `after_snapshot`:
- keraksiz juda katta payload bo‘lmasin
- o‘zgarishni tushunishga yetsin
- maxfiy ma’lumotni ortiqcha saqlamasin

---

## 11. Validation qoidalari

### 11.1 Validation ko‘p qatlamli bo‘lishi mumkin

Validation quyidagi darajalarda bo‘lishi mumkin:
- Django model constraint
- serializer/form schema validation
- service-level business validation
- database constraint

### 11.2 Business validation service’da bo‘ladi

Masalan:
- yangi odometr avvalgisidan kichik bo‘lmasligi
- viewer maintenance record qo‘sha olmasligi
- revoked membership action qilolmasligi
- workshop owner o‘z profiliga ikki marta bir xil location qo‘sha olmasligi
- review policy buzilmasligi
- invalid reminder threshold qabul qilinmasligi

Bu validationlar service qatlamida bo‘ladi.

### 11.3 Fail fast, lekin ma’noli xato bilan

Validation xatosi:
- aniq
- loggable
- user-facing qatlamga map qilish oson
- debuggingga yordam beradigan

bo‘lishi kerak.

---

## 12. Exception handling qoidalari

### 12.1 Domen exceptionlari aniq bo‘lsin

Custom exception’lar ishlatiladi, masalan:
- `EntityNotFoundError`
- `PermissionDeniedError`
- `BusinessRuleViolation`
- `DuplicateOperationError`
- `InvalidStateTransitionError`
- `ValidationError`

### 12.2 Infra exceptionlari alohida ko‘riladi

Quyidagilar infra xatolar:
- DB unavailable
- Telegram timeout
- AI provider timeout
- OCR provider xatosi
- file storage failure
- network issue

Ular domain xatolar bilan aralashmasligi kerak.

### 12.3 Generic exception bilan yopib yuborish taqiqlanadi

`except Exception: pass` yoki ma’nosiz wrapper’lar qabul qilinmaydi.

### 12.4 User-facing qatlam exception’ni tarjima qiladi

Bot, API yoki admin:
- domain exception’ni ushlaydi
- kerakli user message yoki response kodga aylantiradi
- lekin domain ma’lumotni yo‘qotmaydi

---

## 13. Logging qoidalari

### 13.1 Structured logging

Loglar production debugging uchun foydali bo‘lishi kerak.

Imkon qadar quyidagilar bo‘lsin:
- event_name
- entity_id
- user_id
- telegram_user_id
- correlation_id
- task_id
- status
- reason

### 13.2 Maxfiy ma’lumotlar log qilinmaydi

Quyidagilar log qilinmaydi:
- tokenlar
- secret key’lar
- parollar
- raw auth header’lar
- private file URL’lar
- AI provider credential’lari

### 13.3 Foydali log yoziladi, shovqin emas

Har bir helper ichida spam log kerak emas.

Muhim joylar:
- use-case start/end
- external integration failure
- worker lifecycle
- retry
- state transition
- permission denial
- invalid input rejection

### 13.4 Error log kontekstli bo‘lsin

Error log’da:
- nima bo‘lgani
- qaysi entity bilan bog‘liqligi
- qaysi user/contextda sodir bo‘lgani

ko‘rinsin.

---

## 14. Background worker qoidalari

### 14.1 Celery default emas

Ushbu loyiha default tarzda Celery ishlatmaydi. Background ishlar Django management command va DB-backed queue/event yondashuvi bilan quriladi.

### 14.2 Worker service/selectorga tayanadi

Worker:
- model bilan to‘g‘ridan-to‘g‘ri chalkash ishlamaydi
- service/selectorga tayanadi
- business rule’ni botdan ko‘chirib olmaydi

### 14.3 Worker task dizayni

Task yoki event:
- explicit state’ga ega
- restart-safe
- idempotent
- retryable
- observable

bo‘lishi kerak.

### 14.4 Tavsiya etiladigan worker commandlar

Masalan:
- `runworker`
- `process_reminders`
- `send_notifications`
- `cleanup_expired_states`
- `process_odometer_ocr`
- `process_recommendations`

### 14.5 Scheduler loop qoidalari

Agar worker loop periodik ishlasa:
- interval env/config orqali boshqariladi
- graceful shutdown bo‘ladi
- heartbeat yoki lifecycle log bo‘ladi
- parallel collision nazorat qilinadi
- uzoq tasklar worker’ni bloklab qo‘ymaydi

---

## 15. External integration va adapter pattern

### 15.1 Har bir provider adapter orqali ulanadi

Quyidagi integratsiyalar adapter yoki gateway orqali bo‘ladi:
- Telegram
- AI
- OCR
- storage
- geocoding/maps
- future push/email/SMS

### 15.2 Core logic providerga qattiq bog‘lanmaydi

Bugun:
- Telegram bot
- local OCR
- free AI model

bo‘lishi mumkin.

Ertaga:
- mobile app
- cloud OCR
- boshqa LLM provider

ga o‘tish mumkin.

Shu sababli core logic adapter abstraction orqali yoziladi.

### 15.3 Fallback mexanizmi bo‘lishi kerak

Ayniqsa AI va OCR uchun:
- provider ishlamasa
- timeout bo‘lsa
- confidence past bo‘lsa
- model mavjud bo‘lmasa

tizim fallback bilan ishlashi kerak.

Misollar:
- AI yo‘q -> rule-based recommendation
- OCR noaniq -> manual confirm
- notification send xatosi -> retry queue

---

## 16. Performance qoidalari

### 16.1 N+1 taqiqlanadi

History, cars list, review list, membership list, notifications kabi joylarda:
- `select_related`
- `prefetch_related`
- annotate/aggregate

to‘g‘ri ishlatilishi kerak.

### 16.2 Query ownership selector’da bo‘ladi

Murakkab query service yoki handler ichida emas, selector ichida bo‘lishi kerak.

### 16.3 Cached fieldlar source of truth emas

Quyidagilar cache bo‘lishi mumkin:
- `Car.current_odometer`
- `WorkshopProfile.average_rating_cached`
- `WorkshopProfile.total_reviews_cached`
- summary/stat counters

Lekin source of truth alohida canonical yozuvlarda bo‘ladi.

### 16.4 Premature optimization qilinmaydi

Avval toza arxitektura, keyin o‘lchangan joyga optimizatsiya.

Lekin obvious performance xatolar:
- N+1
- pointless loop query
- massive unpaginated list

qabul qilinmaydi.

---

## 17. Model bilan ishlash qoidalari

### 17.1 Fat model ham, fat handler ham emas

Loyiha:
- fat bot handler emas
- fat API view emas
- haddan tashqari fat model ham emas

Service-oriented Django yondashuvi bilan quriladi.

### 17.2 Model methodlar minimal bo‘lsin

Model methodlar:
- convenience helper
- tiny computed helpers
- normalize logic

uchun ishlatilishi mumkin.

Murakkab use-case modelga tiqilmaydi.

### 17.3 Domain relationlar aniq bo‘lsin

Har bir model relationi:
- kimga tegishli
- kim yaratgan
- kim ko‘ra oladi
- lifecycle’i qanday

aniq bo‘lishi kerak.

Noaniq “misc” yoki “generic everything” model yondashuvi qabul qilinmaydi.

---

## 18. Naming va kod uslubi qoidalari

### 18.1 Nomlar aniq bo‘lsin

Yomon:
- `data`
- `obj`
- `thing`
- `processor`
- `handle_all`

Yaxshi:
- `maintenance_record`
- `car_membership`
- `register_manual_odometer_entry`
- `can_user_edit_car`

### 18.2 Fayl nomlari vazifaga mos bo‘lsin

Masalan:
- `car_service.py`
- `maintenance_service.py`
- `car_selectors.py`
- `car_policies.py`
- `notification_service.py`
- `ocr_gateway.py`

### 18.3 Helper’lar “axlat qutisi”ga aylanmasin

`utils.py`, `helpers.py`, `common.py` kabi fayllar:
- aniq maqsadli
- kichik
- toifalangan

bo‘lishi kerak.

Har xil aloqasiz kodni bir joyga tiqish qabul qilinmaydi.

---

## 19. Testability qoidalari

### 19.1 Asosiy correctness service darajasida testlanadi

Eng muhim testlar:
- service testlar
- selector testlar
- policy testlar
- worker logic testlar

Bot handler testlari bo‘lishi mumkin, lekin core correctness botga bog‘liq bo‘lmasligi kerak.

### 19.2 Test yozishni qiyinlashtiradigan kod yozilmaydi

Quyidagilar testability’ni buzadi:
- yashirin global state
- inline provider call
- bir funksiyada ko‘p responsibility
- random side-effect
- vaqt/ID/network’ga qattiq bog‘langan kod

### 19.3 External dependency mock qilinadigan joyda adapter orqaligina mock qilinadi

Bevosita SDK chaqiruvini har joyda yozish taqiqlanadi. Aks holda testlash qiyinlashadi.

---

## 20. Future-ready qoidalari

### 20.1 Bot-bound arxitektura taqiqlanadi

Kod shunday yozilmasligi kerakki:
- use-case faqat Telegram message bilan ishlasin
- response faqat Telegram text bo‘lsin
- keyin API/mobile chiqsa qayta yozishga to‘g‘ri kelsin

### 20.2 ICE-only assumption taqiqlanadi

Mashina modeli kelajakda quyidagilarni ko‘tara olishi kerak:
- `ice`
- `hybrid`
- `ev`

Recommendation va maintenance logikasi shunga mos kengaytiriladigan bo‘lishi kerak.

### 20.3 Workshop marketplace alohida domen sifatida ko‘riladi

Workshop, service catalog, rating, location, review logikalari:
- faqat bot ichida yozilmaydi
- alohida service va selector qatlamiga ega bo‘ladi
- keyin web/mobile uchun reusable bo‘ladi

### 20.4 AI optional enhancement bo‘ladi

AI bo‘lmasa ham:
- servis yozish ishlashi kerak
- reminder ishlashi kerak
- recommendation minimal rule-based ishlashi kerak

AI:
- enhancement layer
- optional adapter
- fallback mavjud qatlam

bo‘lishi kerak.

---

## 21. AI agentlar uchun qat’iy ko‘rsatmalar

AI agentlar ushbu repository’da ishlaganda quyidagilarga rioya qilishi shart:

1. Handler ichiga business logic yozma.
2. Service ichiga Telegram-specific format yozma.
3. Selector ichida write qilma.
4. Policy o‘rniga random `if` tekshiruvlar yozma.
5. Multi-step write’ni transactiondan tashqarida qoldirma.
6. Audit talab qilinadigan action’da audit logni unutma.
7. Duplicate update ehtimolini inobatga ol.
8. Kodingni keyingi web/mobile reuse’ni o‘ylab yoz.
9. External provider’ga qattiq bog‘lanib qolma.
10. Model yoki migration qarorini “tezroq bo‘lsin” deb future extensibility’ni sindirib qo‘yma.
11. Katta service yozsang, use-case chegarasini aniq saqla.
12. Noaniq nomlar ishlatma.
13. Yangi endpoint yozsang ViewSet emas, explicit generic view yo‘lini tanla.
14. Hozir API kerak bo‘lmasa ham service layer’ni API-ready qil.
15. Har bir katta o‘zgarishni tegishli issue/task bilan bog‘la.

---

## 22. Anti-patternlar

Quyidagilar qat’iyan taqiqlanadi:

- Telegram handler ichida business logic yozish
- selector ichida `save()` qilish
- service ichida UI matn generatsiyasi
- policy o‘rniga transport qatlamida permission yozish
- audit log’siz sensitive write
- duplicate protection’siz Telegram update processing
- transaction’ni handler/view ichida boshqarish
- core logicni bitta provider SDK’siga qattiq bog‘lash
- AI bo‘lmasa ishlamaydigan arxitektura
- CRUD generator uslubida noaniq service’lar
- `ModelViewSet` bilan “tezroq” endpoint yozib yuborish
- `utils.py` ichiga aloqasiz hamma narsani tiqish
- “keyin tozalaymiz” deb arxitektura qarorini iflos boshlash

---

## 23. Definition of backend done

Backend task yoki modul done hisoblanadi, agar:

1. Qatlamlar to‘g‘ri ajratilgan bo‘lsa.
2. Service / selector / policy chegaralari saqlangan bo‘lsa.
3. Transaction boundary to‘g‘ri qo‘llangan bo‘lsa.
4. Validation va exception handling aniq bo‘lsa.
5. Logging foydali bo‘lsa.
6. Audit talab qilingan joylarda yozilgan bo‘lsa.
7. Duplicate/idempotency masalasi ko‘rib chiqilgan bo‘lsa.
8. Kod botdan mustaqil use-case sifatida ishlasa.
9. Kelajakda API/mobile/web bilan reuse qilish mumkin bo‘lsa.
10. Testlash mumkin bo‘lgan tarzda yozilgan bo‘lsa.
11. External integration adapter orqali bajarilgan bo‘lsa.
12. Future extensibility buzilmagan bo‘lsa.

---

## 24. Yakuniy prinsip

Bu backend “Telegram bot uchun kod” emas.

Bu:
- Telegram bot
- future web app
- future mobile app
- future AI assistant
- future workshop marketplace
- future analytics/reporting

uchun xizmat qiladigan **platforma backend**.

Har bir texnik qaror quyidagi savol bilan tekshiriladi:

**Bu qaror keyin yangi client, yangi modul yoki yangi provider qo‘shishni osonlashtiryaptimi yoki qiyinlashtiryaptimi?**

Agar qiyinlashtirayotgan bo‘lsa, qaror qayta ko‘rib chiqiladi.