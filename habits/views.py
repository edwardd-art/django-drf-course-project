from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Habit
from .serializers import HabitSerializer
from .permissions import IsOwnerOrReadOnly, IsOwner

class HabitPagination(PageNumberPagination):
    """
    Пагинация для привычек (5 шт на страницу)
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

class HabitViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления привычками
    """
    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_pleasant', 'is_public', 'periodicity']
    ordering_fields = ['time', 'created_at']
    ordering = ['time']

    def get_queryset(self):
        """
        Получение списка привычек:
        - Все свои привычки
        - Публичные привычки других пользователей
        """
        user = self.request.user
        if self.action == 'list':
            # Свои привычки + публичные чужие
            return Habit.objects.filter(
                models.Q(user=user) | models.Q(is_public=True)
            ).distinct()
        return Habit.objects.filter(user=user)

    def get_permissions(self):
        """
        Права доступа
        """
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwner()]
        else:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_create(self, serializer):
        """
        При создании привычки автоматически добавляем пользователя
        """
        serializer.save(user=self.request.user)

