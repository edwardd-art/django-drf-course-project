# 📚 LMS System - Habit Tracker

Система управления курсами, уроками и привычками с автоматическим деплоем через CI/CD.

## 📋 О проекте

Проект представляет собой REST API для образовательной платформы с интеграцией Telegram-бота для напоминаний о привычках.

### Основные возможности:
- 🔐 JWT-авторизация
- 📚 Управление курсами и уроками
- 📊 Управление привычками (Habit Tracker)
- 🔔 Telegram-напоминания через Celery
- 🐳 Полная контейнеризация (Docker)
- 🚀 CI/CD через GitHub Actions
- 📖 Документация API (Swagger/ReDoc)

## 🛠 Технологии

- Python 3.10+
- Django 4.2.7
- Django REST Framework 3.14.0
- PostgreSQL 15
- Redis 7
- Celery 5.3.6
- Docker & Docker Compose
- Nginx
- GitHub Actions (CI/CD)
- JWT-аутентификация

## 🚀 Быстрый старт

### Локальный запуск (без Docker)

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/edwardd-art/django-drf-course-project.git
cd django-drf-course-project

# 2. Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate     # для Windows

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Создайте файл .env из шаблона
cp .env.example .env

# 5. Примените миграции
python manage.py migrate

# 6. Создайте суперпользователя
python manage.py createsuperuser

# 7. Запустите сервер
python manage.py runserver