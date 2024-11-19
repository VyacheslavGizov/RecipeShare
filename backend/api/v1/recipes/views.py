from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions

from .filters import IngredientFilter
from .serializers import (
    IngredientSerialiser,
    ReadRecipeSerialiser,
    CreateUpdateRecipeSerialiser,
    TagSerializer,
)
from apps.recipes import models
# from api.pagination import PageNumberPaginationWithLimit
from api.permissions import IsAuthorOrReadOnly


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Тега обеспечивающий только чтение данных."""

    queryset = models.Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Ингредиентов обеспечивающий только чтение данных."""

    queryset = models.Ingredient.objects.all()
    serializer_class = IngredientSerialiser
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (permissions.AllowAny,)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Рецептов обеспечивает операции CRUD."""

    # над разрешениями подумать
    queryset = models.Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    # permission_classes = (IsAuthorOrReadOnly | permissions.IsAdminUser)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadRecipeSerialiser
        return CreateUpdateRecipeSerialiser

    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = (permissions.AllowAny,)
        return super().get_permissions()
