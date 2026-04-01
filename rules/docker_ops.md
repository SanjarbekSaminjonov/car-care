# Docker & Operations Rules

## 1. Maqsad

Ushbu hujjat loyiha uchun Docker, Docker Compose, environment boshqaruvi, deploy, runtime operatsiyalar va production ops qoidalarini belgilaydi.

Bu loyiha:
- bitta VPS’da ishlashi mumkin
- Dockerized muhitda yuradi
- Nginx + Django + bot + worker + PostgreSQL stack’iga ega
- keyinchalik backup, monitoring, object storage, webhook, AI/OCR workerlari bilan kengayishi mumkin

Shu sababli infra va operations qarorlari:
- sodda, lekin production-ready
- qayta deploy qilish oson
- rollback qilish oson
- log va health ko‘rinadigan
- environment’lar orasida izchil
- AI agentlar uchun aniq

bo‘lishi kerak.

---

## 2. Asosiy prinsiplar

1. **One command to boot local stack**
2. **Environment parity**
3. **Immutable-ish containers**
4. **Config env orqali**
5. **Persistent data volumes orqali**
6. **Logs stdout/stderr ga**
7. **Graceful shutdown**
8. **Health checks majburiy**
9. **Secrets image ichiga bake qilinmaydi**
10. **Bot va worker alohida process/container**

---

## 3. Deploy modeli

### 3.1 Asosiy deploy modeli

Default deploy modeli:
- bitta VPS
- Docker Compose
- reverse proxy sifatida Nginx
- alohida containerlar:
  - `nginx`
  - `web`
  - `bot`
  - `worker`
  - `db`

Kelajakda qo‘shilishi mumkin:
- `backup`
- `pgbouncer`
- `minio`
- `ocr_worker`
- `ai_worker`

### 3.2 Single-host production acceptable

Loyiha boshida Kubernetes yoki murakkab orchestration shart emas.

Docker Compose yetarli, lekin:
- layout productionga mos
- container responsibility aniq
- restart behavior to‘g‘ri
- volumes/security/logging o‘ylangan

bo‘lishi kerak.

### 3.3 Local va production orasida farq minimal bo‘lsin

Local hack’lar production strukturasini buzmasligi kerak.

---

## 4. Container roli va chegaralari

### 4.1 `web` container

`web` container:
- Django application
- gunicorn (yoki mos WSGI runner)
- HTTP app serving
- management command’lar uchun image bazasi

### 4.2 `bot` container

`bot` container:
- `python manage.py runbot`
- Telegram update polling/webhook processing
- faqat bot process uchun

Bot `web` bilan bir process bo‘lib ketmasligi kerak.

### 4.3 `worker` container

`worker` container:
- `python manage.py runworker`
- periodic task / scheduled task / queue task processing
- reminder, notification, cleanup va future OCR/AI foundation

### 4.4 `db` container

`db` container:
- PostgreSQL
- persistent volume
- backup strategiyasi bilan

### 4.5 `nginx` container

`nginx` container:
- reverse proxy
- static/media serving
- TLS termination
- request buffering/limits
- upstream routing

---

## 5. Dockerfile qoidalari

### 5.1 Bitta asosiy app image

Default yondashuv:
- `web`, `bot`, `worker` bir xil image’dan ishlaydi
- entrypoint/command bilan farqlanadi

Bu image drift’ni kamaytiradi.

### 5.2 Image minimal bo‘lsin

Image:
- keraksiz package’lardan xoli
- deterministic build
- requirements lock strategiyasiga yaqin
- cache-friendly layer’lar bilan

bo‘lishi kerak.

### 5.3 Multi-stage build ko‘rib chiqiladi

Agar image katta yoki build dependency ko‘p bo‘lsa multi-stage build ishlatiladi.

### 5.4 Source code va secrets

Image ichiga:
- real `.env`
- secret key
- production credential
- local cache axlatlari

kiritilmaydi.

### 5.5 Non-root user afzal

Imkon qadar application container non-root user bilan ishlaydi.

Agar root kerak bo‘lsa, sababi aniq bo‘lishi kerak.

### 5.6 Dockerfile’da magic script’lar ko‘paymasin

Entrypoint:
- aniq
- qisqa
- idempotent
- kuzatish oson

bo‘lishi kerak.

---

## 6. Docker Compose qoidalari

### 6.1 Compose fayl aniq va o‘qilishi oson bo‘lsin

Service nomlari semantic bo‘lsin:
- `nginx`
- `web`
- `bot`
- `worker`
- `db`

Noaniq:
- `app1`
- `main`
- `service_x`

