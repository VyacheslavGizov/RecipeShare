from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, reverse, response, decorators, status
from django.db.models import Sum
from django.http import HttpResponse

from .filters import IngredientFilter, RecipesFilter
from .serializers import (
    IngredientSerialiser,
    ReadRecipeSerialiser,
    CreateUpdateRecipeSerialiser,
    TagSerializer,
    AddRecipeInShopingCartSerializer,
    AddRecipeInFavoriteSerializer,
)
from apps.recipes import models
# from api.pagination import PageNumberPaginationWithLimit
from api.permissions import IsAuthorOrReadOnly
from api.pagination import PageNumberPaginationWithLimit


# возможно в queryset нужно что-то заранее подгрузить, чтобы избежать доп запросов

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
    # permission_classes = (permissions.IsAdminUser,)
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
        if self.action == 'retrieve':
            self.permission_classes = (permissions.AllowAny,)
            # return (permissions.AllowAny,)
        return super().get_permissions()
    
    def partial_update(self, request, *args, **kwargs):
        # при putch запросе все поля обязаельные
        kwargs['partial'] = False
        return self.update(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    @decorators.action(
        detail=True,  # если тру, то в маршруте должен быть pk
        permission_classes=(permissions.AllowAny,),
        url_path='get-link',  # необходимый урл
        url_name='get_link',  # будет использовано для имени адреса как basename-urlname (user-me-avatar)
    )
    def get_link(self, request, pk=None):
        url = reverse.reverse('api:recipes-detail', kwargs={'pk': pk})
        original_url = request.build_absolute_uri(url)  # тут додумать
        data = {'short-link': original_url}
        return response.Response(data)

    @decorators.action(
        detail=True,
        methods=('post', 'delete',),
        permission_classes=(permissions.IsAuthenticated,),
        url_name='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        if not models.Recipe.objects.filter(pk=pk).exists():
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        if request.method == 'POST':
            return self.add_recipe(request, pk)
        return self.delete_recipe(request.user.shopping_cart_records, pk)
    
    @decorators.action(
        detail=True,
        methods=('post', 'delete',),
        permission_classes=(permissions.IsAuthenticated,),
        url_name='favorite'
    )
    def favorite(self, request, pk=None):
        if not models.Recipe.objects.filter(pk=pk).exists():
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        if request.method == 'POST':
            return self.add_recipe(request, pk)
        return self.delete_recipe(request.user.favorite_records, pk)
    
    @decorators.action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        url_name='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        ingredients = models.RecipeIngridients.objects.filter(
            recipe__shopping_cart_records__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit',
        ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')
        filename = 'shoping-lis.txt'
        content = self.convert_to_string(ingredients)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
        return response

    def convert_to_string(self, ingredients_queryset):
        content = 'Список покупок: \n\n'
        LINE = '- {name} ({measurement_unit}):  {amount}\n'
        for ingredient in ingredients_queryset:
            content += LINE.format(
                name=ingredient['ingredient__name'],
                measurement_unit=ingredient['ingredient__measurement_unit'],
                amount=ingredient['total_amount'],
            )
        return content

    def add_recipe(self, request, pk=None):
        serializer = self.get_serializer(data={'recipe': pk})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete_recipe(self, recipe_user_records, pk=None):
        """Для удаления нужно передать записи из списка покупок текущего пользователя."""
        # над именами подумать
        recipe = recipe_user_records.filter(recipe=pk)
        if not recipe.exists():
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        recipe.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)



       
