# Django Rules

## 1. Maqsad

Ushbu hujjat Django asosidagi backend kod bazasini production-ready, tartibli va uzoq muddat kengaytiriladigan usulda yuritish uchun majburiy qoidalarni belgilaydi.

Bu loyiha:
- oddiy CRUD admin emas
- faqat Telegram bot backend’i emas
- keyinchalik web, mobile, AI, OCR, workshop marketplace va analytics qo‘shilishi mumkin bo‘lgan platforma

Shu sababli Django quyidagicha ishlatiladi:
- domain-oriented app struktura bilan
- settings split bilan
- custom user bilan
- service-oriented arxitektura bilan
- migration va admin’ni production asset sifatida ko‘rib
- media/static, security va extensibility’ni hisobga olib

Bu hujjat AI agentlar va developerlar uchun Django bo‘yicha asosiy standart hisoblanadi.

---

## 2. Loyiha strukturasi qoidalari

### 2.1 Root structure

Django loyihaning asosiy kodi `src/` papkasi ichida yashaydi.

Tavsiya etiladigan struktura:

- `src/manage.py`
- `src/config/` — settings, urls, wsgi, asgi
- `src/apps/` — domain app’lar
- `src/services/` — write/use-case orchestration
- `src/selectors/` — read/query logic
- `src/policies/` — authorization
- `src/bot/` — Telegram integration qatlamlari
- `src/common/` — shared utility, base abstraction, helperlar
- `src/integrations/` yoki `src/gateways/` — provider adapterlari
- `src/templates/` — kerak bo‘lsa server-side template
- `src/static/` — static assets
- `src/media/` — local development media storage
- `src/tests/` yoki app-level `tests/` — testlar

### 2.2 App’lar domain bo‘yicha ajratiladi

App’lar texnik qatlam bo‘yicha emas, domen bo‘yicha ajratiladi.

Yaxshi misollar:
- `users`
- `telegram`
- `cars`
- `maintenance`
- `expenses`
- `media_assets`
- `workshops`
- `notifications`
- `reminders`
- `odometer`
- `recommendations`
- `audit`

Yomon misollar:
- `utils_app`
- `misc`
- `handlers`
- `shared_stuff`
- `main_app`

### 2.3 Juda mayda app’ga bo‘lib yuborilmaydi

Har bir kichik model uchun alohida app ochish tavsiya etilmaydi.

App:
- aniq domain ma’noga ega
- ichki cohesion’i yaxshi
- ortiqcha fragmentatsiyasiz
- maintain qilish oson

bo‘lishi kerak.

### 2.4 Har bir app ichida ham tartib bo‘lsin

App ichida kamida quyidagi fayllar bo‘lishi mumkin:

- `apps.py`
- `models.py`
- `admin.py`
- `validators.py`
- `constants.py`
- `choices.py`
- `signals.py` (faqat juda zarur bo‘lsa)
- `tests/`

Katta app bo‘lsa quyidagicha bo‘linishi mumkin:
- `models/`
- `admin/`
- `api/`
- `queries/`

Lekin bunday bo‘lishi faqat hajm oshganda oqlanadi.

---

## 3. Settings qoidalari

### 3.1 Settings split majburiy

Settings bitta faylda bo‘lmaydi.

Minimal split:
- `base.py`
- `local.py`
- `production.py`

Agar kerak bo‘lsa:
- `test.py`

### 3.2 Base settings umumiy va xavfsiz bo‘lsin

`base.py`:
- umumiy config
- INSTALLED_APPS
- middleware
- templates
- auth model
- rest framework defaultlar (agar ishlatilsa)
- timezone/lang
- logging skeleton
- static/media path
- env o‘qish helperlari

uchun ishlatiladi.

`base.py` ichida production-only yoki local-only hack’lar bo‘lmasligi kerak.

### 3.3 Secret’lar code ichida bo‘lmaydi

Quyidagilar faqat env orqali olinadi:
- `SECRET_KEY`
- DB credentials
- Telegram bot token
- ALLOWED_HOSTS
- CSRF trusted origins
- AI/OCR provider keylari
- storage credential’lari
- email credential’lari
- third-party API keylar

`.env.example` version control’da bo‘ladi. Real `.env` kiritilmaydi.

### 3.4 Production settings qat’iy bo‘lsin

