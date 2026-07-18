from celery import shared_task
from django.utils import timezone
from .models import Habit


@shared_task
def send_habit_reminders():
    """
    Отправка напоминаний о привычках через Telegram
    """
    now = timezone.now()
    current_time = now.time()

    # Находим привычки, которые нужно выполнить сейчас
    habits = Habit.objects.filter(
        time__hour=current_time.hour,
        time__minute=current_time.minute
    )

    for habit in habits:
        # Проверяем, что сегодня нужно выполнять привычку
        days_since_creation = (now.date() - habit.created_at.date()).days
        if days_since_creation % habit.periodicity == 0:
            # Здесь будет отправка в Telegram
            print(f"Напоминание: {habit.action} в {habit.time} в {habit.place}")

    return f"Обработано {habits.count()} привычек"