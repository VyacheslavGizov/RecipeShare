from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Разрешение на изменение объекта только для автора."""

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.method == 'GET'
