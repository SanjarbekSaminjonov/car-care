# Testing Rules

## 1. Maqsad

Ushbu hujjat loyiha uchun test yozish standartlarini, test strategiyasini va quality gate qoidalarini belgilaydi.

Bu loyiha:
- Telegram-first platforma
- multi-user, multi-car domain
- structured maintenance va expense tracking
- background worker’lar
- media upload
- reminder/recommendation foundation
- kelajakda OCR, AI, workshop marketplace va web/mobile clientlar

bilan kengayadigan tizim bo‘lgani uchun testlar shunchaki “ishlayapti shekilli” darajasida emas, **production-grade ishonchlilik** darajasida bo‘lishi kerak.

Testing maqsadi:
- regressiyalarni oldini olish
- business rule’larni himoya qilish
- AI agentlar yozgan kodni nazorat qilish
- refactor qilishni xavfsizlashtirish
- edge-case’larni oldindan ushlash
- idempotency, permission va stateful flow xatolarini erta aniqlash

---

## 2. Asosiy prinsiplar

1. **Test yozish majburiy.**
2. **Core business logic har doim testlanadi.**
3. **Testlar deterministic bo‘ladi.**
4. **Happy path yetarli emas.**
5. **Permission va validation testlari majburiy.**
6. **Idempotency va state transition alohida tekshiriladi.**
7. **Test tez, o‘qilishi oson va ishonchli bo‘lishi kerak.**
8. **Core correctness bot/UI qatlamiga bog‘lanmaydi.**
9. **Regression topilgan joyga test qo‘shilmasdan fix yakunlangan hisoblanmaydi.**
10. **AI agent yozgan har muhim kod test bilan mustahkamlanadi.**

---

## 3. Test strategiyasi

Loyiha quyidagi test qatlamlari asosida tekshiriladi:

### 3.1 Unit testlar
Kichik, izolyatsiyalangan logikani tekshiradi.

Misollar:
- parser
- formatter
- helper
- enum/status transition validator
- kichik policy helper
- dedup key generator

### 3.2 Service testlar
Asosiy business correctness shu yerda tekshiriladi.

Misollar:
- `create_car`
- `request_car_access`
- `approve_car_access_request`
- `create_maintenance_record`
- `register_manual_odometer_entry`
- `create_workshop_review`
- `schedule_due_notifications`

### 3.3 Selector testlar
Read/query correctness va performance-sensitive query expectationlarni tekshiradi.

Misollar:
- filtering
- ordering
- pagination semantics
- aggregation
- visibility scope

### 3.4 Policy testlar
Authorization va object-level access qoidalarini tekshiradi.

### 3.5 Bot flow testlar
Telegram interaction mapping va state machine to‘g‘riligini tekshiradi.

### 3.6 Worker testlar
Background task, retry, idempotency, scheduling va state progression’ni tekshiradi.

### 3.7 Integration testlar
Bir nechta qatlam birga ishlaganda correctness tekshiriladi.

Misollar:
- service + DB transaction
- bot handler + service boundary
- worker + notification event lifecycle
- media metadata + storage integration

### 3.8 Smoke testlar
Muhim asosiy flow’lar minimal holda ishlashini tasdiqlaydi.

---

## 4. Nima majburiy test qilinadi

Quyidagilar majburiy test qilinadi:

- service layer
- selector layer
- policy layer
- worker logic
- stateful bot flow’lar
- parsing va normalization
- status transition
- duplicate protection
- permission denial
- validation error
- transaction-sensitive write flow
- audit yozilishi talab qilingan actionlar
- notification scheduling logic
- reminder evaluation logic
- media validation logic

Quyidagilar kamida smoke/integration darajasida ko‘rib chiqiladi:
- admin critical action
- API layer (yozilgan bo‘lsa)
- provider adapter boundary

---

## 5. Test piramidasi va ustuvorlik

Ustuvorlik:

1. **Service testlar** — eng muhim
2. **Policy testlar** — xavfsizlik uchun juda muhim
3. **Selector testlar** — correctness + query behavior
4. **Worker testlar** — idempotency va retry xavfi uchun muhim
5. **Bot flow testlar** — UX/state correctness
6. **Integration testlar** — muhim wiring tekshiruvi
7. **Pure UI-format testlar** — faqat kerak bo‘lsa

Testlar faqat bot matniga bog‘lanib qolmasligi kerak. Core correctness bot response’dan emas, business natijadan tekshiriladi.

---

## 6. Service test qoidalari

### 6.1 Har bir muhim service uchun test bo‘ladi

Har bir muhim write/use-case service kamida quyidagilar bilan testlanadi:
- success case
- validation failure
- permission failure
- state violation
- edge case
- audit yoki side-effect expectation
- idempotency kerak bo‘lsa duplicate case

### 6.2 Service test strukturasi

Service testlar ideal holda quyidagi pattern bilan yoziladi:
- Arrange
- Act
- Assert

Misol:
- kerakli user/car/membership yaratish
- service chaqirish
- DB natijasi, audit, status va qaytgan qiymatni tekshirish

### 6.3 Service testlar faqat “yaratildi” darajasida bo‘lmasligi kerak

Tekshirilsin:
- qaysi entitylar yaratildi
- qaysi fieldlar to‘g‘ri yozildi
- cache field yangilandimi
- audit log yozildimi
- line item count to‘g‘rimi
- invalid holatda partial write bo‘lmadimi

### 6.4 Multi-step write’da atomicity tekshiriladi

Masalan:
- maintenance record yaratishda
- line item va odometer va audit birga yozilganda

xato yuz bersa partial state qolmasligi test qilinadi.

### 6.5 Business rule testlari majburiy

Misollar:
- odometer avvalgisidan kichik bo‘lmasligi
- viewer record qo‘sha olmasligi
- revoked membership action qila olmasligi
- duplicate review qoidasi
- invalid reminder threshold

---

## 7. Selector test qoidalari

### 7.1 Selector correctness test qilinadi

Tekshirilsin:
- faqat tegishli user yozuvlarini qaytarishi
- soft-delete yoki inactive holatlarni hisobga olishi
- ordering to‘g‘rimi
- filter kombinatsiyasi to‘g‘rimi
- bo‘sh natija holati to‘g‘rimi

### 7.2 Selector performance semantics tekshiriladi

Har selector uchun SQL count test yozish shart emas, lekin performance-sensitive selectorlar uchun:
- N+1 yo‘qligi
- `select_related`/`prefetch_related` ishlashi
- pagination semantics

kamida review qilinadi, kerak bo‘lsa test bilan mustahkamlanadi.

### 7.3 Selector write qilmasligi test va code review orqali nazorat qilinadi

Selector side-effect bermasligi kerak.

---

## 8. Policy test qoidalari

### 8.1 Policy’lar alohida testlanadi

Har object-level permission uchun kamida:
- allow scenario
- deny scenario

bo‘lishi kerak.

### 8.2 Role matrix test qilinadi

Masalan:
- owner
- manager
- viewer
- unrelated user

bir xil object uchun alohida test qilinadi.

### 8.3 Policy testlar user-storyga yaqin bo‘lsin

Masalan:
- owner share qila oladi
- manager owner’ni remove qila olmaydi
- viewer maintenance qo‘sha olmaydi

---

## 9. Bot test qoidalari

### 9.1 Bot testlari core business logic o‘rnini bosmaydi

Bot testlari quyidagilar uchun:
- routing
- state transition
- invalid input recovery
- cancel behavior
- callback parsing
- formatter integration
- transport error handling

### 9.2 Har kritik flow test qilinadi

Kamida:
- start / onboarding
- add car
- add maintenance
- add odometer
- cancel flow
- invalid input flow
- share flow
- confirmation flow

### 9.3 Flow testlari step-by-step yoziladi

Tekshirilsin:
- qaysi state’ga o‘tdi
- qanday xabar qaytdi
- noto‘g‘ri inputda state saqlanib qoldimi
- cancel state’ni tozaladimi

### 9.4 Bot testlari overly brittle bo‘lmasin

