from djoser.permissions import CurrentUserOrAdmin
from djoser.views import UserViewSet
from rest_framework import decorators, response, status, permissions

from .serializers import AvatarSerializer, SubscribeSerializer, UserInSubscriptionsSerializer
from api.pagination import PageNumberPaginationWithLimit
from apps.users.models import CustomUser, Subscription


class CustomUserViewSet(UserViewSet):

    pagination_class = PageNumberPaginationWithLimit  # добавить возможность указывать limit при объявлении экземпляра

    def get_permissions(self):
        # явно задаю разрешение на этот эндпоинт, потому-что его нет в настройках
        if self.action == 'me':
            self.permission_classes = (CurrentUserOrAdmin,)
            # return (CurrentUserOrAdmin,)
        return super().get_permissions()

    def get_serializer_class(self):  # чтобы отработал update в avatar
        if self.action == 'avatar':
            return AvatarSerializer
        if self.action == 'subscribe':
            return SubscribeSerializer
        if self.action == 'subscriptions':
            return SubscribeSerializer
        return super().get_serializer_class()

    def get_object(self):  # чтобы отработал update в avatar
        if self.action == 'avatar':
            return self.request.user
        return super().get_object()
    
    def get_queryset(self):
        if self.action == 'subscriptions':
            return self.request.user.subscriptions.all()
        return super().get_queryset()

    @decorators.action(
        methods=['put', 'delete'],
        detail=False,  # если тру, то в маршруте должен быть pk
        permission_classes=(CurrentUserOrAdmin,),
        url_path='me/avatar',  # необходимый урл
        url_name='me-avatar',  # будет использовано для имени адреса как basename-urlname (user-me-avatar)
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
        permission_classes=[permissions.IsAuthenticated],
        url_name='subscribe',
    )
    def subscribe(self, request, id=None):
        # аналогично в recipes
        if not CustomUser.objects.filter(id=id).exists():
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        if request.method == 'POST':
            serializer = self.get_serializer(data={'author': id})
            if serializer.is_valid():
                serializer.save(user=request.user)
                return response.Response(serializer.data, status=status.HTTP_201_CREATED)
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        subscriptions = request.user.subscriptions.filter(author=id)
        if not subscriptions.exists():
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        subscriptions.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
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