Production’da:
- `DEBUG = False`
- secure cookie’lar
- HTTPS bilan bog‘liq setting’lar yoqilgan
- `ALLOWED_HOSTS` aniq
- `CSRF_TRUSTED_ORIGINS` aniq
- logging ishlaydigan
- static/media serving strategiyasi aniq
- file upload va request size bilan bog‘liq limitlar ko‘rib chiqilgan

### 3.5 Settings’da biznes logika bo‘lmaydi

Settings fayllarida:
- murakkab funksiya
- business rule
- dynamic hack
- app import side-effect

bo‘lmasligi kerak.

---

## 4. Custom User qoidalari

### 4.1 Boshidan custom user ishlatiladi

Django’ning default `auth.User` modeli ishlatilmaydi.

Loyiha boshidan custom user model bilan boshlanadi.

Sabab:
- keyinchalik field qo‘shish oson
- auth strategiyasi moslashuvchan bo‘ladi
- Telegram-first bo‘lsa ham future auth variantlar qo‘shilishi mumkin

### 4.2 User modeli minimal bo‘lsin

`User` model:
- identity
- account holati
- umumiy profilinga oid eng minimal fieldlar

uchun ishlatiladi.

Telegram’ga xos fieldlar:
- `telegram_user_id`
- `chat_id`
- `username`
- `language_code`

alohida `TelegramAccount` modelida saqlanadi.

### 4.3 Telegram account user’dan ajratiladi

`TelegramAccount` alohida model bo‘lishi shart.

Bu:
- bir userga kelajakda bir nechta transport identity ulash
- transport qatlamini domen user’dan ajratish
- Telegram-specific fieldlarni toza saqlash

uchun kerak.

### 4.4 User model keyinchalik haddan tashqari semirtirilmaydi

User model ichiga:
- random statistics
- bot state
- notification queue fieldlari
- AI log
- car ownership summary

kabi fieldlarni qo‘shib yuborish taqiqlanadi.

---

## 5. Model qoidalari

### 5.1 Har bir model business ma’noga ega bo‘lsin

Model:
- aniq domain entity bo‘lishi kerak
- relationlari tushunarli bo‘lishi kerak
- lifecycle’i aniq bo‘lishi kerak

“Balki keyin kerak bo‘lar” deb model qo‘shish qabul qilinmaydi.

### 5.2 Primary key strategiyasi

Tashqi yoki muhim business entity’lar uchun UUID afzal:
- `Car`
- `MaintenanceRecord`
- `MediaAsset`
- `NotificationEvent`
- `WorkshopProfile`
- `OdometerEntry`

Oddiy lookup yoki kichik reference jadvallar uchun integer ishlatilishi mumkin.

### 5.3 Timestamp field’lar

Muhim modellarda kamida:
- `created_at`
- `updated_at`

bo‘lishi kerak.

Event yoki append-only modellarda:
- `created_at`

yetarli bo‘lishi mumkin.

### 5.4 Source / status fieldlar explicit bo‘lsin

Tizimda transport va lifecycle muhim bo‘lgan entity’larda explicit fieldlar ishlatiladi:

Misollar:
- `source = telegram/admin/system/ocr/ai`
- `status = draft/final/pending/failed/sent/revoked`

Noaniq boolean’lar bilan status ifodalash tavsiya etilmaydi.

### 5.5 Soft delete har yerda ishlatilmaydi

Soft delete default emas.

Faqat kerakli entity’larda ko‘rib chiqiladi:
- `Car`
- `MaintenanceRecord`
- `WorkshopProfile`

Soft delete qo‘llansa:
- selector’lar buni hisobga oladi
- admin’da ko‘rinishi boshqariladi
- unique constraint strategy ko‘rib chiqiladi
- “o‘chdi” va “arxivlandi” ma’nosi chalkashmasligi kerak

### 5.6 Model methodlar minimal bo‘lsin

Model method’lar:
- `__str__`
- tiny normalize helper
- computed property
- small convenience checker

uchun ishlatilishi mumkin.

Murakkab use-case modelga joylanmaydi.

### 5.7 GenericForeignKey faqat zarur bo‘lsa ishlatiladi

Agar media yoki audit kabi cross-entity bog‘lanish kerak bo‘lsa, `GenericForeignKey` ishlatish mumkin.

Lekin:
- default tanlov bo‘lmaydi
- explicit FK bilan hal qilish imkoni bo‘lsa, o‘sha afzal
- GFK ishlatilsa selector va index strategiyasi oldindan o‘ylanadi

### 5.8 Constraint va index’lar ongli yoziladi

Har bir model uchun quyidagilar ko‘rib chiqiladi:
- unique constraint
- partial uniqueness
- foreign key index
- date/status bo‘yicha index
- composite index

