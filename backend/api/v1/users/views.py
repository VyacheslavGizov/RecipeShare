from djoser.permissions import CurrentUserOrAdmin
from djoser.views import UserViewSet
from rest_framework import decorators, response, status, permissions

from .serializers import AvatarSerializer, SubscriptionSerialiser
from api.pagination import PageNumberPaginationWithLimit


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
        return super().get_serializer_class()

    def get_object(self):  # чтобы отработал update в avatar
        if self.action == 'avatar':
            return self.request.user
        return super().get_object()

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

    # @decorators.action(
    #         methods=['get'],
    #         detail=False,
    #         permission_classes=(permissions.IsAuthenticated,),
    #         # возможно по-умолчанию такие создаст
    #         url_path='subscriptions',
    #         url_name='subscriptions'
    # )
    # def subscriptions(self, request):
    #     instance = self.request.user.subscriptions.all()
    #     serialiser = SubscriptionSerialiser(instance=instance, many=True)
    #     return response.Response(serialiser.data)