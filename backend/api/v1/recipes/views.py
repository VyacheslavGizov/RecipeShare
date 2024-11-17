from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions

from .filters import IngredientFilter
from .serializers import TagSerializer, IngredientSerialiser
from apps.recipes import models


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

