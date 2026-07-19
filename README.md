# Habit Tracker - Приложение для управления привычками

## 📚 О проекте

Habit Tracker - это веб-приложение для отслеживания и управления привычками. Проект построен на Django REST Framework и включает:

- 📝 Создание и управление привычками
- 🔔 Автоматические напоминания через Telegram
- 📊 Пагинация и фильтрация
- 🔐 JWT-авторизация
- 📖 Документация API (Swagger/ReDoc)

## 🚀 Быстрый старт

### Установка

```bash
# Клонируем репозиторий
git clone https://github.com/edwardd-art/django-drf-course-project.git
cd django-drf-course-project

# Создаем виртуальное окружение
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate     # для Windows

# Устанавливаем зависимости
pip install -r requirements.txt

# Применяем миграции
python manage.py migrate

# Создаем суперпользователя
python manage.py createsuperuser

# Запускаем сервер
python manage.py runserver