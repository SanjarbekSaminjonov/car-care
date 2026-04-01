# Security Rules

## 1. Maqsad

Ushbu hujjat loyiha xavfsizligini ta’minlash uchun majburiy qoidalarni belgilaydi.

Bu loyiha:
- Telegram bot
- user data (car history, expenses)
- media fayllar
- kelajakda AI va marketplace

bilan ishlaydi.

Shu sababli security:
- boshidan to‘g‘ri qurilishi kerak
- keyin qo‘shiladigan narsa emas

---

## 2. Asosiy prinsiplar

1. **Least privilege**
2. **Fail secure**
3. **Explicit access control**
4. **No trust to user input**
5. **Auditability**

---

## 3. Auth va identity

### 3.1 Telegram ishonchli manba emas

Telegram user:
- faqat transport identity
- to‘liq trust qilinmaydi

Har doim:
- internal user bilan map qilinadi

---

### 3.2 User impersonation yo‘q

Hech qachon:
- query param orqali user tanlanmaydi
- raw user_id orqali action qilinmaydi

---

## 4. Authorization

### 4.1 Policy majburiy

Permission faqat:
- policy layer orqali

---

### 4.2 Object-level access

Har action:
- user + object asosida tekshiriladi

---

## 5. Input validation

### 5.1 Hech qanday input trusted emas

User yuborgan:
- text
- file
- callback data

hammasi validate qilinadi

---

### 5.2 Callback data

- parse qilinadi
- verify qilinadi
- raw ishlatilmaydi

---

## 6. Media security

### 6.1 File validation

Tekshiriladi:
- extension
- mime
- size

---

### 6.2 Xavfli fayllar

Quyidagilar bloklanadi:
- executable
- script
- suspicious mime

---

### 6.3 File path

- sanitize qilinadi
- traversal imkoni yo‘q

---

## 7. Secrets management

### 7.1 Code ichida secret yo‘q

- tokenlar
- API keylar
- DB password

faqat env orqali

---

### 7.2 .env xavfsizligi

- gitignore’da
- faqat example repo’da

---

## 8. Logging xavfsizligi

### 8.1 Sensitive data log qilinmaydi

- token
- password
- private file
- raw user data

---

## 9. API / bot security

### 9.1 Rate limiting

Spam va abuse oldi olinadi

---

### 9.2 Replay protection

Duplicate update nazorat qilinadi

---

## 10. Database security

### 10.1 Least privilege DB user

- faqat kerakli huquqlar

---

### 10.2 SQL injection

- ORM ishlatiladi
- raw SQL ehtiyotkor

---

## 11. Admin security

### 11.1 Admin yopiq

- strong password
- HTTPS
- cheklangan access

---

## 12. External integration

### 12.1 Provider trust qilinmaydi

AI/OCR:
- natija validate qilinadi

---

## 13. Backup

- muntazam backup
- restore test

---

## 14. AI agentlar uchun

1. Secretni hardcode qilma
2. Permissionni bypass qilma
3. Inputni validate qil
4. Media’ni tekshir
5. Policy ishlat

---

## 15. Anti-patternlar

- hardcoded token
- raw SQL
- validation yo‘q
- admin ochiq
- full debug log

---

## 16. Definition of done

Security done agar:
- input validate qilinadi
- permission tekshiriladi
- secret himoyalangan
- log xavfsiz
- media xavfsiz

---

## 17. Yakuniy prinsip

**Security buzilsa, hamma narsa buziladi.**
