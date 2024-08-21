from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit or delete books.
    """

    def has_permission(self, request, view):

        return (request.method in permissions.SAFE_METHODS) or (
            request.user and request.user.is_staff
        )
