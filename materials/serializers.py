from rest_framework import serializers
from .models import Course, Lesson
from .validators import validate_youtube_url, YouTubeURLValidator


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'name', 'description', 'preview', 'video_url', 'course', 'owner']
        read_only_fields = ['owner']
        validators = [
            YouTubeURLValidator(field='video_url')  # Валидация на уровне объекта
        ]

    def validate_video_url(self, value):
        """
        Валидация на уровне поля
        """
        return validate_youtube_url(value)


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True, source='lessons.all')
    is_subscribed = serializers.SerializerMethodField()  # Для задания 2

    class Meta:
        model = Course
        fields = ['id', 'name', 'preview', 'description', 'owner', 'lessons_count', 'lessons', 'is_subscribed']
        read_only_fields = ['owner']

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """
        Проверка подписки текущего пользователя на курс
        """
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return False

        # Проверяем, есть ли подписка у пользователя на этот курс
        return obj.subscribers.filter(user=request.user).exists()