Har vergul, har emoji uchun snapshot test yozib bot testlarini sinuvchan qilish tavsiya etilmaydi.

Asosiy fokus:
- semantics
- state
- action outcome

---

## 10. Worker test qoidalari

### 10.1 Worker logic alohida testlanadi

Quyidagilar test qilinadi:
- pending task olinishi
- task processed bo‘lishi
- status o‘zgarishi
- retryable xato
- non-retryable xato
- duplicate process bo‘lmasligi

### 10.2 Reminder/notification flow test qilinadi

Masalan:
- due bo‘lgan rule notification event yaratadi
- yaratgan event qayta takrorlanmaydi
- sent status to‘g‘ri qo‘yiladi
- failed bo‘lsa retry queue logikasi ishlaydi

### 10.3 Restart-safe semantics ko‘rib chiqiladi

Worker qayta ishlasa:
- duplicate send bo‘ladimi
- task state noto‘g‘ri qoladimi
- half-processed holat qanday yakunlanadi

test qilinadi.

---

## 11. Idempotency test qoidalari

### 11.1 Idempotency alohida testlanadi

Bu loyiha uchun bu juda muhim.

Quyidagilar test qilinadi:
- duplicate Telegram update
- duplicate notification send trigger
- bir xil external/source id bilan write
- worker task qayta ishlanishi

### 11.2 “Ikki marta chaqirib ko‘rish” testi majburiy bo‘lishi mumkin

Idempotent bo‘lishi kerak bo‘lgan service/task uchun:
- birinchi chaqiriq
- ikkinchi shu chaqiriq

natijasi tekshiriladi.

### 11.3 Duplicate protection regressiyalari alohida muhim

Bir marta topilgan duplicate bug uchun regression test yozilishi majburiy.

---

## 12. Audit test qoidalari

### 12.1 Audit talab qilingan actionlar test qilinadi

Tekshirilsin:
- audit yozildimi
- actor to‘g‘rimi
- target type/id to‘g‘rimi
- before/after ma’nolimi
- action kodi to‘g‘rimi

### 12.2 Audit yo‘q qolishi bug hisoblanadi

Audit talab qilingan critical action test bilan himoyalanadi.

---

## 13. Validation va error handling test qoidalari

### 13.1 Failure case majburiy

Har muhim flow/service uchun kamida bitta failure case bo‘ladi.

### 13.2 User xatosi va system xatosi aralashmasin

Testlar quyidagini ajratib tekshiradi:
- invalid input
- permission yo‘qligi
- business rule violation
- provider xatosi
- infra xatosi

### 13.3 Error case’da partial write qolmasligi tekshiriladi

Bu ayniqsa transactionli flow’larda majburiy.

---

## 14. Parsing va normalization test qoidalari

### 14.1 Parser’lar alohida testlanadi

Masalan:
- mileage parsing
- amount parsing
- date parsing
- plate normalization
- callback data parsing

### 14.2 Noto‘g‘ri inputlar test qilinadi

Masalan:
- bo‘sh string
- noto‘g‘ri format
- noaniq qiymat
- juda katta son
- manfiy son
- kutilmagan belgilar

### 14.3 OCR/AI parsing future-ready test strategiyasi

Kelajakda provider natijasi parse qilinsa:
- valid result
- low confidence
- empty result
- malformed result

holatlari testlanadi.

---

## 15. Media va file test qoidalari

### 15.1 Media validation test qilinadi

Tekshirilsin:
- allowed type
- disallowed type
- max size
- metadata saqlanishi
- entityga bog‘lanishi

### 15.2 Media storage to‘liq real providerga bog‘lanib test qilinmaydi

Storage adapter mock/fake bilan testlanadi.

### 15.3 Security-sensitive media holatlari tekshiriladi

Masalan:
- yomon filename
- noto‘g‘ri mime
- xavfli extension
- duplicate file metadata

---

## 16. Integration test qoidalari

### 16.1 Barcha narsani integration testga tiqib yuborilmaydi

Integration test faqat qatlamlar o‘zaro ishlashini tekshiradi.

