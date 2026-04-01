# Telegram Bot Rules

## 1. Maqsad

Ushbu hujjat Telegram bot qatlamini production-ready, boshqariladigan va keyinchalik web/mobile clientlar bilan birga ishlay oladigan tarzda qurish uchun majburiy qoidalarni belgilaydi.

Bu bot:
- oddiy command bot emas
- structured data bilan ishlovchi client
- stateful interaction interface
- service layer’dan foydalanuvchi transport qatlami
- keyinchalik API, mobile app, web app bilan parallel yashay oladigan tizimning birinchi client’i

Shu sababli Telegram bot kodi:
- domain logikadan ajratilgan
- state machine asosida
- duplicate update’ga chidamli
- restart-safe
- minimal typing, ko‘proq guided UX
- audit va idempotency bilan mos
- kelajakdagi AI, OCR, workshop marketplace va reminder scenario’lariga tayyor

bo‘lishi shart.

---

## 2. Botning arxitekturadagi roli

### 2.1 Bot = client / transport layer

Telegram bot backendning yuragi emas. U faqat:
- user input qabul qiladi
- interaction flow’ni boshqaradi
- service/selectorga murojaat qiladi
- natijani Telegram formatida qaytaradi

Bot quyidagilarni qilmasligi kerak:
- business rule saqlamasligi
- murakkab DB write orchestration qilmasligi
- permission qoidalarini mustaqil hal qilmasligi
- query optimization logikasini o‘zida saqlamasligi
- keyinchalik web/mobile reuse bo‘ladigan domain logikani yutib yubormasligi

### 2.2 Bot service layer’dan foydalanadi

Har bir muhim action:
- service orqali bajariladi
- selector orqali o‘qiladi
- policy orqali tekshiriladi

Bot handler faqat adapter rolini bajaradi.

### 2.3 Bot-first, lekin bot-bound emas

Kod shunday yozilmasligi kerakki:
- use-case faqat Telegram message formatida ishlasin
- response faqat Telegram text bo‘lsin
- state faqat bot ichida yashasin
- keyinchalik web/mobile client chiqsa, core logika qayta yozilsin

---

## 3. Ishlash modeli

### 3.1 Run modeli

Bot Django management command orqali ishlaydi.

Masalan:
- `python manage.py runbot`

Bu process:
- update’larni oladi
- router/dispatcher orqali handlerlarga uzatadi
- conversation state bilan ishlaydi
- xatolarni log qiladi
- graceful stop qila oladi

### 3.2 Polling hozir, webhook keyin bo‘lishi mumkin

Joriy bosqichda polling ishlatilishi mumkin.

Kelajakda webhook’ga o‘tish ehtimoli bo‘lgani uchun:
- update ingestion qatlami transportdan ajratilgan bo‘lishi kerak
- handlerlar polling/webhook farqidan bexabar bo‘lishi kerak

### 3.3 Bitta token uchun bitta update consumer

Bir Telegram bot tokeni uchun parallel, nazoratsiz ko‘p consumer ishlatish taqiqlanadi.

Aks holda:
- duplicate processing
- race condition
- state corruption

kelib chiqishi mumkin.

---

## 4. Tavsiya etilgan bot strukturasi

Quyidagi struktura afzal:

- `bot/routers/` — command/callback/message routing
- `bot/handlers/` — handlerlar
- `bot/flows/` — ko‘p bosqichli interaction flow’lar
- `bot/states/` — state nomlari va state contract’lar
- `bot/keyboards/` — inline/reply keyboard builderlar
- `bot/formatters/` — user-facing text va summary formatterlar
- `bot/parsers/` — user input parsing helperlari
- `bot/guards/` — update-level protection/helperlar
- `bot/context/` — bot context builder/helperlar
- `bot/exceptions/` — transport qatlamiga xos exception mapping
- `bot/dispatchers/` — update dispatch orchestration

Bot strukturasida ham qatlamlar aralashib ketmasligi kerak.

---