Misollar:
- `telegram_user_id`
- `normalized_plate_number`
- `vin`
- `car + user` membership unique
- `status + scheduled_for` notification querylari
- `car + entry_date` odometer querylari

### 5.9 Null va blank farqi to‘g‘ri ishlatiladi

String fieldlarda:
- keraksiz `null=True` ishlatilmaydi
- odatda `blank=True` yetarli

Nullable bo‘lishi haqiqiy semantik ma’noga ega bo‘lishi kerak.

### 5.10 Choices va enum’lar markazlashgan bo‘lsin

Status, role, type kabi maydonlar uchun:
- Django `TextChoices`
- yoki markazlashgan `choices.py`

ishlatiladi.

Literal string’larni kod bo‘ylab sochib yuborish taqiqlanadi.

---

## 6. Migration qoidalari

### 6.1 Migration’lar tekshiriladi, ko‘r-ko‘rona commit qilinmaydi

`makemigrations` chiqargan migration avtomatik ravishda to‘g‘ri deb qabul qilinmaydi.

Har bir migration:
- o‘qiladi
- dependency tekshiriladi
- noto‘g‘ri rename/drop/add yo‘qligi ko‘riladi
- keraksiz noise yo‘qligi tekshiriladi

### 6.2 Har bir schema o‘zgarish migration bilan birga ketadi

Model o‘zgargan bo‘lsa, migration ham shu task ichida bo‘lishi kerak.

“Keyin migration qilamiz” yondashuvi qabul qilinmaydi.

### 6.3 Existing migration rewrite ehtiyotkorlik bilan

Agar migration:
- main branch’da
- shared branch’da
- productionga yaqin muhitda

bo‘lsa, eski migration’ni rewrite qilish tavsiya etilmaydi.

Yangi migration yoziladi.

### 6.4 Data migration alohida mas’uliyat bilan yoziladi

Data migration kerak bo‘lsa:
- aniq maqsad bilan
- rollback impact o‘ylab
- katta jadval uchun batch strategiyasi ko‘rib
- downtime xavfi baholanib

yoziladi.

### 6.5 Dangerous migration’lar oldindan baholanadi

Katta jadvaldagi:
- NOT NULL qo‘shish
- default bilan column qo‘shish
- massive index
- field type o‘zgartirish
- unique constraint

kabi o‘zgarishlar alohida ko‘rib chiqiladi.

---

## 7. Django admin qoidalari

### 7.1 Admin production tool sifatida qaraladi

Admin faqat debug panel emas.

Admin:
- internal operator tool
- support correction panel
- audit inspection joyi
- workshop/provider moderation panel
- data triage panel

sifatida foydali bo‘lishi kerak.

### 7.2 Har bir muhim model uchun admin dizayni o‘ylanadi

Muhim model admin’ida ko‘rib chiqiladi:
- `list_display`
- `search_fields`
- `list_filter`
- `readonly_fields`
- `autocomplete_fields`
- `raw_id_fields`
- `ordering`
- `date_hierarchy`

### 7.3 Admin destructive bo‘lmasin

Admin’da:
- keraksiz bulk delete yo‘q
- audit bypass qiladigan action yo‘q
- sensitive fieldlarni tasodifiy edit qilish oson bo‘lmasin
- critical workflow iloji bo‘lsa service orqali bajarilsin

### 7.4 Admin performance’ga zarar bermasin

Katta relation’li admin’larda:
- `list_select_related`
- `autocomplete_fields`
- queryset optimization
- pagination

ishlatiladi.

Admin N+1 generator bo‘lmasligi kerak.

### 7.5 Admin permissionlari ko‘rib chiqiladi

Hamma staff ham hamma modelni edit qila olmaydi.

Kerak bo‘lsa:
- readonly admin
- add-only
- moderate-only
- superuser-only

kabi yondashuv qo‘llanadi.

### 7.6 Admin action service chaqirishi mumkin

Agar admin’dan critical action bajarilsa:
- bevosita model update emas
- tegishli service chaqirish

afzal.

Masalan:
- access approve
- notification requeue
- reminder regenerate
- workshop verify

---

## 8. Django REST Framework qoidalari

### 8.1 API hozir majburiy emas

Joriy bosqichda to‘liq HTTP API majburiy emas.

Sabab:
- asosiy client — Telegram bot
- bot management command orqali ishlaydi
- use-case’lar service layer orqali bajariladi
- ichki orchestration uchun API shart emas

