from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор для привычек
    """
    user = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Habit
        fields = [
            'id', 'user', 'place', 'time', 'action',
            'is_pleasant', 'related_habit', 'periodicity',
            'reward', 'execution_time', 'is_public',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """
        Валидация данных
        """
        # Проверка на одновременное заполнение reward и related_habit
        if data.get('reward') and data.get('related_habit'):
            raise serializers.ValidationError(
                "Нельзя одновременно указывать вознаграждение и связанную привычку"
            )

        # Проверка для приятной привычки
        if data.get('is_pleasant') and (data.get('reward') or data.get('related_habit')):
            raise serializers.ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки"
            )

        # Проверка связанной привычки
        if data.get('related_habit'):
            related = data.get('related_habit')
            if not related.is_pleasant:
                raise serializers.ValidationError(
                    "Связанная привычка должна быть приятной"
                )

        return data