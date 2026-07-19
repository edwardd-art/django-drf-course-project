from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Проверка прав доступа: только владелец может изменять
    """
    def has_object_permission(self, request, view, obj):
        # Публичные привычки могут просматривать все
        if request.method in permissions.SAFE_METHODS and obj.is_public:
            return True
        return obj.user == request.user

class IsOwner(permissions.BasePermission):
    """
    Только владелец может изменять
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user