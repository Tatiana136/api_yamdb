from rest_framework import permissions


class IsAuthenticatedWithRole(permissions.BasePermission):
    """
    Разрешает доступ только аутентифицированным пользователям с определенной ролью.
    """

    def __init__(self, role):
        self.role = role

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == self.role

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or (request.user and request.user.is_authenticated and request.user.role == self.role))


class IsAdmin(permissions.BasePermission):
    """Права администратра."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_admin
