# EV Battery Health & Digital Passport — Backend

Django 6.1 + Django REST Framework backend for the EV Battery Platform (SOAIDEATHON-S13).
Provides JWT authentication, EV-owner battery management, BMS CSV upload, ML-based
State-of-Health analysis (scikit-learn), second-life digital passports, and a
tester verification workflow.

- Database: PostgreSQL (Supabase or local)
- Auth: SimpleJWT (access + refresh tokens)
- ML model: `ml_models/soh_model_original.pkl` (loaded server-side only)

---

## Project structure

```
sih2026/
├── manage.py
├── requirements.txt
├── config/            # settings, urls, wsgi
├── users/             # custom User model (EV_OWNER / CERTIFIED_TESTER), auth endpoints
├── batteries/         # Battery + BMSData models & endpoints
├── analysis/          # ML analysis (BatteryAnalysis) + model pipeline
├── passport/          # BatteryPassport + verification/public-verify endpoints
├── ml_models/         # trained SOH model (tracked in git)
└── media/             # uploaded BMS CSVs (gitignored, not in repo)
```

---

## 1. Clone

```bash
git clone <GITHUB_REPOSITORY_URL>
cd sih2026
```

## 2. Virtual environment (Python 3.12)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

Includes: Django, DRF, SimpleJWT, django-cors-headers, psycopg2-binary,
python-dotenv, gunicorn, whitenoise, pandas, joblib, scikit-learn.

## 4. Configure environment variables

Create a `.env` file in the `sih2026/` root (it is gitignored — never commit it).

### Local development (local PostgreSQL)

```env
DEBUG=True
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<your_local_db_name>
DB_USER=<your_local_db_user>
DB_PASSWORD=<your_local_db_password>
DB_HOST=localhost
DB_PORT=5432
```

### Supabase PostgreSQL

```env
DEBUG=False
SECRET_KEY=<a long random secret>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=<supabase_db_password>
DB_HOST=db.<project-ref>.supabase.co
DB_PORT=5432
DB_SSLMODE=require
ALLOWED_HOSTS=<your-hostname>
CORS_ALLOWED_ORIGINS=<frontend-url, e.g. https://your-app.netlify.app>
```

Notes:
- `DEBUG` defaults to `False`. Keep it `True` only for local development.
- `SECRET_KEY` is **required** when `DEBUG=False` (the server refuses to start without it).
- `ALLOWED_HOSTS` / `CORS_ALLOWED_ORIGINS` are comma-separated lists.

## 5. Apply migrations

Migrations are committed to the repository — do **not** run `makemigrations`.

```bash
python manage.py migrate
```

## 6. Create users

EV owners self-register via the frontend (`POST /api/auth/register/`).
Create a certified tester manually:

```bash
python manage.py shell
```

```python
from users.models import User

tester = User.objects.create_user(
    username="tester1",
    email="tester@ev.com",
    password="<choose-a-strong-password>",   # example — change it
    first_name="Certified",
    last_name="Tester",
    phone="9999999999",
    role="CERTIFIED_TESTER",
    is_staff=True,
    is_superuser=True,
    is_active=True,
)
print(tester)
```

## 7. Run (development)

```bash
python manage.py runserver
```

API base URL: `http://127.0.0.1:8000/api/`

---

## API overview

| Area | Endpoints |
|---|---|
| Auth | `POST /api/auth/register/`, `POST /api/auth/owner/login/`, `POST /api/auth/tester/login/`, `POST /api/auth/token/refresh/` |
| Profiles | `GET /api/auth/owner/profile/`, `GET /api/auth/tester/profile/` |
| Batteries | `GET /api/batteries/list/`, `POST /api/batteries/create/`, `GET /api/batteries/view/<pk>/`, `PUT /api/batteries/update/<pk>/`, `DELETE /api/batteries/delete/<pk>/` |
| BMS data | `POST /api/batteries/bms/create/` (multipart: `battery`, `file`), `GET /api/batteries/bms/list/` |
| ML analysis | `POST /api/analysis/create/` (`{"bms_data": <pk>}`), `GET /api/analysis/list/` |
| Passports (owner) | `POST /api/passport/create/`, `GET /api/passport/list/`, `GET /api/passport/view/<pk>/` |
| Passports (tester) | `GET /api/passport/verification/pending/`, `GET /api/passport/decisions/?status=`, `PUT /api/passport/verify/<pk>/`, `PUT /api/passport/reject/<pk>/` |
| Public | `GET /api/passport/public/verify/<passport_id>/` (no auth) |

All endpoints except registration, login, token refresh and public verify
require a JWT: `Authorization: Bearer <access_token>`.

---

## Production deployment (Render)

- **Root Directory:** `sih2026`
- **Build Command:**
  ```bash
  pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
  ```
- **Start Command:**
  ```bash
  gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2
  ```
- **Environment variables:** the Supabase block from step 4, plus `SECRET_KEY`
  (required), `ALLOWED_HOSTS` (Render hostname), `CORS_ALLOWED_ORIGINS`
  (Netlify URL). Leave `DEBUG` unset.

Static files are served by WhiteNoise. Uploaded BMS CSVs currently use Render's
ephemeral disk — they are lost on redeploy and ML analysis for old rows requires
the file to exist; cloud storage (e.g. Supabase Storage) is a planned follow-up.

---

## Important

- Use real API responses in the frontend. Do not hardcode ML results.
- Never access the `.pkl` model from the frontend.
- Never commit `.env`, passwords, or secret keys.
- Rotate any credential that has ever been exposed.
