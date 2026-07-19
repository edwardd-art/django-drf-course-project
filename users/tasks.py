from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_welcome_email(user_id):
    """
    Пример дополнительной задачи: отправка приветственного письма
    """
    from users.models import User
    try:
        user = User.objects.get(id=user_id)
        send_mail(
            subject='Добро пожаловать в LMS!',
            message=f'Здравствуйте, {user.first_name or user.email}!\n\n'
                    f'Вы успешно зарегистрировались в нашей LMS системе.\n'
                    f'Теперь вы можете просматривать курсы и уроки.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return f"Приветственное письмо отправлено {user.email}"
    except Exception as e:
        return f"Ошибка отправки письма: {str(e)}"