### 8.2 Lekin API-ready arxitektura bo‘lishi shart

Kelajakda:
- mobile app
- web app
- internal dashboard
- external integration

uchun API kerak bo‘lishi mumkin.

Shu sababli:
- business logic service’larda
- query logic selector’larda
- permission policy’larda
- API faqat adapter qatlamida

bo‘lishi kerak.

### 8.3 ViewSet default tarzda ishlatilmaydi

Ushbu loyihada default qoida:
- `ModelViewSet` ishlatilmaydi
- `ViewSet` ishlatilmaydi

Sabab:
- endpoint behavior juda implicit bo‘lib ketadi
- permission va serializer boshqaruvi tarqaladi
- use-case centered design susayadi
- AI agentlar “tezroq CRUD” yo‘liga ketadi

### 8.4 GenericAPIView oilasi afzal

API yozilsa quyidagilar afzal:
- `CreateAPIView`
- `RetrieveAPIView`
- `ListAPIView`
- `UpdateAPIView`
- `DestroyAPIView`

Yoki:
- `GenericAPIView`
- explicit `get/post/patch/delete`

Bu yondashuv:
- endpointlarni explicit qiladi
- permission boshqaruvini soddalashtiradi
- serializer tanlashni nazoratda ushlaydi
- service semantikasiga yaqin turadi

### 8.5 Serializer vazifasi cheklangan

Serializer:
- input parsing
- schema validation
- representation

uchun ishlatiladi.

Serializer ichida:
- transaction orchestration
- ko‘p model write
- notification yaratish
- murakkab business rule

bo‘lmasligi kerak.

### 8.6 API view vazifasi

View:
- request qabul qiladi
- serializer validate qiladi
- service chaqiradi
- response qaytaradi

View ichida:
- murakkab domain logic
- selector o‘rniga query yig‘ish
- qo‘lda permission logic
- raw transport text yasash

bo‘lmasligi kerak.

### 8.7 API endpoint use-case oriented bo‘ladi

Endpointlar CRUD generator uslubida emas, use-case markazida yoziladi.

Misollar:
- `POST /cars/`
- `POST /cars/{id}/access-requests/`
- `POST /maintenance-records/`
- `POST /odometer-entries/`
- `POST /workshops/{id}/reviews/`

Lekin endpoint semantics service’ga mos bo‘lishi kerak.

### 8.8 Pagination, filtering, ordering nazoratli bo‘lsin

API yozilsa:
- cheksiz list endpoint bo‘lmaydi
- pagination default bo‘ladi
- filtering explicit bo‘ladi
- noaniq massiv query param sprawl’dan qochiladi

---

## 9. Forms, admin validation va service integratsiyasi

### 9.1 Schema validation va business validation ajratiladi

- form/serializer — shape va basic validation
- service — business validation

Misol:
- “bu sana format jihatdan to‘g‘rimi?” — serializer/form
- “bu odometr oldingisidan kichik emasmi?” — service

### 9.2 Admin service’ni bypass qilmasin

Agar admin orqali critical yozuv yaratish/o‘zgartirish bo‘lsa, imkon qadar service chaqiriladi.

Bevosita `save_model` ichida murakkab business logic yozish tavsiya etilmaydi.

### 9.3 Model clean() hamma narsani hal qilmaydi

`clean()` ishlatilishi mumkin, lekin:
- core orchestration joyi emas
- service-level qoidalar o‘rnini bosmaydi

---

## 10. File, media va storage qoidalari

### 10.1 Media DB’da saqlanmaydi

Media faylning o‘zi filesystem yoki storage backend’da saqlanadi.
DB’da:
- metadata
- file path
- telegram file id
- checksum
- mime/type

saqlanadi.

### 10.2 Upload path deterministic bo‘lsin

Path strategiyasi tartibli bo‘lishi kerak.

Masalan:
- entity type
- entity id
- year/month
- uuid filename

Original filename storage strukturasi uchun ishonchli asos emas.

### 10.3 Filename sanitization majburiy

Foydalanuvchi yuborgan filename:
- tozalanadi
- xavfli belgilar olib tashlanadi
- path traversal imkoni bo‘lmaydi

### 10.4 File validation majburiy

Upload paytida tekshiriladi:
- extension
- mime type
- size
- kerak bo‘lsa image verification
- allowed file class

### 10.5 Local storage’dan S3/MinIO’ga o‘tish imkoniyati saqlanadi