nomlar tavsiya etilmaydi.

### 6.2 `depends_on` yetarli emas

`depends_on` container start order beradi, readiness emas.

Shuning uchun:
- healthcheck
- retry
- wait-for-db strategiyasi

ko‘rib chiqiladi.

### 6.3 Restart policy aniq bo‘lsin

Production’da kamida quyidagilar ko‘rib chiqiladi:
- `unless-stopped`
- yoki mos restart policy

### 6.4 Named volume ishlatiladi

Persistent data uchun:
- postgres data
- media
- static collect output (kerak bo‘lsa)
- backup output

named volume yoki aniq bind mount ishlatiladi.

### 6.5 Networklar aniq bo‘lsin

Ichki service communication uchun Docker network ishlatiladi.

Tashqi portlar faqat kerakli servislar uchun ochiladi:
- odatda faqat `nginx`
- local dev’da ehtiyojga ko‘ra `db`

---

## 7. Environment va config boshqaruvi

### 7.1 Config env orqali

Quyidagilar env orqali boshqariladi:
- Django settings module
- DEBUG
- SECRET_KEY
- database URL/credentials
- Telegram token
- allowed hosts
- worker loop interval
- log level
- AI/OCR provider config
- upload/media limitlar
- backup config

### 7.2 `.env.example` majburiy

Repo ichida:
- `.env.example`

bo‘ladi.

Unda:
- barcha kerakli env nomlari
- izohlar
- sample value’lar

beriladi.

### 7.3 Real `.env` repoga kiritilmaydi

`.env`, `.env.prod`, secret fayllar git’da bo‘lmaydi.

### 7.4 Environmentlar o‘rtasida aniq farq bo‘lsin

Kamida:
- local
- production

Kerak bo‘lsa:
- staging

Environment-specific config aniq boshqariladi.

---

## 8. Entrypoint va startup qoidalari

### 8.1 Startup deterministic bo‘lsin

Container start bo‘lganda nima bo‘lishi aniq bo‘lishi kerak.

Masalan:
- web -> gunicorn
- bot -> runbot
- worker -> runworker

### 8.2 Automatic migration ehtiyotkorlik bilan

Production container har restart bo‘lganda ko‘r-ko‘rona migration ishlatishi tavsiya etilmaydi.

Migration:
- alohida release step
- yoki aniq boshqariladigan operation

bo‘lishi afzal.

### 8.3 Collectstatic strategiyasi aniq bo‘lsin

`collectstatic`:
- build time’da emas, odatda deploy/release step’da
- yoki controlled startup step’da

qilinadi.

Qaysi model tanlansa, documented bo‘lishi kerak.

### 8.4 Wait-for dependencies strategy

DB tayyor bo‘lmaganda app crash loop’ga tushib qolmasligi uchun:
- retry
- readiness wait
- explicit bootstrap check

bo‘lishi kerak.

---

## 9. Healthcheck va readiness qoidalari

### 9.1 Healthcheck majburiy

Kamida:
- `web`
- `bot`
- `worker`
- `db`

uchun health semantics ko‘rib chiqiladi.

### 9.2 Web health endpoint

`web` uchun yengil health endpoint bo‘ladi:
- app boot bo‘ldimi
- DB bilan gaplasha oladimi (kerakli levelda)
- minimal dependency holati

### 9.3 Bot health

Bot uchun health semantics:
- process tirikmi
- update loop ishlayaptimi
- oxirgi successful activity qachon bo‘lgan

### 9.4 Worker health

Worker uchun:
- process tirikmi
- scheduler loop ishlayaptimi
- stuck task alomatlari bormi

### 9.5 Readiness va liveness chalkashmasin

Health check “process bor” degani bilan cheklanmasin, lekin juda og‘ir ham bo‘lmasin.

---

## 10. Volumes va persistent data

### 10.1 Database data persistent bo‘lishi shart

Postgres data ephemeral bo‘lishi mumkin emas.

### 10.2 Media persistent bo‘lishi shart

User yuklagan media container restart/redeploy’da yo‘qolmasligi kerak.

### 10.3 Static output strategiyasi documented bo‘lsin

Agar static fayllar Nginx orqali berilsa:
- collect qayerga tushadi
- qanday volume/bind orqali ulanishi
- release jarayonida qanday yangilanishi

aniq bo‘lsin.

### 10.4 Backup output uchun alohida joy

Backup fayllari random container FS ichida qolib ketmasligi kerak.

---

## 11. Nginx qoidalari

### 11.1 Nginx reverse proxy sifatida ishlatiladi

