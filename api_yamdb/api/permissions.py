from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Права администратра."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.is_admin


class IsSuperUserOrIsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_superuser
                 or request.user.is_staff
                 or request.user.is_admin)
        )


class ReadOnly(permissions.BasePermission):
    """Разрешает анонимному пользователю только безопасные запросы."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsSuperUserIsAdminIsModeratorIsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.is_superuser
                 or request.user.is_staff
                 or request.user.is_admin
                 or request.user.is_moderator
                 or request.user == obj.author)
        )
