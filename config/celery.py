import os
from celery import Celery
from django.conf import settings

# Устанавливаем модуль настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Создаем экземпляр Celery
app = Celery('config')

# Загружаем настройки из Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи в приложениях
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    """
    Отладочная задача для проверки работы Celery
    """
    print(f'Request: {self.request!r}')