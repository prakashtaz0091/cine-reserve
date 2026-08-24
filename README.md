# Cine Reserve 🎬

Cine Reserve is a Django-based cinema ticket reservation system that allows users to browse movies and reserve cinema tickets.

## Tech Stack

* Python
* Django
* SQLite / Database configured in Django
* HTML, CSS, JavaScript
* Django Templates

## Project Structure

```text
cine-reserve/
├── config/
├── core/
├── manage.py
└── .gitignore
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/prakashtaz0091/cine-reserve.git
cd cine-reserve
```

### 2. Create a virtual environment

#### Linux / macOS

```bash
python3 -m venv venv
```

#### Windows

```bash
python -m venv venv
```

### 3. Activate the virtual environment

#### Linux / macOS

```bash
source venv/bin/activate
```

#### Windows

```bash
venv\Scripts\activate
```

For PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

### 4. Install dependencies

If `requirements.txt` is available:

```bash
pip install -r requirements.txt
```

Otherwise, install Django:

```bash
pip install django
```

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Create a superuser

To access the Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### 7. Run the development server

```bash
python manage.py runserver
```

Open the application in your browser:

```text
http://127.0.0.1:8000/
```

The Django admin panel is available at:

```text
http://127.0.0.1:8000/admin/
```

## Development Commands

Create migrations after changing models:

```bash
python manage.py makemigrations
```

Apply migrations:

```bash
python manage.py migrate
```

Run the development server:

```bash
python manage.py runserver
```

Create a Django superuser:

```bash
python manage.py createsuperuser
```

Run tests:

```bash
python manage.py test
```

Open the Django shell:

```bash
python manage.py shell
```

## Deactivate Virtual Environment

When you are finished working on the project:

```bash
deactivate
```

## Project

**Cine Reserve** — A cinema ticket reservation system built with Django.

Repository: https://github.com/prakashtaz0091/cine-reserve
