# دليل تنصيب منصة GACMS على سيرفر محلي

هذا الدليل يشرح تنصيب **نظام إدارة أصول المجموعة (GACMS)** خطوة بخطوة على جهازك المحلي فقط (بدون Docker).

---

## المتطلبات الأساسية

- **Python 3.11** أو أحدث ([تحميل Python](https://www.python.org/downloads/))
- **PostgreSQL 14** أو أحدث ([تحميل PostgreSQL](https://www.postgresql.org/download/))
- **Git** (اختياري، إذا كان المشروع من مستودع)

---

## الخطوة 1: تثبيت PostgreSQL وإنشاء قاعدة البيانات

### على Windows

1. ثبّت PostgreSQL من الموقع الرسمي وشغّل المُثبِّت.
2. احفظ كلمة مرور مستخدم `postgres` التي تُعيّنها أثناء التثبيت.
3. افتح **pgAdmin** أو **Command Line** المتوفر مع PostgreSQL.

### إنشاء قاعدة البيانات والمستخدم

افتح **SQL Shell (psql)** أو **pgAdmin → Query Tool** ونفّذ:

```sql
-- إنشاء مستخدم (إذا أردت مستخدمًا مخصصًا)
CREATE USER gacms WITH PASSWORD 'gacms_secret';

-- إنشاء قاعدة البيانات
CREATE DATABASE gacms OWNER gacms;

-- منح الصلاحيات
GRANT ALL PRIVILEGES ON DATABASE gacms TO gacms;
\c gacms
GRANT ALL ON SCHEMA public TO gacms;
```

إذا استخدمت مستخدم `postgres` نفسه، أنشئ فقط قاعدة البيانات:

```sql
CREATE DATABASE gacms;
```

---

## الخطوة 2: فتح مجلد المشروع

- إذا المشروع داخل مجلد (مثل `d:\STC\Asset`):

```bash
cd d:\STC\Asset
```

- أو استنساخ من Git:

```bash
git clone <رابط-المستودع> Asset
cd Asset
```

---

## الخطوة 3: إنشاء بيئة افتراضية (venv) وتفعيلها

```bash
python -m venv .venv
```

**تفعيل البيئة:**

- **Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

- **Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

- **Linux / macOS:**
```bash
source .venv/bin/activate
```

بعد التفعيل يظهر اسم البيئة مثل: `(.venv)` في بداية السطر.

---

## الخطوة 4: تثبيت الحزم

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

قد يستغرق التثبيت دقائق (خاصة WeasyPrint لإنشاء PDF).

### ملاحظة لـ WeasyPrint (PDF) على Windows

لتصدير مستندات PDF بشكل صحيح قد تحتاج تثبيت **GTK3 Runtime**:

- تحميل من: [GTK3 Runtime for Windows](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases)
- أو استخدام WeasyPrint كما هو؛ إن ظهرت أخطاء متعلقة بـ GTK فثبّت الـ Runtime أعلاه.

---

## الخطوة 5: إعداد ملف البيئة (.env)

1. انسخ الملف النموذجي:

```bash
copy .env.example .env
```

(على Linux/macOS: `cp .env.example .env`)

2. افتح `.env` بمحرر نصوص وعدّل القيم التالية حسب بيئتك المحلية:

| المتغير | الوصف | مثال للسيرفر المحلي |
|--------|--------|----------------------|
| `DATABASE_URL` | رابط اتصال PostgreSQL | `postgresql+asyncpg://gacms:gacms_secret@localhost:5432/gacms` |
| `SECRET_KEY` | مفتاح سري لـ JWT (32 حرفًا على الأقل) | أي نص طويل عشوائي |
| `SCAN_BASE_URL` | عنوان المنصة للمسح (QR) | `http://localhost:8000` |
| `QR_SIGNING_SECRET` | مفتاح توقيع روابط QR | أي نص سري |

**مثال لمقطع من `.env`:**

```env
DATABASE_URL=postgresql+asyncpg://gacms:gacms_secret@localhost:5432/gacms
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
SCAN_BASE_URL=http://localhost:8000
QR_SIGNING_SECRET=qr-signing-secret-change-in-production
UPLOAD_DIR=./uploads
PDF_OUTPUT_DIR=./generated_pdfs
```

احفظ الملف بعد التعديل.

---

## الخطوة 6: تشغيل ترحيلات قاعدة البيانات (Alembic)

لتطبيق الجداول والإصدارات على قاعدة البيانات:

```bash
alembic upgrade head
```

يجب أن تظهر رسائل تؤكد تطبيق الترحيلات بنجاح.

---

## الخطوة 7: إدخال البيانات الأولية (Seed)

لإنشاء مجموعة وشركة وفرع ومستخدم افتراضي:

```bash
python scripts/seed.py
```

**بيانات الدخول الافتراضية:**

- **البريد:** `admin@gacms.example.com`
- **كلمة المرور:** `Admin123!`

---

## الخطوة 8: تشغيل السيرفر

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **الواجهة الأمامية (عربي):**  
  افتح المتصفح على: **http://localhost:8000**

- **واجهة API (Swagger):**  
  **http://localhost:8000/docs**

- **الواجهة تُقدَّم من نفس السيرفر** (لا حاجة لتشغيل frontend منفصل).

---

## التحقق من التنصيب

1. افتح **http://localhost:8000** في المتصفح.
2. سجّل الدخول بـ `admin@gacms.example.com` / `Admin123!`.
3. يجب أن تظهر لوحة التحكم والقوائم الجانبية بالعربية.

---

## أوامر مفيدة لاحقًا

| المهمة | الأمر |
|--------|--------|
| تشغيل السيرفر | `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` |
| ترحيلات جديدة بعد تعديل النماذج | `alembic revision --autogenerate -m "وصف"` ثم `alembic upgrade head` |
| إعادة البيانات الأولية | `python scripts/seed.py` |
| إيقاف السيرفر | `Ctrl+C` في نفس نافذة الطرفية |

---

## إعادة تعيين قاعدة البيانات (Database reset)

إذا واجهت أخطاء ترحيل أو تريد بدءًا نظيفًا:

1. **إسقاط كل الجداول وإعادة الترحيل من الصفر (PostgreSQL):**
   - افتح **psql** أو **pgAdmin** واتصل بقاعدة `gacms`.
   - نفّذ:
   ```sql
   DROP SCHEMA public CASCADE;
   CREATE SCHEMA public;
   GRANT ALL ON SCHEMA public TO gacms;   -- أو postgres حسب المستخدم
   GRANT ALL ON SCHEMA public TO public;
   ```
2. **تشغيل الترحيلات ثم البذار:**
   ```bash
   alembic upgrade head
   python scripts/seed.py
   ```
   بعد ذلك يجب أن يعمل السيرفر والـ seed بدون أخطاء (بشرط أن تكون جميع الـ ForeignKey في النماذج والترحيلات متوافقة).

---

## استكشاف الأخطاء

- **خطأ في الاتصال بقاعدة البيانات:**  
  تأكد أن PostgreSQL يعمل وأن `DATABASE_URL` في `.env` صحيح (المستخدم، كلمة المرور، المنفذ 5432، اسم القاعدة `gacms`).

- **خطأ عند إنشاء PDF (WeasyPrint):**  
  على Windows قد تحتاج تثبيت GTK3 Runtime كما ذُكر في الخطوة 4.

- **صفحة تسجيل الدخول لا تظهر أو 404:**  
  تأكد أنك تفتح `http://localhost:8000` (بدون مسار فرعي) وأن السيرفر يعمل بدون أخطاء في الطرفية.

- **نسيت كلمة المرور:**  
  أعد تشغيل `python scripts/seed.py` (سيُعيد إنشاء المستخدم الافتراضي إذا كان السكربت مصممًا لذلك).

---

بهذا تكون المنصة مُنصَّبة وتعمل على السيرفر المحلي فقط. لتشغيلها على شبكة أو سيرفر بعيد، غيّر `host` و`SCAN_BASE_URL` واقرأ قسم النشر في `README.md` إذا رغبت باستخدام Docker أو نشر إنتاجي.