### 16.2 Muhim integration scenariylar

Kamida:
- service + DB transaction
- bot handler + state + service
- worker + notification event lifecycle
- audit + service integration
- permission + service integration

### 16.3 Integration testlar ozroq, lekin load-bearing bo‘lsin

Ko‘p, sekin va takroriy integration testlar emas — muhim wiring point’lar testlanadi.

---

## 17. API test qoidalari

Agar API yozilsa:
- serializer validation testlanadi
- endpoint permission testlanadi
- pagination/filter testlanadi
- service chaqirilishi semanticsi tekshiriladi

ViewSet ishlatilmasligi qoidasi testingga ham taalluqli:
- explicit endpoint behavior test qilinadi

---

## 18. Admin test qoidalari

Har bir admin elementni test qilish shart emas.

Lekin critical admin workflow’lar uchun test yoziladi:
- readonly field behavior
- restricted permission
- custom admin action
- service-calling admin action
- dangerous action block

---

## 19. Test struktura qoidalari

### 19.1 Test fayl nomlari aniq bo‘lsin

Masalan:
- `test_create_car_service.py`
- `test_car_policies.py`
- `test_list_car_maintenance_records.py`
- `test_add_maintenance_flow.py`

### 19.2 Testlar domen bo‘yicha joylashtiriladi

Variantlar:
- app ichida `tests/`
- yoki markaziy `tests/`

Qaysi biri tanlansa ham izchil bo‘lsin.

### 19.3 Test nomlari behavior’ni ifodalasin

Yaxshi:
- `test_owner_can_share_car_with_other_user`
- `test_viewer_cannot_create_maintenance_record`
- `test_duplicate_update_does_not_create_second_record`

Yomon:
- `test_service_1`
- `test_ok`
- `test_main_case`

---

## 20. Factory, fixture va test data qoidalari

### 20.1 Factory-first yondashuv afzal

Test data yaratishda:
- factory
- builder
- explicit helper

ishlatiladi.

### 20.2 Minimal yetarli data

Kerak bo‘lmagan 10 ta object yaratish tavsiya etilmaydi.

### 20.3 Hidden coupling’dan qochiladi

Global katta fixture’lar testlarni noaniq va sinuvchan qiladi.

### 20.4 Default factory qiymatlari ma’noli bo‘lsin

Factory:
- realistik
- valid
- override qilish oson

bo‘lishi kerak.

---

## 21. Mock va external dependency qoidalari

### 21.1 Tashqi provider’lar mock/fake orqali testlanadi

Masalan:
- Telegram gateway
- AI provider
- OCR provider
- storage provider
- geocoding provider

### 21.2 Mock qilish chegarasi

Mock qilinadi:
- network boundary
- external provider
- time/random/uuid kerak bo‘lsa

Mock qilinmaydi:
- core business rule
- ORM behavior (keraksiz holda)
- selector logicni to‘liq soxtalashtirish

### 21.3 Over-mocking taqiqlanadi

Juda ko‘p mock testni yolg‘on xavfsizlikka aylantiradi.

---

## 22. Determinism va flaky testlarga qarshi qoidalar

### 22.1 Test deterministik bo‘lishi kerak

Testlar:
- random natija bermasligi
- vaqtga bog‘liq sirpanmasligi
- tashqi tarmoqqa chiqmasligi
- parallel ishlaganda sinmasligi

### 22.2 Vaqtni freeze qilish kerak bo‘lsa qilinadi

Reminder, scheduled event, expiry, notification time kabi joylarda vaqt nazorat ostida bo‘ladi.

### 22.3 Flaky test qabul qilinmaydi

“Ba’zan o‘tadi” test aslida bug.

---

## 23. Coverage qoidalari

### 23.1 Coverage raqam o‘zi maqsad emas

100% coverage talab qilinmaydi.

Lekin low-value coverage emas, **high-value coverage** kerak.

### 23.2 Majburiy qamrov joylari

Yuqori qamrov talab qilinadi:
- service layer
- policy layer
- state transition logic
- critical parserlar
- worker logic
- duplicate protection

