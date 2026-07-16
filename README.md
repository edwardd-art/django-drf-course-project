# LMS System - Django REST Framework

Система управления курсами и уроками с расширенным функционалом платежей, подписок и пагинацией.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14.0-red.svg)](https://www.django-rest-framework.org/)

## 📋 Описание проекта

Проект представляет собой REST API для образовательной платформы (LMS). Реализована полная CRUD функциональность для курсов, уроков, платежей и подписок.

### Основные возможности:
- 🔐 Кастомная модель пользователя с авторизацией по email
- 📚 Управление курсами и уроками с валидацией YouTube ссылок
- 💳 Система платежей с фильтрацией и сортировкой
- 🔔 Подписки на обновления курсов
- 📊 Автоматический подсчет количества уроков в курсе
- 👤 Профиль пользователя с историей платежей
- 🎯 Права доступа для разных групп пользователей
- 📄 Пагинация для курсов и уроков
- 🧪 Полное покрытие тестами

## 🛠 Технологии

- Python 3.10+
- Django 4.2.7
- Django REST Framework 3.14.0
- Django REST Framework SimpleJWT 5.3.0
- Django Filter 23.5
- Pillow 10.1.0
- Coverage 7.3.2
- SQLite3 (по умолчанию)

## 📦 Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/ваш_username/django-drf-course-project.git
cd django-drf-course-project