## 5. Handler qoidalari

### 5.1 Handler vazifasi

Handler:
- update’dan kerakli ma’lumotni oladi
- user contextni aniqlaydi
- kerakli flow yoki service’ni chaqiradi
- natijani formatter orqali tayyorlaydi
- reply yuboradi

### 5.2 Handler ichida nimalar bo‘lmasligi kerak

Handler ichida bo‘lmasligi kerak:
- murakkab business logic
- transaction
- bulk query yig‘ish
- audit orchestration
- permission logikasini qo‘lda yozish
- provider-agnostic domen qarorlari

### 5.3 Handlerlar kichik va aniq bo‘lsin

Bitta handler:
- bitta trigger yoki kichik scenario uchun
- o‘qilishi oson
- testlashga qulay
- side-effecti tushunarli

bo‘lishi kerak.

### 5.4 Handler nomlari aniq bo‘lsin

Yaxshi nomlar:
- `handle_start_command`
- `handle_add_car_entrypoint`
- `handle_select_car_for_maintenance`
- `handle_odometer_photo_message`
- `handle_cancel_flow`

Yomon nomlar:
- `main_handler`
- `process_message`
- `do_all`
- `universal_callback_handler`

---

## 6. Routing qoidalari

### 6.1 Routing explicit bo‘lsin

Command, callback, text message, media message va state-based routing aniq yoziladi.

Route’lar:
- o‘qilishi oson
- prioriteti tushunarli
- collision’ga chidamli
- default fallback’ga ega

bo‘lishi kerak.

### 6.2 Bitta update bir nechta handlerga ketib qolmasin

Dispatch qatlami buni nazorat qiladi.

Agar routing ambiguous bo‘lsa:
- aniq prioritet belgilanadi
- fallback strategy yoziladi

### 6.3 State-based routing command routingdan ajratiladi

Flow ichidagi user input bilan global command’lar aralashib ketmasligi kerak.

Masalan:
- `/cancel` har doim ishlashi mumkin
- lekin oddiy text message state bo‘yicha talqin qilinadi

---

## 7. Conversation state qoidalari

### 7.1 State DB’da saqlanadi

Bot state RAM’da saqlanadigan yagona truth bo‘lmasligi kerak.

State:
- database’da saqlanadi
- bot restart bo‘lsa tiklanadi
- bir user/chat uchun aniq boshqariladi

### 7.2 Har bir flow explicit state machine’ga ega bo‘lsin

Ko‘p bosqichli flow’lar aniq holatlarga bo‘linadi.

Masalan maintenance flow:
- `select_car`
- `input_date`
- `input_odometer`
- `select_service_type`
- `input_title`
- `input_line_items`
- `input_workshop`
- `input_notes`
- `attach_media`
- `confirm`

### 7.3 State payload tartibli bo‘lsin

State payload:
- minimal
- serializable
- versioning ehtimolini hisobga olgan
- kerakli fieldlargina saqlangan

bo‘lishi kerak.

Keraksiz raw update payload’ni state ichiga yozish taqiqlanadi.

### 7.4 State expiry bo‘lishi mumkin

Flow’lar abadiy ochiq qolmasligi kerak.

Kerakli joylarda:
- expiry time
- inactivity cleanup
- expired state bo‘yicha userga tushunarli javob

bo‘lishi kerak.

### 7.5 Bir userda bir vaqtda necha flow ochilishi aniq belgilansin

Default qoida:
- bitta user/chat uchun bitta aktiv asosiy flow

Murakkab parallel flow’lar default yondashuv emas.

---

## 8. Flow dizayn qoidalari

### 8.1 Flow’lar step-by-step va guided bo‘lsin

Bot UX:
- minimal typing
- maksimal tushunarli yo‘l-yo‘riq
- har bosqichda nima kutilayotgani aniq
- oldinga/orqaga/cancel strategiyasi bor

### 8.2 Har bir flowda confirm step bo‘lsin

Kritik write action oldidan summary ko‘rsatilib tasdiq olinadi.