Storage’ga qattiq bog‘lanmagan arxitektura bo‘ladi.

Media modeli va storage provider ajratilgan bo‘lishi kerak.

### 10.6 Media URL security o‘ylanadi

Har bir media public bo‘lishi shart emas.

Kelajakda:
- private media
- signed URL
- permission-protected serving

kerak bo‘lishi mumkin.

Hozirgi qarorlar keyin buni qiyinlashtirmasligi kerak.

---

## 11. Static files qoidalari

### 11.1 Static va media chalkashmaydi

- static — kod bilan keladigan assetlar
- media — user yuklagan fayllar

Bu ikkalasi alohida saqlanadi.

### 11.2 Production static strategy aniq bo‘lsin

Static:
- collectstatic orqali yig‘iladi
- Nginx yoki mos serving strategy bilan tarqatiladi

Static filelar application runtime ichida noaniq joyda qolib ketmasligi kerak.

---

## 12. Signals qoidalari

### 12.1 Signals default instrument emas

Django signal’lar default yondashuv sifatida ishlatilmaydi.

Sabab:
- side-effect yashirin bo‘lib ketadi
- debugging qiyinlashadi
- AI agentlar noma’lum coupling hosil qiladi

### 12.2 Signal faqat juda zarur bo‘lsa ishlatiladi

Masalan:
- kichik, izolyatsiyalangan, past riskli side-effect
- framework integration ehtiyoji

Ammo core business workflow signal’da bo‘lmaydi.

### 12.3 Critical action signal ichida yashirilmaydi

Maintenance record yaratish, access approve qilish, notification scheduling, audit log strategiyasi kabi muhim actionlar signal ichida yashirilmaydi.

---

## 13. Managers va QuerySet qoidalari

### 13.1 Custom manager minimal bo‘lsin

Custom manager:
- tiny reusable queryset helper
- active/not_deleted helper
- typed queryset convenience

uchun ishlatilishi mumkin.

Lekin:
- murakkab report query
- permission query
- orchestration

manager ichiga yozilmaydi.

### 13.2 QuerySet helper’lar selector o‘rnini bosmaydi

Katta read logic selector’da bo‘ladi.

Manager/QuerySet helper’lar faqat qurilish bloklari bo‘lishi mumkin.

---

## 14. Caching qoidalari

### 14.1 Cache source of truth emas

Cache:
- performance uchun
- derived summary uchun
- tez-tez o‘qiladigan aggregation uchun

ishlatilishi mumkin.

Lekin asosiy truth canonical model/jadvalda bo‘ladi.

### 14.2 Cache invalidation strategy o‘ylanadi

Cached field yoki external cache ishlatilsa:
- qachon yangilanadi
- qachon qayta hisoblanadi
- stale holat qanchalik xavfli

aniq bo‘lishi kerak.

### 14.3 Erta cache qo‘shilmaydi

Premature cache qatlamlari qo‘shilmaydi. Avval profiling va aniq ehtiyoj.

---

## 15. Timezone, sana va locale qoidalari

### 15.1 Timezone-aware datetime

Datetime field’lar timezone-aware bo‘ladi.

Naive datetime bilan yashirin xatolar qilinmaydi.

### 15.2 Sana va datetime chalkashmasin

- servis kuni — `DateField` bo‘lishi mumkin
- event yaratish va audit vaqti — `DateTimeField`

Semantika aniq bo‘lishi kerak.

### 15.3 Locale-dependent parsing transport qatlamida hal qilinadi

Telegram yoki API user input formatlari:
- transport qatlami
- serializer/form

darajasida parse qilinadi.

Model/service ichida raw locale-dependent string parse qilish tavsiya etilmaydi.

---

## 16. Security bo‘yicha Django-specific qoidalar

### 16.1 Admin ochiq qoldirilmaydi

Admin:
- kuchli credential
- kerakli host/proxy setting
- kerak bo‘lsa IP cheklov
- HTTPS

bilan himoyalangan bo‘lishi kerak.

### 16.2 File upload xavfsizligi

Upload:
- file type validation
- filename sanitization
- executable fayllarga ehtiyotkor munosabat
- media serving strategy

bilan himoyalanadi.

### 16.3 CSRF, session va auth settinglar productionda to‘g‘ri bo‘lsin

Agar future web UI bo‘lsa, hozirdan Django security defaults’ni buzadigan qarorlar qabul qilinmaydi.

### 16.4 Internal admin/debug endpointlar nazoratsiz ochilmaydi

