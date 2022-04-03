from rest_framework.permissions import (BasePermission, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly, SAFE_METHODS
                                        )


class IsAnonymous(BasePermission):
    pass


class AuthUserOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return (
                request.method in SAFE_METHODS
                or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


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
            request.user.role == 'moderator' or super().get_permission(request)
        )


class IsAuthorOrReadOnly(IsAuthenticatedOrReadOnly, IsModerator):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or IsModerator.has_object_permission(self, request, view, obj)
        )
