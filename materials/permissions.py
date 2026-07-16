from rest_framework import permissions
from django.contrib.auth.models import Group


class IsModerator(permissions.BasePermission):
    """Проверка, является ли пользователь модератором"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        try:
            moderator_group = Group.objects.get(name='moderators')
            return request.user.groups.filter(id=moderator_group.id).exists()
        except Group.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        # Модераторы не могут удалять и создавать объекты
        if request.method in ['DELETE', 'POST']:
            return False
        return True


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Проверка, является ли пользователь владельцем объекта"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        return obj.owner == request.user


class IsOwnerOrModeratorOrReadOnly(permissions.BasePermission):
    """Комбинированное разрешение: владелец или модератор"""

    def has_permission(self, request, view):
        # Для создания (POST) - только не модераторы
        if request.method == 'POST':
            try:
                moderator_group = Group.objects.get(name='moderators')
                if request.user.groups.filter(id=moderator_group.id).exists():
                    return False
            except Group.DoesNotExist:
                pass
        return True

    def has_object_permission(self, request, view, obj):
        # Безопасные методы - доступны всем авторизованным
        if request.method in permissions.SAFE_METHODS:
            return True

        # Проверяем, является ли пользователь модератором
        is_moderator = False
        try:
            moderator_group = Group.objects.get(name='moderators')
            is_moderator = request.user.groups.filter(id=moderator_group.id).exists()
        except Group.DoesNotExist:
            pass

        # Модераторы не могут удалять
        if request.method == 'DELETE' and is_moderator:
            return False

        # Модераторы могут обновлять (PUT, PATCH)
        if request.method in ['PUT', 'PATCH'] and is_moderator:
            return True

        # Для изменения: владелец или суперпользователь
        return obj.owner == request.user or request.user.is_superuser