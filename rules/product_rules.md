# Product Rules

## 1. Umumiy prinsiplar

Ushbu loyiha:
- Telegram-first platforma
- structured data asosida ishlovchi tizim
- multi-user, multi-car collaboration platforma
- future-ready (AI, OCR, EV, marketplace)

### Asosiy prinsiplar

1. **Telegram’dan chiqmasdan ishlash**
   - foydalanuvchi barcha asosiy ishlarni bot orqali bajaradi

2. **Structured data > chat**
   - har bir yozuv DB’da aniq strukturada saqlanadi

3. **Bot = interface**
   - business logic bot ichida emas
   - service layer ichida

4. **Auditability**
   - har bir muhim action log qilinadi

5. **Extensibility**
   - yangi feature qo‘shish mavjud tizimni buzmasligi kerak

---

## 2. User va access qoidalari

### 2.1 User identity

- user Telegram orqali identifikatsiya qilinadi
- Telegram account → internal User ga map qilinadi

---

### 2.2 Mashina ownership

- bitta user → ko‘p mashina
- bitta mashina → ko‘p user

---

### 2.3 Access modeli

Access faqat quyidagi usullar orqali beriladi:

#### ✅ Ruxsat etiladi:
- invite link (token)
- owner tasdiqlashi orqali request

#### ❌ Ruxsat etilmaydi:
- faqat davlat raqamini bilgan uchun avtomatik access

---

### 2.4 Role’lar

#### Owner
- to‘liq nazorat

#### Manager
- yozuv qo‘shadi va o‘zgartiradi

#### Viewer
- faqat ko‘radi

---

## 3. Mashina modeli qoidalari

### 3.1 Identifikatsiya

- asosiy identifikator: UUID
- plate number normalize qilinadi

---

### 3.2 Powertrain

Har bir mashinada:

- `ice`
- `hybrid`
- `ev`

bo‘lishi kerak

Bu kelajak uchun majburiy.

---

### 3.3 Odometr

- har bir servisda odometr saqlanadi
- alohida `OdometerEntry` ham yuritiladi
- `Car.current_odometer` cache sifatida ishlatiladi

---

## 4. Servis va xarajat qoidalari

### 4.1 Maintenance record

Har bir servis quyidagilarni o‘z ichiga oladi:

- sana
- odometr
- servis turi
- izoh
- workshop (optional)
- total summa

---

### 4.2 Line item

Har bir servis ichida:

- part
- labor
- fluid
- filter
- boshqa

bo‘lishi mumkin

---

### 4.3 Payer vs Creator

Har bir yozuvda:

- `created_by`
- `paid_by_user` yoki `paid_by_label`

bo‘lishi shart

---

### 4.4 Edit qoidasi

- edit qilish mumkin
- lekin audit log yoziladi

---

## 5. Media qoidalari

### 5.1 Media turlari

- image
- video
- document
- audio

---

### 5.2 Saqlash

- media DB’da emas, filesystem’da
- DB’da metadata

---

### 5.3 Bog‘lanish

Media:
- maintenance record bilan bog‘lanadi
- boshqa entity’lar bilan ham bog‘lanishi mumkin

---

## 6. Telegram UX qoidalari

### 6.1 Interaction modeli

Bot:
- step-by-step flow
- state saqlaydi

---

### 6.2 Commandlar

Minimal:

- /start
- menu
- add car
- add service
- history
- share

---

### 6.3 UX talablari

- minimal typing
- ko‘proq button
- har bir step aniq bo‘lishi kerak
- cancel imkoniyati bo‘lishi kerak

---

## 7. Notification va reminder qoidalari

### 7.1 Notification tipi

- reminder
- system message
- insight

---

### 7.2 Reminder trigger

- mileage-based
- time-based

---

### 7.3 Smart notification (future)

- userdan odometr so‘rash
- servis yaqinlashgani haqida ogohlantirish
- unusual spending aniqlash

---

## 8. Recommendation qoidalari

### 8.1 Rule-based (v1)

- standart interval asosida

---

### 8.2 Future

- car type + history asosida
- AI yordamida

---

## 9. Odometr OCR (future)

### 9.1 Flow

- user rasm yuboradi
- OCR ishlaydi
- natija tasdiqlanadi

---

### 9.2 Requirement

- manual override bo‘lishi kerak
- confidence score saqlanadi

---

## 10. Workshop / Usta marketplace

### 10.1 Usta profili

- nom
- logo
- telefon
- location
- xizmatlar

---

### 10.2 Review

- rating
- comment

---

### 10.3 Qoidalar

- fake review oldini olish kerak
- future’da verification qo‘shiladi

---

## 11. AI qoidalari

### 11.1 Optional layer

AI:
- majburiy emas
- fallback bo‘lishi kerak

---

### 11.2 Use case

- insight
- recommendation
- Q&A

---

### 11.3 Provider abstraction

- AI provider almashishi mumkin

---

## 12. Data integrity

- transaction ishlatiladi
- duplicate yozuvlar oldi olinadi
- audit log majburiy

---

## 13. Anti-patternlar

❌ Bot ichida business logic  
❌ Hardcoded qoidalar  
❌ Plate orqali auth  
❌ State yo‘qoladigan flow  
❌ Audit logsiz write  

---

## 14. Definition of correct product behavior

Tizim to‘g‘ri ishlayapti agar:

- user chalkashmaydi
- data yo‘qolmaydi
- history aniq
- kim nima qilgani ko‘rinadi
- kelajak feature qo‘shish oson