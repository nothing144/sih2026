# EV Battery Health & Digital Passport Backend

## What you have to do

### 1. Clone the project

```bash
git clone <GITHUB_REPOSITORY_URL>
put in sihbackend



2. Create virtual environment

python -m venv venv
venv\Scripts\activate

3. Install packages

pip install django djangorestframework djangorestframework-simplejwt django-cors-headers pandas joblib
pip install scikit-learn==1.6.1


4. Create your own PostgreSQL database

Create a new database for this project and configure its:

Database name
Username
Password
Host
Port

in Django settings.py or environment variables.


5. Run migrations

python manage.py makemigrations
python manage.py migrate

6. Create users

Create:
ev owner will only register..
EV Owner → role = EV_OWNER
Certified Tester → role = CERTIFIED_TESTER

-> python manage.py shell

from users.models import User

tester = User.objects.create_user(
    username="tester1",
    email="tester@ev.com",
    password="Tester@12345",
    first_name="Certified",
    last_name="Tester",
    phone="9999999999",
    role="CERTIFIED_TESTER",
    is_staff=True,
    is_superuser=True,
    is_active=True
)

print(tester)



7. Start backend
python manage.py runserver


Important

Use the API responses in the frontend.
Do not hardcode ML results.
Do not access the .pkl model from the frontend.
Use JWT access tokens for protected APIs.
Configure CORS for the frontend URL.
For deployment, create and configure your own production database.
Do not commit passwords or secret keys.

