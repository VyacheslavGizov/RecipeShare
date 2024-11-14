from djoser.permissions import CurrentUserOrAdmin
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import PageNumberPaginationWithLimit

# from .serializers import CustomUserSerializer, AvatarSerialiser


class CustomUserViewSet(UserViewSet):

    pagination_class = PageNumberPaginationWithLimit

    # def get_permissions(self):
    #     if self.action == 'me':
    #         self.permission_classes = [IsAuthenticated, CurrentUserOrAdmin]
    #     return super().get_permissions()
    

    # @action(
    #         detail=True,
    #         methods=['put', 'delete'],
    #         permission_classes=[IsAuthenticated],
    # )
    # def avatar(self, request, pk=None):
    #     """Добавить или удалить аватар."""

    #     user = self.get_object()
    #     if request.method == 'PUT':
    #         serializer = CustomUserSerializer(user, data=request.data, partial=True)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(serializer.data, status=status.HTTP_201_CREATED)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
