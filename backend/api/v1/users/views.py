from djoser.permissions import CurrentUserOrAdmin
from djoser.views import UserViewSet
from rest_framework import decorators, response, status

from .serializers import AvatarSerializer
from api.pagination import PageNumberPaginationWithLimit


class CustomUserViewSet(UserViewSet):

    pagination_class = PageNumberPaginationWithLimit

    def get_permissions(self):
        # явно задаю разрешение на этот эндпоинт, потому-что его нет в настройках
        if self.action == 'me':
            self.permission_classes = (CurrentUserOrAdmin,)
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

    # def avatar(self, request):  # для отдельного сериализатора
    #     instance = request.user
    #     if request.method == 'PUT':
    #         serializer = AvatarSerializer(instance=instance, data=request.data)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return response.Response(serializer.data, status=status.HTTP_200_OK)
    #         return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     if request.method == 'DELETE':
    #         instance.avatar = None
    #         instance.save()
    #         return response.Response(status=status.HTTP_204_NO_CONTENT)
