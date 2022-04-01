from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly, SAFE_METHODS
)


class IsAdmin(IsAuthenticated):
    def get_permission(self, request):
        return request.user.role == 'admin' or request.user.is_superuser

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and self.get_permission(request)
        )

    def has_object_permission(self, request, view, obj):
        return self.get_permission(request)


class IsModerator(IsAdmin):
    def get_permission(self, request):
        return (
            super().get_permission(request) or request.user.role == 'moderator'
        )


class IsAuthorOrReadOnly(IsAuthenticatedOrReadOnly, IsModerator):
    def has_object_permission(self, request, view, obj):
        return (
            IsModerator.has_object_permission(self, request, view, obj)
            or obj.author == request.user or request.method in SAFE_METHODS
        )