Temporary debug view, open health detail, raw task inspector kabi endpointlar ehtiyotkorlik bilan boshqariladi.

---

## 17. Testing bo‘yicha Django-specific qoidalar

### 17.1 App-level testlar aniq joylashadi

Har bir app o‘z testlariga ega bo‘lishi mumkin:
- `tests/test_models.py`
- `tests/test_admin.py`
- `tests/test_api.py`

Lekin asosiy business flow testlari service qatlamida markazlashgan bo‘lishi mumkin.

### 17.2 Factory/fixture yondashuvi tartibli bo‘lsin

Test datasi:
- o‘qilishi oson
- qayta ishlatiladigan
- side-effect kam
- noaniq massive fixture’lardan qochilgan

bo‘lishi kerak.

### 17.3 Migration va model regressiyalar test bilan ushlansin

Muhim constraint, uniqueness, status flow, relation semantics test qilinadi.

---

## 18. AI agentlar uchun Django bo‘yicha qat’iy ko‘rsatmalar

AI agentlar quyidagilarga rioya qilishi shart:

1. Default `auth.User` ishlatma, custom user’dan foydalan.
2. Telegram field’larni User modelga tiqma, `TelegramAccount` alohida bo‘lsin.
3. Yangi model qo‘shsang, uning business ma’nosini aniq saqla.
4. Migration’ni ko‘r-ko‘rona generatsiya qilib qoldirma, tekshir.
5. `ModelViewSet` ishlatma.
6. API kerak bo‘lsa explicit `GenericAPIView` oilasidan foydalan.
7. Serializer ichiga business logic yozma.
8. Signal ichiga core business workflow yashirma.
9. `utils.py` ichiga har xil aloqasiz kodni tiqma.
10. Admin’ni production tool deb qarab, list/search/filter/read-only fieldlarni o‘ylab yoz.
11. Upload path’ni tartibli qil.
12. String field’larda keraksiz `null=True` yozma.
13. Status/type maydonlari uchun choices yoki enum ishlat.
14. Soft delete’ni hamma joyga sochib yuborma.
15. Future web/mobile/API reuse’ni buzadigan Django shortcut’lardan qoch.

---

## 19. Anti-patternlar

Quyidagilar qat’iyan taqiqlanadi:

- Default `auth.User` bilan boshlash
- Telegram-specific fieldlarni User ichiga qo‘shib yuborish
- `ModelViewSet` bilan tezkor CRUD generatsiya
- serializer ichida murakkab business logic
- signal’da core workflow yashirish
- migration’ni tekshirmasdan commit qilish
- `null=True` ni keraksiz string fieldlarga yozish
- noaniq `misc`, `utils_app`, `core_stuff` app’lar yaratish
- admin’ni umuman o‘ylamasdan tashlab qo‘yish
- upload fayllarni tartibsiz saqlash
- service layer o‘rniga model/save override bilan barcha logikani yozish
- GFK’ni har yerda universal yechim deb ishlatish
- static/media’ni bir joyga aralashtirib yuborish

---

## 20. Definition of Django done

Django bilan bog‘liq task done hisoblanadi, agar:

1. App domain jihatdan to‘g‘ri joylashgan bo‘lsa.
2. Model business ma’noga ega bo‘lsa.
3. Migration yaratilgan va tekshirilgan bo‘lsa.
4. Admin integration o‘ylangan bo‘lsa.
5. Settings va env qarorlari production-safe bo‘lsa.
6. API yozilgan bo‘lsa, explicit generic view’lar ishlatilgan bo‘lsa.
7. Serializer/form/service chegaralari buzilmagan bo‘lsa.
8. Media/static qarorlari tartibli bo‘lsa.
9. Security va extensibility buzilmagan bo‘lsa.
10. Keyinchalik web/mobile/API evolyutsiyasi uchun arxitektura ochiq bo‘lsa.

---

## 21. Yakuniy prinsip

Django bu loyihada shunchaki framework emas. U platformaning asosiy skeleti.

Shuning uchun har bir Django qarori quyidagi savol bilan tekshiriladi:

**Bu qaror kod bazani keyin tozalashni qiyinlashtiryaptimi yoki hozirdanoq toza va kengaytiriladigan qilayaptimi?**

Agar qaror:
- coupling’ni oshirsa
- domain chegarasini xiralashtirsa
- future clientlar uchun reuse’ni qiyinlashtirsa
- AI agentni “shortcut”ga majburlasa

u holda bu qaror qayta ko‘rib chiqiladi.