Nginx:
- Django upstream’ga uzatadi
- static/media beradi
- upload limitni boshqaradi
- timeout/buffering strategiyasini qo‘llaydi

### 11.2 HTTPS production’da majburiy

Production’da TLS yoqilgan bo‘lishi kerak.

### 11.3 Request size limit o‘ylangan bo‘lsin

Media upload tufayli:
- `client_max_body_size`
- timeoutlar
- buffering

nazorat qilinadi.

### 11.4 Xavfsiz defaultlar

Keraksiz ochiq directory listing, debug config, default misconfig bo‘lmasligi kerak.

---

## 12. Logging va observability

### 12.1 Logs stdout/stderr ga

Container ichida local faylga yashirin log yozish default emas.

Primary log stream:
- stdout
- stderr

### 12.2 Har containerning roli bo‘yicha loglari aniq bo‘lsin

Masalan:
- web access/app logs
- bot update logs
- worker task logs
- nginx access/error logs
- postgres logs

### 12.3 Log rotation strategiyasi ko‘rib chiqiladi

Host darajasida yoki Docker logging driver darajasida disk to‘lib ketishi oldi olinadi.

### 12.4 Correlation va context

Imkon qadar loglarda:
- service/container nomi
- user id
- telegram user id
- request/task/update id
- status

ko‘rinsin.

---

## 13. Release va deploy qoidalari

### 13.1 Deploy qayta tiklanadigan bo‘lsin

Deployment:
- documented
- takrorlanadigan
- qo‘lda ham, script orqali ham bajariladigan

bo‘lishi kerak.

### 13.2 Build va run ajratiladi

Ideal flow:
1. image build
2. migration/release step
3. service restart/update
4. health verification

### 13.3 Rollback oson bo‘lsin

Agar release xato bo‘lsa:
- oldingi image’ga qaytish
- service qayta ishga tushirish
- data-migration xavfi oldindan baholash

ko‘rib chiqiladi.

### 13.4 Tag/versiya strategiyasi aniq bo‘lsin

`:latest`ga suyanib qolish tavsiya etilmaydi.

Image tag yoki release identifier documented bo‘lsin.

---

## 14. Migration va release operation

### 14.1 Migration deployning alohida bosqichi

Schema migration:
- web startupga yashirilmaydi
- aniq step sifatida bajariladi

### 14.2 Dangerous migrationlar oldindan ko‘rib chiqiladi

Katta jadval o‘zgarishi, lock, index, default backfill kabi risklar baholanadi.

### 14.3 Migration failure runbook bo‘lishi kerak

Agar migration xato bersa:
- nima qilinadi
- qayerdan log olinadi
- rollback qanday

documented bo‘ladi.

---

## 15. Backup va restore qoidalari

### 15.1 Backup majburiy

Kamida:
- PostgreSQL backup
- media backup strategiyasi

bo‘lishi kerak.

### 15.2 Restore test qilinadi

Backup borligi yetarli emas. Vaqti-vaqti bilan restore sinov qilinadi.

### 15.3 Backup retention

Retention siyosati bo‘ladi:
- kunlik
- haftalik
- kerak bo‘lsa oylik

### 15.4 Backup secure bo‘lsin

Backup:
- ochiq joyda yotmasligi
- permission nazoratida bo‘lishi
- kerak bo‘lsa encryption bilan

saqlanishi kerak.

---

## 16. Monitoring va alerting foundation

### 16.1 To‘liq monitoring keyin qo‘shilishi mumkin

Lekin foundation hozirdan bo‘lishi kerak:
- healthcheck
- log inspection
- disk usage awareness
- db storage awareness
- process restart awareness

### 16.2 Minimal ops checklist

Kamida kuzatiladi:
- bot ishlayaptimi
- worker ishlayaptimi
- DB volume to‘lib qolmayaptimi
- media disk o‘sishi
- backup ishlayaptimi

### 16.3 Silent failure taqiqlanadi

Worker yoki bot “jim ishlamay qolishi” eng xavfli holatlardan biri.

Heartbeats, health timestamp yoki shunga o‘xshash mexanizm ko‘rib chiqiladi.

---

## 17. Resource va performance qoidalari

### 17.1 Har containerning roli yengil va aniq bo‘lsin

Bitta container ichida:
- web
- bot
- worker
- scheduler
- backup

hammasini birga tiqish tavsiya etilmaydi.

### 17.2 Resource cheklovlari o‘ylab ko‘riladi

CPU/RAM limit yoki kamida kuzatuv bo‘lishi kerak.

### 17.3 OOM va disk-full xavfi

