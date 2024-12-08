from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as BaseUserViewSet
from djoser.permissions import CurrentUserOrAdmin
from rest_framework import decorators, permissions, response, status

from .serializers import AvatarSerializer, UserInSubscriptionsSerializer
from .pagination import PageNumberPaginationWithLimit
from foodgram.models import Subscription


User = get_user_model()


class UserViewSet(BaseUserViewSet):
    pagination_class = PageNumberPaginationWithLimit

    def get_permissions(self):
        if self.action == 'me':
            return (CurrentUserOrAdmin(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('subscribe', 'subscriptions'):
            return UserInSubscriptionsSerializer
        return super().get_serializer_class()

    @decorators.action(
        methods=['put', 'delete'],
        detail=False,
        url_path='me/avatar',
        url_name='me-avatar',
    )
    def avatar(self, request):
        instance = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data)
        instance.avatar.delete()  # добавил удаление файла, проверить, что работает
        instance.avatar = None
        instance.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        methods=['post', 'delete'],
        detail=True,
        url_name='subscribe',
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            try:
                Subscription.objects.create(user=user, author=author)
            except IntegrityError as error:
                return response.Response(
                    str(error),
                    status=status.HTTP_400_BAD_REQUEST
                )
            return response.Response(
                self.get_serializer(author).data,
                status=status.HTTP_201_CREATED
            )
        get_object_or_404(author.authors, user=user).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=False, url_name='subscribtions')
    def subscriptions(self, request):
        queryset = User.objects.filter(authors__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)
