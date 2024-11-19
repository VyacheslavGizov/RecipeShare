from rest_framework import permissions
# from rest_framework.permissions import SAFE_METHODS


class IsAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