Masalan:
- servis yozuvi yaratish
- access berish
- review yuborish
- odometer correction

### 8.3 Cancel har doim mavjud bo‘lsin

Ko‘p bosqichli flow’larda user:
- `/cancel`
- “Bekor qilish”
- kerak bo‘lsa inline cancel

orqali chiqib keta olishi kerak.

### 8.4 Invalid input recovery bo‘lsin

User noto‘g‘ri input yuborsa:
- flow sinib ketmaydi
- state yo‘qolmaydi
- aniq tushuntirish beriladi
- shu bosqich qayta so‘raladi

### 8.5 Flow textlari qisqa va aniq bo‘lsin

Bot ortiqcha uzun, chalkash matn yozmasligi kerak.

Lekin:
- talab tushunarli
- misol kerak bo‘lsa beriladi
- user keyingi qadamni darrov biladi

---

## 9. UX qoidalari

### 9.1 Telegram-native UX

Bot Telegram muhitiga mos yoziladi:
- reply keyboard
- inline keyboard
- callback action
- compact summary
- media caption
- short prompts

### 9.2 Minimal typing, maksimal tanlash

Iloji boricha user:
- button bosadi
- variant tanlaydi
- structured input yuboradi

Erkin text faqat kerak bo‘lganda olinadi.

### 9.3 Har bir javob userga keyingi qadamni ko‘rsatsin

“Done” yoki “xatolik” degan yalang‘och javob yetarli emas.

Bot:
- nima bo‘ldi
- keyin nima qila oladi
- flow qayerdaligini

tushunarli ko‘rsatadi.

### 9.4 Long history chunk’lab beriladi

Tarix yoki katta list:
- paginate qilinadi
- chunk’lanadi
- summary bilan beriladi

Telegram message limitlari e’tiborga olinadi.

### 9.5 Accessibility va tushunarlilik

Emoji ishlatilishi mumkin, lekin:
- semantikaga xizmat qilsin
- ortiqcha bo‘lmasin
- professional uslub buzilmasin

---

## 10. Keyboard qoidalari

### 10.1 Keyboard builderlar alohida qatlamda bo‘lsin

Inline va reply keyboard kodlari handler ichida qo‘lda yig‘ilmaydi.

Ular alohida builder/helper’larda bo‘ladi.

### 10.2 Callback data aniq va versionable bo‘lsin

Callback data:
- qisqa
- parse qilish oson
- collision’ga chidamli
- kerak bo‘lsa namespace’li

bo‘lishi kerak.

Masalan:
- `car:select:<id>`
- `maintenance:confirm:<draft_id>`
- `share:approve:<request_id>`

### 10.3 Juda katta keyboard qilinmaydi

Ko‘p item bo‘lsa:
- paginate
- search flow
- grouping

ishlatiladi.

Telegram UI’ni buzadigan ulkan keyboard taqiqlanadi.

---

## 11. Formatter qoidalari

### 11.1 User-facing text formatterlarda bo‘lsin

Summary, detail view, confirmation matni, list item presentation alohida formatterlarda bo‘lishi kerak.

Handler ichida katta format string yozish tavsiya etilmaydi.

### 11.2 Formatter business qaror qabul qilmaydi

Formatter:
- berilgan ma’lumotni userga ko‘rsatadi
- lekin kim ko‘ra oladi, nimalar hisoblanadi, qaysi yozuv tanlanadi — buni hal qilmaydi

### 11.3 Formatter reusable bo‘lsin

Bitta entity uchun:
- short summary
- detail summary
- confirmation summary

alohida reusable formatterlar bo‘lishi mumkin.

---

## 12. Parser qoidalari

### 12.1 Erkin text parsing alohida qatlamda bo‘lsin

Masalan:
- odometr sonini parse qilish
- sana parse qilish
- narx parse qilish
- mashina raqamini normalize qilish

handler ichida qo‘lda qilinmaydi.

### 12.2 Parsing tolerant, lekin aniq bo‘lsin

