from rest_framework.permissions import (
    BasePermission, IsAuthenticatedOrReadOnly, SAFE_METHODS
)

from users.models import UserRole


class IsAdmin(BasePermission):
    def get_permission(self, request):
        return request.user.role == UserRole.ADMIN or request.user.is_superuser

    def has_permission(self, request, view):
        return self.get_permission(request)

    def has_object_permission(self, request, view, obj):
        return self.get_permission(request)


class IsAdminOrReadOnly(IsAdmin):
    def get_permission(self, request):
        return (
            request.method in SAFE_METHODS or super().get_permission(request)
        )


class IsAdminOrIsModeratorOrIsAuthorOrReadOnly(
    IsAuthenticatedOrReadOnly, IsAdminOrReadOnly
):
    def has_object_permission(self, request, view, obj):
        return (
            self.get_permission(request)
            or obj.author == request.user
            or request.user.role == UserRole.MODERATOR
        )
