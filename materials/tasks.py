from celery import shared_task
from users.models import User, Subscription
from .models import Course, Lesson


@shared_task
def send_course_update_notifications(course_id, lesson_id):
    """
    Отправка уведомлений об обновлении курса
    """
    try:
        course = Course.objects.get(id=course_id)
        lesson = Lesson.objects.get(id=lesson_id)

        # Находим всех подписчиков курса
        subscriptions = Subscription.objects.filter(course=course)

        for subscription in subscriptions:
            user = subscription.user
            # Здесь можно отправить уведомление пользователю
            print(f"Уведомление для {user.email}: "
                  f"В курсе '{course.name}' добавлен новый урок '{lesson.name}'")

        return f"Отправлено {subscriptions.count()} уведомлений"
    except Course.DoesNotExist:
        return f"Курс с id {course_id} не найден"
    except Lesson.DoesNotExist:
        return f"Урок с id {lesson_id} не найден"