Bot kichik user xatolariga sabrli bo‘lishi mumkin, lekin:
- noaniq input’ni taxmin bilan commit qilmaydi
- kerak bo‘lsa qayta tasdiq so‘raydi

### 12.3 OCR va AI parsing parser/service qatlamiga ulanadi

Kelajakda:
- odometer image OCR
- receipt extraction
- AI-based intent parsing

qo‘shilganda ham handlerlar minimal o‘zgarishi kerak.

---

## 13. Update processing qoidalari

### 13.1 Duplicate update protection majburiy

Telegram update qayta kelishi mumkin.

Shu sababli:
- processed update registry
- idempotent handler/service design
- deduplication strategy

bo‘lishi kerak.

### 13.2 Har bir update log qilinadi, lekin ehtiyotkorlik bilan

Kamida quyidagilar bilan:
- update_id
- telegram_user_id
- chat_id
- update_type
- routing_result
- error_status

Lekin full raw payload doim log qilinmaydi.

### 13.3 Unknown update graceful ishlanadi

Bot tushunmaydigan update olsa:
- crash qilmaydi
- log qiladi
- kerak bo‘lsa userga neutral javob beradi
- routingni buzmaydi

### 13.4 Update processing restart-safe bo‘lsin

Bot process restart bo‘lsa:
- state yo‘qolmasligi
- duplicate create bo‘lmasligi
- polling offset noto‘g‘ri yurib ketmasligi

kerak.

---

## 14. Error handling qoidalari

### 14.1 User-facing xatolar tushunarli bo‘lsin

Domain error userga:
- oddiy
- qisqa
- actionable

ko‘rinishda beriladi.

Masalan:
- “Bu mashinaga sizda access yo‘q.”
- “Yuborgan odometr qiymati avvalgisidan kichik bo‘lib qoldi.”
- “Bu flow eskirib qolgan, qaytadan boshlang.”

### 14.2 Internal xato userga sizib chiqmaydi

Traceback, raw DB error, provider response userga ko‘rsatilmaydi.

Ular logga yoziladi.

### 14.3 Transport error va domain error ajratiladi

Masalan:
- Telegram API timeout
- media download xatosi
- OCR provider xatosi

transport/infra xato.

Masalan:
- access yo‘q
- noto‘g‘ri state
- invalid amount

domain xato.

### 14.4 Flow error state’ni buzib yubormasin

Agar oraliq xato bo‘lsa:
- state saqlanadimi yoki tozalanadimi aniq qaror bo‘ladi
- userni “osilib qolgan” flow’da qoldirish taqiqlanadi

---

## 15. Permissions va user context

### 15.1 Har update’da user context aniqlanadi

Bot:
- Telegram userni topadi yoki yaratadi
- tegishli internal userga bog‘laydi
- active/block holatini tekshiradi

### 15.2 Permissionlar policy orqali tekshiriladi

Handler ichida random `if owner` yoki `if user_id == ...` usulida permission yozilmaydi.

### 15.3 Multi-user, multi-car model aniq ishlashi kerak

Bot bir userning ko‘p mashinasi va bir mashinaning ko‘p useri borligini to‘liq hisobga oladi.

Har bir action’da:
- qaysi mashina kontekstida ishlayotgani
- userning roli nima
- bu actionga haqqi bormi

aniq bo‘lishi kerak.

---

## 16. Media handling qoidalari

### 16.1 Bot media bilan ishlay olishi kerak

Qo‘llab-quvvatlanadigan media:
- image
- video
- document
- audio/voice

### 16.2 Media qabul qilish transport va domain qatlamiga bo‘linadi

Bot:
- Telegram file metadata oladi
- kerakli adapter/service’ga uzatadi
- resultni userga ko‘rsatadi

Media storage, validation, linking service qatlamida bajariladi.

### 16.3 Media upload flow’da confirm yoki summary bo‘lishi mumkin

