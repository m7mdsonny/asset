# GACMS – Group Asset Custody Management System

Production-ready **internal SaaS** for managing physical IT assets (laptops, mobiles, tablets, equipment) with **QR codes**, **multi-group/company/branch**, **role-based access**, **legal PDF handover documents**, and **audit mode**.

## Features

- **Multi-tenancy**: Group → Companies → Branches → Employees & Assets
- **Roles**: Group Admin, Company Admin, Branch Manager, Auditor
- **Asset lifecycle**: Create, assign, transfer, return, maintenance, lost, retire
- **QR codes**: Tokenized scan URL per asset; public scan page (summary or “REPORTED LOST” alert)
- **PDF handover documents**: Jinja2 + WeasyPrint, company logo/colors/legal text
- **Audit mode**: Start session, scan QR codes, compare expected vs scanned, export report
- **Activity logging**: Full audit trail (create/update/delete/restore on groups, assets, documents); IP logging; viewer at `/api/v1/logs`
- **Responsibility control**: Block employee resignation if they have assigned assets
- **Dashboard**: Group/company analytics (totals, by branch/department, warranty, depreciation)
- **Bulk import**: Excel (Employees + Assets sheets)
- **Depreciation**: Script for yearly book value recalculation
- **Soft delete**: Groups, Companies, Branches, Users, Employees, Assets support soft delete + restore (`include_deleted` query param on list endpoints; `POST /.../restore` to restore)
- **Global search**: Search across assets, employees, companies, branches
- **Signed copy**: Upload signed PDF copy for handover documents

## Tech stack

- **Backend**: Python 3.11+, FastAPI, PostgreSQL, SQLAlchemy (async), Alembic, JWT, Pydantic v2
- **Frontend**: واجهة عربية احترافية — HTML + Tailwind CSS + Alpine.js، خط **الإسكندرية** (Google Fonts)، RTL، لوحة تحكم، قوائم وجداول، نوافذ منبثقة
- **PDF**: Jinja2, WeasyPrint
- **QR**: `qrcode` library, UUID-based scan URL؛ صفحة المسح العامة بالعربية وخط الإسكندرية
- **Deployment**: Docker, docker-compose, .env config

## تنصيب على سيرفر محلي (خطوة بخطوة)

لدليل تفصيلي لتنصيب المنصة على جهازك المحلي فقط (بدون Docker)، راجع **[INSTALL.md](INSTALL.md)**.

---

## Quick start

### 1. Clone and configure

```bash
cd Asset
cp .env.example .env
# Edit .env: set SECRET_KEY (min 32 chars), SCAN_BASE_URL, etc.
```

### 2. Run with Docker

```bash
docker-compose up -d
```

- **الواجهة الأمامية (عربي)**: http://localhost:8000 — واجهة احترافية بالكامل بالعربية وخط الإسكندرية (تسجيل دخول، لوحة تحكم، مجموعات، شركات، فروع، موظفون، أصول، تنبيهات، سجل النشاط).
- **API**: http://localhost:8000/api/v1  
- **Docs**: http://localhost:8000/docs  
- Migrations run on startup.

### 3. Seed default data (optional)

```bash
# With venv and deps installed locally, or run inside container:
docker-compose exec app python scripts/seed.py
```

Default login: **admin@gacms.example.com** / **Admin123!**

### 4. Run without Docker (local dev)

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
# Set DATABASE_URL to your PostgreSQL (e.g. postgresql+asyncpg://user:pass@localhost:5432/gacms)
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API overview

| Area | Prefix | Description |
|------|--------|-------------|
| Auth | `POST /api/v1/auth/login` | JWT login |
| Auth | `GET /api/v1/auth/me` | Current user |
| Users | `/api/v1/users` | CRUD users |
| Groups | `/api/v1/groups` | CRUD groups |
| Companies | `/api/v1/companies` | CRUD companies |
| Branches | `/api/v1/branches` | CRUD branches |
| Employees | `/api/v1/employees` | CRUD employees |
| Assets | `/api/v1/assets` | CRUD, assign, transfer, return, lost, maintenance, retire |
| Assets | `GET /api/v1/assets/{id}/timeline` | Lifecycle history |
| Documents | `POST /api/v1/documents/handover` | Generate handover PDF |
| Audits | `/api/v1/audits` | Start/end session, record scan, get report |
| Logs | `/api/v1/logs` | Activity log viewer |
| Dashboard | `/api/v1/dashboard/group/{id}` | Group analytics |
| Dashboard | `/api/v1/dashboard/company/{id}` | Company analytics |
| Alerts | `GET /api/v1/alerts?company_id=` | Maintenance, warranty expiring, lost assets |
| Documents | `GET /api/v1/documents?asset_id=` | List documents for an asset |
| Audits | `GET /api/v1/audits/{id}/report/pdf` | Export audit report as PDF |
| Bulk | `POST /api/v1/bulk-import/upload` | Excel import (Employees, Assets sheets) |
| Search | `GET /api/v1/search?q=` | Global search (assets, employees, companies, branches) |
| Groups | `POST /api/v1/groups/{id}/restore` | Restore soft-deleted group |
| Companies | `POST /api/v1/companies/{id}/restore` | Restore soft-deleted company |
| Branches | `POST /api/v1/branches/{id}/restore` | Restore soft-deleted branch |
| Users | `DELETE /api/v1/users/{id}` (soft), `POST .../restore` | Soft delete / restore user |
| Employees | `POST /api/v1/employees/{id}/restore` | Restore soft-deleted employee |
| Assets | `DELETE /api/v1/assets/{id}` (soft), `POST .../restore` | Soft delete / restore asset |
| Documents | `POST /api/v1/documents/{id}/signed-copy` | Upload signed PDF copy |
| **Public** | `GET /scan/{asset_id}` | QR scan – JSON summary |
| **Public** | `GET /scan/{asset_id}/page` | QR scan – HTML (or LOST alert) |

## QR and scan

- Each asset has a scan URL: `{SCAN_BASE_URL}/scan/{asset_uuid}`.
- Generate QR image via `app.services.qr_service.generate_qr_image(asset_id)` (used in PDFs).
- Public endpoints **do not require auth**; they return limited data (type, brand, model, status, company name, assigned employee name). If status is **lost**, the HTML page shows a red “THIS DEVICE IS REPORTED LOST” screen.

## Depreciation cron

Run yearly (e.g. via cron or scheduler):

```bash
python scripts/depreciation_cron.py
```

This reduces `current_book_value` by `depreciation_rate`% for active assets that have both fields set.

## Project structure

```
app/
├── core/           # config, database, security, dependencies, exceptions
├── models/         # SQLAlchemy models
├── schemas/        # Pydantic common schemas
├── services/       # QR, PDF
├── modules/
│   ├── auth/       # login, me
│   ├── users/      # user CRUD
│   ├── groups/
│   ├── companies/
│   ├── branches/
│   ├── employees/
│   ├── assets/     # lifecycle + timeline
│   ├── scan/       # public QR scan
│   ├── documents/  # handover PDF
│   ├── audits/
│   ├── logs/       # activity log
│   ├── dashboard/
│   └── bulk_import/
├── templates/      # Jinja2 (e.g. handover.html)
├── main.py
alembic/
scripts/            # seed.py, depreciation_cron.py
Dockerfile
docker-compose.yml
```

## Security

- JWT with role/company/branch in claims; RBAC enforced in services.
- Passwords hashed with bcrypt.
- Input validation via Pydantic; no business logic in routers.
- Activity log stores user, action, resource, IP.

## License

Internal use. Adjust as per your organization.
