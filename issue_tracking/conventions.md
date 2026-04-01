# Issue Tracking Conventions

## 1. Maqsad

Bu hujjat tasklar qanday yozilishi, bajarilishi va holati qanday boshqarilishini belgilaydi.

Bu system:
- AI agentlar uchun ishlaydi
- deterministic bo‘lishi kerak
- noaniqlik bo‘lmasligi kerak

---

## 2. Task lifecycle

Har bir task quyidagi lifecycle’dan o‘tadi:

1. todo → bajarilmagan
2. active → bajarilmoqda
3. done → tugagan

---

## 3. Task formati

Har bir task alohida `.md` fayl bo‘ladi.

Struktura:

- title
- description
- requirements
- acceptance criteria
- notes (optional)

---

## 4. Task naming

Format: `TASK-<number>_<short_name>.md


Misol:
- TASK-001_create_user_model.md
- TASK-002_create_car_model.md

---

## 5. Acceptance criteria (ENG MUHIM)

Har taskda bo‘lishi shart.

AI agent taskni tugatgan hisoblanadi faqat:
- barcha acceptance criteria bajarilganda

---

## 6. Task size

Task:
- 1–3 soatlik ish bo‘lishi kerak
- juda katta bo‘lmasin
- juda kichik ham bo‘lmasin

---

## 7. Definition of done

Task done agar:
- code yozilgan
- test yozilgan
- rules buzilmagan
- acceptance criteria bajarilgan

---

## 8. Anti-patternlar

❌ “Car model yozish” (juda umumiy)  
❌ Acceptance criteria yo‘q  
❌ Testsiz task  
❌ 10 ta ishni bitta taskga tiqish  

---

## 9. AI agent uchun qoidalar

1. Taskni to‘liq o‘qi
2. Acceptance criteria’ni checklist sifatida ishlat
3. Taskdan tashqariga chiqma
4. Tugatgandan keyin self-check qil
5. Qoidalarni buzma (rules/** ga qarab)

---

## 10. Yakuniy prinsip

**Agar task noaniq bo‘lsa — u task emas.**