Kritik flow’larda media biriktirish:
- optional
- skip qilinadigan
- yakuniy summary ichida ko‘rinadigan

bo‘lishi kerak.

### 16.4 Odometer image future-ready bo‘lsin

Panel rasmi yuborilganda keyinchalik:
- OCR queue’ga yuborish
- confidence natija olish
- userga confirm qildirish

oson qo‘shilishi kerak.

---

## 17. Notification va proaktiv bot qoidalari

### 17.1 Bot faqat reaktiv emas, proaktiv ham bo‘ladi

Kelajakda bot:
- odometr so‘rashi
- servis vaqti yaqinlashganini aytishi
- reminder yuborishi
- unusual spending yoki tavsiya yuborishi

mumkin.

Shuning uchun outgoing notification flow ham first-class concern.

### 17.2 Notification yuborish alohida service/worker bilan boshqariladi

Bot handler o‘zi bevosita “hamma joyda send” qilmaydi.

Notification:
- event sifatida yaratiladi
- worker tomonidan yuboriladi
- status yuritiladi
- retry mumkin bo‘ladi

### 17.3 Notification spam bo‘lmasligi kerak

Qoidalar:
- deduplication
- cooldown
- user relevance
- schedule awareness

bo‘lishi kerak.

---

## 18. Reminder va recommendation integration

### 18.1 Bot recommendation engine’ning UI qatlami bo‘ladi

Reminder va recommendation hisoblash service/worker qatlamida bo‘ladi.
Bot esa:
- ko‘rsatadi
- tasdiq oladi
- actionga yo‘naltiradi

### 18.2 Rule-based foundation saqlanadi

AI bo‘lmasa ham:
- reminder
- maintenance due signal
- oddiy tavsiyalar

ishlashi kerak.

### 18.3 AI optional enhancement

AI qo‘shilganda bot:
- AI javobini userga ko‘rsatishi mumkin
- lekin AI yo‘q bo‘lsa core flow ishlashda davom etadi

---

## 19. Workshop / marketplace integration

### 19.1 Usta flow’lari alohida dizayn qilinadi

Kelajakda workshop userlari uchun flow’lar bo‘lishi mumkin:
- profil yaratish
- servis qo‘shish
- lokatsiya kiritish
- review ko‘rish
- so‘rov qabul qilish

### 19.2 Workshop domeni car owner flow’iga aralashib ketmaydi

Workshop flow’lari:
- alohida command/menu entrypoint
- alohida permission
- alohida service/selectorga ega bo‘ladi

### 19.3 Bot marketplace logic’ni “quick hack” qilib bir joyga tiqmaydi

Kelajakdagi marketplace uchun handlerlar ham service-oriented bo‘lishi kerak.

---

## 20. Logging va observability

### 20.1 Bot loglari strukturalashgan bo‘lsin

Loglarda kerak bo‘lsa:
- update_id
- telegram_user_id
- internal_user_id
- chat_id
- handler_name
- flow_name
- state_name
- service_name
- result
- error_type

bo‘lsin.

### 20.2 Sensitive data log qilinmaydi

Quyidagilar log qilinmaydi:
- bot token
- private media URL
- secretlar
- full raw personal data
- keraksiz full message dump

### 20.3 Lifecycle loglar mavjud bo‘lsin

Bot start/stop/restart, polling health, provider xatolari, state cleanup kabi muhim lifecycle eventlar log qilinadi.

---

## 21. Reliability qoidalari

### 21.1 Bot crash-resistant bo‘lsin

Bitta user xatosi yoki bitta update xatosi butun botni yiqitmasligi kerak.

### 21.2 Graceful shutdown bo‘lsin

Bot to‘xtatilganda:
- polling to‘g‘ri yakunlanadi
- oraliq offset/state xavfsiz tugaydi
- log yoziladi

### 21.3 Retry strategiyasi bo‘lsin

Telegram send yoki provider xatolari uchun:
- retryable
- non-retryable

xatolar ajratiladi.

### 21.4 Rate limit va backoff hisobga olinadi

