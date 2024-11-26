from djoser.permissions import CurrentUserOrAdmin
from djoser.views import UserViewSet
from rest_framework import decorators, permissions, response, status

from .serializers import AvatarSerializer, CreateSubscribeSerializer
from api.pagination import PageNumberPaginationWithLimit
from apps.users.models import CustomUser


class CustomUserViewSet(UserViewSet):

    pagination_class = PageNumberPaginationWithLimit

    def get_permissions(self):
        if self.action in ('me', 'avatar'):
            self.permission_classes = (CurrentUserOrAdmin,)
        if self.action in ('subscribe', 'subscriptions'):
            self.permission_classes = (permissions.IsAuthenticated,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'avatar':
            return AvatarSerializer
        if self.action in ('subscribe', 'subscriptions'):
            return CreateSubscribeSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.action == 'subscriptions':
            return self.request.user.subscriptions.all()
        return super().get_queryset()

    def get_object(self):
        if self.action == 'avatar':
            return self.request.user
        return super().get_object()

    @decorators.action(
        methods=['put', 'delete'],
        detail=False,
        url_path='me/avatar',
        url_name='me-avatar',
    )
    def avatar(self, request):
        if request.method == 'PUT':
            return self.update(request)
        instance = request.user
        instance.avatar = None
        instance.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        methods=['post', 'delete'],
        detail=True,
        url_name='subscribe',
    )
    def subscribe(self, request, id=None):
        if not CustomUser.objects.filter(id=id).exists():
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        if request.method == 'POST':
            serializer = self.get_serializer(data={'author': id})
            if serializer.is_valid():
                serializer.save(user=request.user)
                return response.Response(serializer.data,
                                         status=status.HTTP_201_CREATED)
            return response.Response(serializer.errors,
                                     status=status.HTTP_400_BAD_REQUEST)
        subscriptions = request.user.subscriptions.filter(author=id)
        if not subscriptions.exists():
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        subscriptions.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=False,
        url_name='subscribtions',
    )
    def subscriptions(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)
