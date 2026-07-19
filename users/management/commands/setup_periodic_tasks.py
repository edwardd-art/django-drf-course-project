from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from django.utils import timezone
import json


class Command(BaseCommand):
    help = 'Setup periodic tasks for celery-beat'

    def handle(self, *args, **options):
        self.stdout.write('Setting up periodic tasks...')

        # Задание 3: Создаем задачу для проверки неактивных пользователей
        # Ежедневно в 00:00
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='0',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
            timezone=timezone.get_current_timezone()
        )

        task, created = PeriodicTask.objects.get_or_create(
            name='Check inactive users every day',
            defaults={
                'task': 'materials.tasks.check_inactive_users',
                'crontab': schedule,
                'enabled': True,
                'args': json.dumps([]),
                'kwargs': json.dumps({}),
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created task: {task.name}'))
        else:
            self.stdout.write(f'Task already exists: {task.name}')

        # Дополнительная задача: отправка уведомлений о курсах
        # Можно добавить по необходимости

        self.stdout.write(self.style.SUCCESS('Periodic tasks setup completed!'))