### 23.3 Uncovered critical path qabul qilinmaydi

Agar critical use-case testlanmagan bo‘lsa, task done hisoblanmaydi.

---

## 24. Performance va query regressiya testlari

### 24.1 Har joyda query count testi shart emas

Lekin performance-sensitive path’larda foydali bo‘lishi mumkin:
- history list
- user cars list
- workshop review summary
- notification pending list

### 24.2 N+1 regressionlar qayta chiqsa, test bilan himoyalanadi

Bir marta N+1 topilgan path uchun regression test yozish tavsiya etiladi.

---

## 25. Regression test qoidalari

### 25.1 Har topilgan bug uchun regression test yoziladi

Bug fix test bilan birga keladi.

### 25.2 Incident-driven hardening

Agar production yoki staging’da xato topilsa:
- root cause aniqlanadi
- regression test yoziladi
- keyin fix yakunlangan hisoblanadi

---

## 26. Test review qoidalari

Review paytida quyidagi savollar beriladi:
1. Bu kodning muhim behavior’lari testlandimi?
2. Permission failure bormi?
3. Validation failure bormi?
4. Duplicate/idempotency ko‘rib chiqildimi?
5. Transaction failure partial state qoldirmaydimi?
6. Test juda brittle emasmi?
7. Test juda ko‘p mock bilan yolg‘on xavfsizlik bermayaptimi?
8. Regression uchun yetarli himoya bormi?

---

## 27. AI agentlar uchun qat’iy ko‘rsatmalar

AI agentlar quyidagilarga rioya qilishi shart:

1. Testsiz muhim service yozma.
2. Faqat happy path test yozib ketma.
3. Permission va validation case’larni unutma.
4. Duplicate/idempotency holatini albatta o‘yla.
5. Multi-step write uchun atomicity test yoz.
6. Worker task uchun retry/reprocess holatini tekshir.
7. Bot flow uchun cancel va invalid input case yoz.
8. Factory’ni haddan tashqari murakkablashtirma.
9. Mockni hamma narsaga ishlatma.
10. Flaky test yozma.
11. Snapshot bilan butun semanticsni almashtirma.
12. Regression bug uchun regression test yoz.
13. Audit talab qilingan actionni auditsiz test qilma.
14. Test nomini aniq yoz.
15. Testlarni “o‘tib ketishi” uchun emas, “xato ushlashi” uchun yoz.

---

## 28. Anti-patternlar

Quyidagilar qat’iyan taqiqlanadi:

- test yozmasdan feature tugatish
- faqat happy path test
- permission case yo‘q test
- validation case yo‘q test
- duplicate case yo‘q idempotent flow testi
- flaky test
- real networkga chiqadigan test
- keraksiz over-mocking
- noaniq test nomlari
- bitta testda juda ko‘p unrelated assertion
- brittle snapshot testlar
- regression bugsiz regression testsiz fix
- core business correctnessni faqat bot text bilan tekshirish

---

## 29. Definition of testing done

Testing task yoki feature done hisoblanadi, agar:

1. Core use-case testlangan bo‘lsa.
2. Success case bor bo‘lsa.
3. Validation failure bor bo‘lsa.
4. Permission failure bor bo‘lsa.
5. Edge case ko‘rib chiqilgan bo‘lsa.
6. Multi-step write bo‘lsa atomicity testlangan bo‘lsa.
7. Idempotency kerak bo‘lsa testlangan bo‘lsa.
8. Worker yoki bot flow bo‘lsa state/retry/cancel behavior testlangan bo‘lsa.
9. Audit talab qilinsa tekshirilgan bo‘lsa.
10. Testlar deterministic va o‘qilishi oson bo‘lsa.

---

## 30. Yakuniy prinsip

Bu loyihada testlar qo‘shimcha ish emas. Testlar — arxitekturaning bir qismi.

Har bir texnik qaror quyidagi savol bilan tekshiriladi:

**Agar ertaga shu kod o‘zgarsa, testlar bizni himoya qila oladimi?**

Agar javob yo‘q bo‘lsa, testing hali yetarli emas.
