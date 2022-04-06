from rest_framework.permissions import (
    BasePermission, IsAuthenticatedOrReadOnly, SAFE_METHODS
)

from users.models import UserRole


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == UserRole.ADMIN or request.user.is_superuser


class IsAdminOrReadOnly(IsAdmin):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or super().has_permission(request, view)
        )


class IsAdminOrIsModeratorOrIsAuthorOrReadOnly(
    IsAuthenticatedOrReadOnly, IsAdminOrReadOnly
):
    def has_object_permission(self, request, view, obj):
        return (
            IsAdminOrReadOnly.has_permission(self, request, view)
            or obj.author == request.user
            or request.user.role == UserRole.MODERATOR
        )
