import re
from rest_framework.exceptions import ValidationError


def validate_youtube_url(value):
    """
    Валидатор для проверки, что ссылка ведет на youtube.com
    """
    if not value:
        return value

    # Проверяем, что ссылка содержит youtube.com или youtu.be
    youtube_patterns = [
        r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/',
        r'(https?://)?(www\.)?(m\.youtube\.com)/',
        r'(https?://)?(www\.)?(youtube\.googleapis\.com)/',
    ]

    is_valid = False
    for pattern in youtube_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            is_valid = True
            break

    if not is_valid:
        raise ValidationError(
            'Разрешены только ссылки на видео с YouTube (youtube.com или youtu.be)'
        )

    return value


class YouTubeURLValidator:
    """
    Класс-валидатор для проверки ссылок YouTube
    """

    def __init__(self, field='video_url'):
        self.field = field

    def __call__(self, attrs):
        """
        Валидация для сериализатора на уровне объекта
        """
        value = attrs.get(self.field)
        if not value:
            return attrs

        # Проверяем ссылку
        youtube_patterns = [
            r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/',
            r'(https?://)?(www\.)?(m\.youtube\.com)/',
        ]

        is_valid = False
        for pattern in youtube_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                is_valid = True
                break

        if not is_valid:
            raise ValidationError(
                {self.field: 'Разрешены только ссылки на видео с YouTube (youtube.com или youtu.be)'}
            )

        return attrs