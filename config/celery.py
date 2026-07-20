import os
from celery import Celery
from celery.schedules import crontab

# Устанавливаем переменную окружения для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Создаем экземпляр Celery
app = Celery('config')

# Загружаем настройки из Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи в приложениях
app.autodiscover_tasks()

# Настройка расписания
app.conf.beat_schedule = {
    'send_habit_reminders': {
        'task': 'habits.tasks.send_habit_reminders',
        'schedule': crontab(minute='*/1'),  # Каждую минуту
    },
    'send_course_update_notifications': {
        'task': 'materials.tasks.send_course_update_notifications',
        'schedule': crontab(minute='*/5'),  # Каждые 5 минут
    },
}

# Настройки Celery
app.conf.timezone = 'UTC'
app.conf.enable_utc = True
app.conf.broker_connection_retry_on_startup = True