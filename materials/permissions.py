from rest_framework import permissions
from django.contrib.auth.models import Group


class IsModerator(permissions.BasePermission):
    """Проверка, является ли пользователь модератором"""

    def has_permission(self, request, view):
        # Проверяем, что пользователь авторизован
        if not request.user or not request.user.is_authenticated:
            return False

        # Проверяем, что пользователь не суперпользователь
        if request.user.is_superuser:
            return True

        # Проверяем, состоит ли пользователь в группе модераторов
        try:
            moderator_group = Group.objects.get(name='moderators')
            return request.user.groups.filter(id=moderator_group.id).exists()
        except Group.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        # Модераторы не могут удалять и создавать объекты
        if request.method in ['DELETE', 'POST']:
            # Проверяем, что пользователь не модератор
            if self.has_permission(request, view):
                return False
        return True


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Проверка, является ли пользователь владельцем объекта"""

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS) для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для изменения/удаления проверяем владельца
        # Проверяем, что пользователь авторизован
        if not request.user or not request.user.is_authenticated:
            return False

        # Проверяем, что пользователь является владельцем
        return obj.owner == request.user


class IsOwnerOrModeratorOrReadOnly(permissions.BasePermission):
    """Комбинированное разрешение: владелец или модератор"""

    def has_permission(self, request, view):
        # Для создания (POST) - только не модераторы
        if request.method == 'POST':
            # Если пользователь модератор - запрещаем создание
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

        # Модераторы не могут удалять
        if request.method == 'DELETE':
            try:
                moderator_group = Group.objects.get(name='moderators')
                if request.user.groups.filter(id=moderator_group.id).exists():
                    return False
            except Group.DoesNotExist:
                pass

        # Для изменения: либо владелец, либо суперпользователь
        return obj.owner == request.user or request.user.is_superuser