Bot va worker loglari yoki media upload diskni to‘ldirib qo‘ymasligi kerak.

---

## 18. Local development qoidalari

### 18.1 Local boot oson bo‘lsin

Yangi developer:
- repo clone
- `.env` tayyorlash
- `docker compose up`

bilan ishga tushira olishi kerak.

### 18.2 Local va production command farqi documented bo‘lsin

Local uchun:
- debug
- autoreload
- sample data

bo‘lishi mumkin, lekin production flow bilan chalkashmasin.

### 18.3 Local data reset oson bo‘lsin

Developer uchun DB/media reset strategiyasi documented bo‘lsin.

---

## 19. Security bilan bog‘liq ops qoidalari

### 19.1 Secrets imagega bake qilinmaydi

Yana ta’kid:
- token
- key
- password
- private config

image ichiga kirmaydi.

### 19.2 Minimal exposed ports

Production’da odatda faqat:
- 80/443 (Nginx)

ochiq bo‘ladi.

DB yoki internal servislar public chiqmaydi.

### 19.3 File permissionlar

Volume va mounted fayllar permissionlari o‘ylanadi, ayniqsa:
- postgres data
- media
- backup
- nginx certlar

### 19.4 Container escape yoki host-level xavflar

Keraksiz privileged mode, docker socket mount, host network kabi xavfli yondashuvlardan qochiladi.

---

## 20. AI agentlar uchun qat’iy ko‘rsatmalar

AI agentlar quyidagilarga rioya qilishi shart:

1. `web`, `bot`, `worker`ni bitta processga birlashtirma.
2. Secretlarni Dockerfile yoki compose ichida hardcode qilma.
3. Persistent datani ephemeral container FS’da qoldirma.
4. `.env`ni repo ichiga qo‘shma.
5. Startup script’larni noaniq va sehrli qilma.
6. Healthcheck’siz production compose yozma.
7. `depends_on`ni readiness deb o‘ylama.
8. Migrationni har startup’da ko‘r-ko‘rona run qiladigan xavfli flow yozma.
9. Faqat `latest` image tag’iga suyanma.
10. Loglarni faqat container ichidagi faylga yashirma.
11. Nginx config’da upload limit va static/media routingni unutma.
12. Backup strategiyasiz production tayyor deb hisoblama.
13. Bot yoki worker jim o‘lib qoladigan arhitekturani qoldirma.
14. Local-dev qulayligi deb production xavfsizligini buzma.
15. Future OCR/AI worker qo‘shishga to‘sqinlik qiladigan compose layout yozma.

---

## 21. Anti-patternlar

Quyidagilar qat’iyan taqiqlanadi:

- bitta container ichida hamma processni “bash bilan” yuritish
- real secretni image ichiga bake qilish
- postgres datani volumesiz ishlatish
- media’ni ephemeral FS’da qoldirish
- healthcheck’siz production deploy
- migrationni silent startup side-effect qilish
- DB portini keraksiz public ochish
- log rotation yoki disk growth’ni umuman hisobga olmaslik
- compose’ni noaniq service nomlari bilan yozish
- rollback o‘ylamasdan deploy qilish
- monitoring/heartbeat’siz worker yoki bot ishlatish
- Nginx’siz xom app serverni public internetga chiqarish
- ops jarayonini “faqat men bilaman” holatida qoldirish

---

## 22. Definition of docker/ops done

Docker/Ops bilan bog‘liq task done hisoblanadi, agar:

1. Container rollari aniq ajratilgan bo‘lsa.
2. Local va production config izchil bo‘lsa.
3. Secrets env orqali boshqarilsa.
4. Persistent data volumes bilan himoyalangan bo‘lsa.
5. Healthcheck mavjud bo‘lsa.
6. Logs stdout/stderr orqali olinadigan bo‘lsa.
7. Deploy/release qadamlari documented bo‘lsa.
8. Backup va restore strategiyasi mavjud bo‘lsa.
9. Nginx routing/static/media/TLS qoidalari o‘ylangan bo‘lsa.
10. Future workerlar va integratsiyalar qo‘shishga arxitektura ochiq bo‘lsa.

---

## 23. Yakuniy prinsip

Docker va operations qatlami “koddan keyingi mayda ish” emas.

U production ishonchlilikning o‘zi.

Har bir ops qarori quyidagi savol bilan tekshiriladi:

**Agar ertaga server restart bo‘lsa, deploy qayta qilinsa yoki bitta container o‘lsa, tizim nazorat ostida tiklana oladimi?**

Agar javob yo‘q bo‘lsa, ops dizayni hali tayyor emas.
