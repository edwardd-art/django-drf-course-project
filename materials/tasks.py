from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from users.models import User, Subscription
from materials.models import Course, Lesson
from django.conf import settings
from django.db.models import Q


@shared_task
def send_course_update_notification(course_id, lesson_id, user_id):
    """
    Задача для отправки уведомления об обновлении курса
    Задание 2: Рассылка писем пользователям об обновлении материалов курса
    """
    try:
        course = Course.objects.get(id=course_id)
        lesson = Lesson.objects.get(id=lesson_id)
        user = User.objects.get(id=user_id)

        # Формируем письмо
        subject = f"Обновление курса: {course.name}"
        message = f"""
        Здравствуйте, {user.first_name or user.email}!

        В курсе "{course.name}" появился новый урок или обновление.

        Название урока: {lesson.name}
        Описание: {lesson.description}

        Ссылка на видео: {lesson.video_url or "не указана"}

        С уважением,
        Команда LMS
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return f"Уведомление отправлено пользователю {user.email}"
    except Exception as e:
        return f"Ошибка отправки уведомления: {str(e)}"


@shared_task
def send_course_update_notifications(course_id, lesson_id):
    """
    Отправка уведомлений всем подписчикам курса
    Задание 2 + Дополнительное задание: Проверка на 4 часа
    """
    try:
        course = Course.objects.get(id=course_id)
        lesson = Lesson.objects.get(id=lesson_id)

        # Дополнительное задание: Проверка, что курс не обновлялся более 4 часов
        # Проверяем время последнего обновления курса
        if course.updated_at:
            time_since_update = timezone.now() - course.updated_at
            if time_since_update < timedelta(hours=4):
                return f"Курс {course.name} обновлялся менее 4 часов назад. Уведомления не отправлены."

        # Получаем всех подписчиков курса
        subscribers = Subscription.objects.filter(
            course=course
        ).select_related('user')

        if not subscribers.exists():
            return f"Нет подписчиков у курса {course.name}"

        # Отправляем уведомления всем подписчикам (батчем, не по одному)
        user_ids = [sub.user.id for sub in subscribers]

        # Используем group для параллельной отправки
        from celery import group
        tasks = group(
            send_course_update_notification.s(course_id, lesson_id, user_id)
            for user_id in user_ids
        )
        result = tasks.apply_async()

        return f"Уведомления отправлены {len(user_ids)} подписчикам курса {course.name}"
    except Exception as e:
        return f"Ошибка отправки уведомлений: {str(e)}"


@shared_task
def check_inactive_users():
    """
    Задание 3: Проверка неактивных пользователей
    Блокировка пользователей, которые не заходили более месяца
    """
    try:
        # Вычисляем дату месяц назад
        one_month_ago = timezone.now() - timedelta(days=30)

        # Находим пользователей, которые не заходили более месяца
        inactive_users = User.objects.filter(
            Q(last_login__lt=one_month_ago) | Q(last_login__isnull=True),
            is_active=True,
            is_superuser=False,  # Не блокируем суперпользователей
            is_staff=False  # Не блокируем персонал
        )

        count = inactive_users.count()

        if count > 0:
            # Блокируем пользователей (батчем, не по одному)
            updated = inactive_users.update(is_active=False)

            # Логируем результат
            for user in inactive_users:
                print(f"Пользователь {user.email} заблокирован за неактивность")

            return f"Заблокировано {updated} неактивных пользователей"
        else:
            return "Неактивных пользователей не найдено"
    except Exception as e:
        return f"Ошибка проверки неактивных пользователей: {str(e)}"