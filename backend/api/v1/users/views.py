from djoser.permissions import CurrentUserOrAdmin
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from api.pagination import PageNumberPaginationWithLimit

from .serializers import CustomUserSerializer, AvatarSerializer


class CustomUserViewSet(UserViewSet):

    pagination_class = PageNumberPaginationWithLimit

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [CurrentUserOrAdmin,]
        return super().get_permissions()
    
    # оставить этот сериализатор, но постараться в нем переписать update и destroy, разобраться, как работает  
    @action(
        methods=['put', 'delete'],
        detail=False,  # если тру, то в маршруте должен быть pk
        permission_classes=[CurrentUserOrAdmin,],
        url_path='me/avatar',  # необходимый урл
    )
    def avatar(self, request): # пока так
        user_object = self.get_instance()   # что делает get_instance 
        if request.method == 'PUT':
            serializer = AvatarSerializer(instance=user_object, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        data = {'avatar': ''}
        serializer = AvatarSerializer(instance=user_object, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        
    
        
