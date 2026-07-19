from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from datetime import timedelta


class Habit(models.Model):
    """
    Модель привычки
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='habits',
        verbose_name='Пользователь'
    )
    place = models.CharField(
        max_length=255,
        verbose_name='Место выполнения'
    )
    time = models.TimeField(
        verbose_name='Время выполнения'
    )
    action = models.CharField(
        max_length=255,
        verbose_name='Действие'
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name='Признак приятной привычки'
    )
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Связанная привычка',
        help_text='Указывается для полезных привычек'
    )
    periodicity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        verbose_name='Периодичность (дни)'
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Вознаграждение'
    )
    execution_time = models.PositiveIntegerField(
        validators=[MaxValueValidator(120)],
        verbose_name='Время на выполнение (сек)'
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name='Признак публичности'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.action}"

    def clean(self):
        """
        Валидация модели
        """
        from django.core.exceptions import ValidationError

        # 1. Нельзя одновременно заполнять reward и related_habit
        if self.reward and self.related_habit:
            raise ValidationError(
                "Нельзя одновременно указывать вознаграждение и связанную привычку"
            )

        # 2. У приятной привычки не может быть вознаграждения или связанной привычки
        if self.is_pleasant and (self.reward or self.related_habit):
            raise ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки"
            )

        # 3. В связанные привычки могут попадать только привычки с признаком приятной привычки
        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError(
                "Связанная привычка должна быть приятной"
            )

        # 4. Нельзя выполнять привычку реже, чем 1 раз в 7 дней
        if self.periodicity > 7:
            raise ValidationError(
                "Периодичность не может быть больше 7 дней"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

