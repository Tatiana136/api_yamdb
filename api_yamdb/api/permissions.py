from rest_framework import permissions


class IsAuthorPermission(permissions.BasePermission):
    pass


class IsAdminPermission(permissions.BasePermission):
    pass


class IsReadOnlyPermission(permissions.BasePermission):
    pass