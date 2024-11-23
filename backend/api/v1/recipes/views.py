from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, reverse, response, decorators, status

from .filters import IngredientFilter, RecipesFilter
from .serializers import (
    IngredientSerialiser,
    ReadRecipeSerialiser,
    CreateUpdateRecipeSerialiser,
    TagSerializer,
    AddRecipeInShopingCartSerializer,
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
        if request.method == 'POST':
            serializer = self.get_serializer(data={'recipe': pk})
            if serializer.is_valid():
                serializer.save(user=request.user)
                return response.Response(serializer.data, status=status.HTTP_201_CREATED)
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # использовать обратный менеджер и в других местах
        recipe = get_object_or_404(models.Recipe, pk=pk)
        user_cart_record = recipe.users_add_in_shoping_cart.filter(user=request.user.id)
        if not user_cart_record.exists():
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        user_cart_record.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)





        # if not models.Recipe.objects.filter(pk=pk).exists():
        #     return response.Response(status=status.HTTP_404_NOT_FOUND)
        # try:
        #     get_object_or_404(models.ShopingCart, recipe=pk, user=request.user).delete()
        # except:
        #     return response.Response(status=status.HTTP_400_BAD_REQUEST)
        # return response.Response(status=status.HTTP_204_NO_CONTENT)
