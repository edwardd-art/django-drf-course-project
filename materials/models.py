from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    preview = models.ImageField(upload_to='courses/', blank=True, null=True, verbose_name='Превью')
    description = models.TextField(blank=True, verbose_name='Описание')
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name='Владелец',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['id']  # Добавляем ordering для пагинации

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name='Курс')
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    preview = models.ImageField(upload_to='lessons/', blank=True, null=True, verbose_name='Превью')
    video_url = models.URLField(blank=True, verbose_name='Ссылка на видео')
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Владелец',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['id']  # Добавляем ordering для пагинации

    def __str__(self):
        return self.name