Telegram API limitlari va burst traffic e’tiborga olinadi.

---

## 22. Testing qoidalari

### 22.1 Bot testlari faqat snapshot text test emas

Testlanadi:
- routing
- state transition
- handler behavior
- invalid input recovery
- callback parsing
- service integration boundary

### 22.2 Core correctness botga bog‘liq bo‘lmaydi

Asosiy business correctness service testlarida bo‘ladi.
Bot testlari:
- interaction correctness
- state correctness
- transport mapping

uchun.

### 22.3 Flow testlari majburiy

Kritik flow’lar test qilinadi:
- add car
- add maintenance
- add odometer
- share flow
- cancel flow
- invalid input recovery

---

## 23. AI agentlar uchun qat’iy ko‘rsatmalar

AI agentlar quyidagilarga rioya qilishi shart:

1. Handler ichiga business logic yozma.
2. State’ni RAM’dagi dict’da truth sifatida saqlama.
3. Duplicate update masalasini e’tiborsiz qoldirma.
4. Router’ni noaniq wildcard handler’lar bilan iflos qilma.
5. Callback data’ni tartibsiz va parse qilib bo‘lmaydigan qilma.
6. Har flow’ga cancel strategiyasi ber.
7. Har kritik write flow’ga confirm step qo‘sh.
8. Formatter va keyboard builderlarni handler ichiga tiqma.
9. Permissionlarni policy orqali tekshir.
10. Botni faqat Telegram uchun yozib, future web/mobile reuse’ni sindirma.
11. Long list/history’ni bitta xabarga tiqma.
12. Xatoda userni osilib qolgan state’da qoldirma.
13. Media/OCR/AI integrationni handlerga qattiq bog‘lama.
14. Worker bilan yuboriladigan notificationlarni handler ichida bevosita send qilib yuborma.
15. Log yozayotganda private ma’lumotni oshkor qilma.

---

## 24. Anti-patternlar

Quyidagilar qat’iyan taqiqlanadi:

- business logic’ni handler ichiga yozish
- state’ni faqat RAM’da saqlash
- duplicate update protection’siz polling
- universal “one handler for everything” yondashuvi
- callback data’ni noaniq string qilib yozish
- confirm step’siz kritik write flow
- cancel’siz multi-step flow
- invalid input’da flow’ni sindirish
- history/list’larni paginationsiz yuborish
- formatter va keyboard kodini handler ichida aralashtirish
- policy o‘rniga handlerda permission yozish
- provider xatosini userga raw ko‘rsatish
- notification logic’ni ad hoc yuborish
- botni bot-bound qilib yozish

---

## 25. Definition of Telegram bot done

Telegram bot bilan bog‘liq task done hisoblanadi, agar:

1. Handler/service/selector/policy chegaralari saqlangan bo‘lsa.
2. Flow state DB’da boshqarilsa.
3. Invalid input recovery mavjud bo‘lsa.
4. Cancel strategiyasi mavjud bo‘lsa.
5. Kritik write’larda confirm bosqichi bo‘lsa.
6. Duplicate update va idempotency ko‘rib chiqilgan bo‘lsa.
7. Logging va error handling foydali bo‘lsa.
8. Keyboard/formatter qatlamlari ajratilgan bo‘lsa.
9. Permissionlar to‘g‘ri tekshirilgan bo‘lsa.
10. Future OCR/AI/reminder/workshop extensibility buzilmagan bo‘lsa.

---

## 26. Yakuniy prinsip

Telegram bot bu loyihaning birinchi va asosiy client’i, lekin yagona haqiqat markazi emas.

Har bir qaror quyidagi savol bilan tekshiriladi:

**Bu bot qatlami keyinchalik yangi feature, yangi client yoki yangi integration qo‘shishni osonlashtiryaptimi yoki qiyinlashtiryaptimi?**

Agar qiyinlashtirayotgan bo‘lsa, bot dizayni qayta ko‘rib chiqiladi.
