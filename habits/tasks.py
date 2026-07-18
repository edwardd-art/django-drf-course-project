import requests
from celery import shared_task
from django.conf import settings
from datetime import datetime, timedelta
from .models import Habit


@shared_task
def send_habit_reminders():
    """
    Отправка напоминаний о привычках через Telegram
    """
    now = datetime.now()
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
            send_telegram_notification.delay(habit.id)


@shared_task
def send_telegram_notification(habit_id):
    """
    Отправка уведомления в Telegram
    """
    try:
        habit = Habit.objects.get(id=habit_id)
        user = habit.user

        # Проверяем, есть ли у пользователя Telegram ID
        if not hasattr(user, 'telegram_id') or not user.telegram_id:
            return

        # Формируем сообщение
        message = f"""
Привет! Пора выполнить привычку:
📍 Место: {habit.place}
⏰ Время: {habit.time}
🎯 Действие: {habit.action}
⏱ Время на выполнение: {habit.execution_time} сек
{'🎁 Вознаграждение: ' + habit.reward if habit.reward else ''}
{'🔗 Связанная привычка: ' + habit.related_habit.action if habit.related_habit else ''}
        """

        # Отправляем сообщение в Telegram
        bot_token = settings.TELEGRAM_BOT_TOKEN
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': user.telegram_id,
            'text': message
        }
        requests.post(url, data=data)

    except Habit.DoesNotExist:
        pass
    except Exception as e:
        print(f"Error sending notification: {e}")