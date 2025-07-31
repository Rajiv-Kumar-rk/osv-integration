# 📦 NPM Package Vulnerability Scanner

A standalone Django-based API application that scans a given `package.json` file for known vulnerabilities using OSV.dev and sends results to Slack.

## 🚀 Features

- Upload a `package.json` file via REST API.
- Get stats of last scans.
- Create the scheduler via REST API.
- Manual scan trigger via REST API.
- Scans NPM package dependencies for known vulnerabilities using OSV.dev.
- Sends formatted results to a Slack channel/user.
- Periodic scans with Celery and Celery Beat.
- Stores results in PostgreSQL database.

---

## 🛠 Tech Stack

- Django & Django REST Framework
- Celery & django-celery-beat
- Djnago Default DB - SQLite 
- Redis (for Celery broker)
- Slack API
- OSV API

---

## 📁 Project Structure
i. There are 'packagejsonscanner' and 'scanner' apps which includes their respective-
    a. packagejsonscanner - settings.py, celery.py, urls.py, wsgi.py, asgi.py
    b. scanner - admin.py, apps.py, models.py, tasks.py, tests.py, urls.py, utils.py, views.py
ii. outer files:
    a. .env
    b. manage.py
    c. requirements.txt
    d. .sample-env
    e. .gitignore

## ⚙️ Setup Instructions
1. create folder backend
2. change directory to /backend
3. clone the repository
git clone https://github.com/yourusername/package-scanner-app.git

4.create virtual environment: 
    python -m venv venv

5. activate the above created virtual environment:
    venv\Scripts\activate (for windows)

6. install all dependecies:
    pip install -r requirements.txt

7. make migrations for db:
    i. python manage.py makemigrations
    ii. python manage.py migrate


8.Run the below services seaparately:
    i. python manage.py runserver
    ii. up redis server:(using docker image)
        a. docker run --name redis-server -p 6379:6379 -d redis
        b. docker exec -it redis-server redis-cli ping  (check the connection)
    iii. up beat service: 
        celery -A packagejsonscanner beat --loglevel=info
    iv. up worker service:
        celery -A packagejsonscanner worker -l info -P solo
