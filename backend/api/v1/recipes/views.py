from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.http import Http404, HttpResponse
from rest_framework import decorators, permissions, response, status, viewsets

from rest_framework.reverse import reverse

from .filters import IngredientFilter, RecipesFilter
from .serializers import (
    AddRecipeInFavoriteSerializer,
    AddRecipeInShopingCartSerializer,
    CreateUpdateRecipeSerialiser,
    IngredientSerialiser,
    ReadRecipeSerialiser,
    TagSerializer,
)
from api.pagination import PageNumberPaginationWithLimit
from api.permissions import IsAuthorOrReadOnly
from apps.recipes import models


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Тега обеспечивающий только чтение данных."""

    queryset = models.Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Ингредиентов обеспечивающий чтение данных."""

    queryset = models.Ingredient.objects.all()
    serializer_class = IngredientSerialiser
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (permissions.AllowAny,)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Рецептов обеспечивающий операции CRUD."""

    queryset = models.Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    pagination_class = PageNumberPaginationWithLimit

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadRecipeSerialiser
        if self.action == 'shopping_cart':
            return AddRecipeInShopingCartSerializer
        if self.action == 'favorite':
            return AddRecipeInFavoriteSerializer
        return CreateUpdateRecipeSerialiser

    def get_permissions(self):
        if self.action in ('retrieve', 'get_link'):
            self.permission_classes = (permissions.AllowAny,)
        if self.action in ('shopping_cart', 'favorite',
                           'download_shopping_cart'):
            self.permission_classes = (permissions.IsAuthenticated,)
        return super().get_permissions()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = False
        return self.update(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @decorators.action(
        detail=True,
        url_path='get-link',
        url_name='get_link',
    )
    def get_link(self, request, pk=None):
        self.recipe_exist_or_404(pk)
        return response.Response({'short-link': request.build_absolute_uri(
            reverse('api:recipes-detail', kwargs={'pk': pk})
        )})

    @decorators.action(
        methods=('post', 'delete',),
        detail=True,
        url_name='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        self.recipe_exist_or_404(pk)
        if request.method == 'POST':
            return self.add_recipe(request, pk)
        return self.delete_recipe(request.user.shopping_cart_records, pk)

    @decorators.action(
        methods=('post', 'delete',),
        detail=True,
        url_name='favorite'
    )
    def favorite(self, request, pk=None):
        self.recipe_exist_or_404(pk)
        if request.method == 'POST':
            return self.add_recipe(request, pk)
        return self.delete_recipe(request.user.favorite_records, pk)

    @decorators.action(
        detail=False,
        url_name='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        content = self.convert_to_string(
            models.RecipeIngridients.objects.filter(
                recipe__shopping_cart_records__user=request.user
            ).values(
                'ingredient__name', 'ingredient__measurement_unit',
            ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')
        )
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format('shoping-lis.txt')
        )
        return response

    @staticmethod
    def convert_to_string(ingredients):
        LINE_FORMAT = '- {name} ({measurement_unit}):  {amount}\n'
        content = 'Список покупок: \n\n'
        for ingredient in ingredients:
            content += LINE_FORMAT.format(
                name=ingredient['ingredient__name'],
                measurement_unit=ingredient['ingredient__measurement_unit'],
                amount=ingredient['total_amount'],
            )
        return content

    def recipe_exist_or_404(self, pk):
        if not self.queryset.filter(pk=pk).exists():
            raise Http404

    def add_recipe(self, request, pk=None):
        serializer = self.get_serializer(data={'recipe': pk})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return response.Response(serializer.data,
                                     status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors,
                                 status=status.HTTP_400_BAD_REQUEST)

    def delete_recipe(self, user_chosen_recipes, pk=None):
        recipe = user_chosen_recipes.filter(recipe=pk)
        if not recipe.exists():
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        recipe.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
