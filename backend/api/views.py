from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import (decorators, permissions, response, serializers,
                            status, viewsets,)
from rest_framework.reverse import reverse

from .filters import IngredientFilter, RecipesFilter
from .pagination import PageNumberPaginationWithLimit
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer,
    IngredientSerialiser,
    ReadRecipeSerialiser,
    ShortRecipeSerializer,
    TagSerializer,
    UserInSubscriptionsSerializer,
    WriteRecipeSerialiser,
)
from .utils import (create_or_validation_error, get_random_string,
                    render_shopping_cart)
from recipes.models import (
    Favorite,
    Ingredient,
    PathKey,
    Recipe,
    RecipeIngridients,
    ShoppingCart,
    Subscription,
    Tag,
)


User = get_user_model()

VALIDATION_ERROR_MESSAGE = 'Ошибка валидации - {error}'
RECIPE_NOT_EXIST_MESSAGE = 'Рецепт с id={id} не найден.'
SELF_SUBSCRIPTION_MESSAGE = 'Нельзя быть подписанным на себя.'
NOT_UNUNIQUE_SUBSCRIPTION_MESSAGE = 'Вы уже подписаны на данного автора.'
URLPATH_LENGTH = 6


class UserViewSet(BaseUserViewSet):
    pagination_class = PageNumberPaginationWithLimit

    def get_permissions(self):
        if self.action == 'me':
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('subscribe', 'subscriptions'):
            return UserInSubscriptionsSerializer
        return super().get_serializer_class()

    @decorators.action(
        methods=['put', 'delete'],
        detail=False,
        url_path='me/avatar',
        url_name='me-avatar',
    )
    def avatar(self, request):
        instance = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data)
        instance.avatar.delete()
        instance.avatar = None
        instance.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        methods=['post', 'delete'],
        detail=True,
        url_name='subscribe',
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, pk=id)
        if user == author:
            raise serializers.ValidationError(SELF_SUBSCRIPTION_MESSAGE)
        if request.method == 'POST':
            create_or_validation_error(Subscription, user=user, author=author)
            return response.Response(
                self.get_serializer(author).data,
                status=status.HTTP_201_CREATED
            )
        get_object_or_404(author.authors, user=user).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=False, url_name='subscribtions')
    def subscriptions(self, request):
        return self.get_paginated_response(
            self.get_serializer(
                self.paginate_queryset(
                    User.objects.filter(authors__user=request.user)
                ),
                many=True
            ).data
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Тега, обеспечивающий только чтение данных."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Продукта, обеспечивающий чтение данных."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerialiser
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (permissions.AllowAny,)


class RecipesViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для модели Рецептов, обеспечивает:
    - операции CRUD для рецептов;
    - получение ссылки на рецепт;
    - добавление и удаление рецепта в Избранное, Список покупок;
    - получение списка покупок в формате .txt.
    """

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    pagination_class = PageNumberPaginationWithLimit

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadRecipeSerialiser
        return WriteRecipeSerialiser

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @decorators.action(
        detail=True,
        permission_classes=(permissions.AllowAny,),
        url_path='get-link',
        url_name='get_link',
    )
    def get_link(self, request, pk=None):
        if not self.queryset.filter(pk=pk).exists():
            raise serializers.ValidationError(
                RECIPE_NOT_EXIST_MESSAGE.format(id=pk))
        source_path = (
            request.META.get('HTTP_REFERER')
            or reverse('api:recipes-detail', args=[pk])
        )
        existed_path_key = PathKey.objects.filter(path=source_path).first()
        key = (existed_path_key.key if existed_path_key
               else get_random_string(URLPATH_LENGTH))
        PathKey.objects.get_or_create(path=source_path, key=key)
        return response.Response({'short-link': request.build_absolute_uri(
            reverse('short-link', args=[key])
        )})

    @decorators.action(
        methods=('post', 'delete',),
        permission_classes=(permissions.IsAuthenticated,),
        detail=True,
        url_name='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            return self.add_to_user_chosen(ShoppingCart, user)
        return self.delete_from_user_chosen(user.shoppingcarts, pk)

    @decorators.action(
        methods=('post', 'delete',),
        permission_classes=(permissions.IsAuthenticated,),
        detail=True,
        url_name='favorite'
    )
    def favorite(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            return self.add_to_user_chosen(Favorite, user)
        return self.delete_from_user_chosen(user.favorites, pk)

    @decorators.action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        url_name='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        user = request.user
        recipes = Recipe.objects.filter(
            shoppingcarts__user=user
        ).order_by('name')
        ingredients = RecipeIngridients.objects.filter(
            recipe__shoppingcarts__user=user
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit',
        ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')
        render_shopping_cart(recipes, ingredients)
        return FileResponse(
            render_shopping_cart(recipes, ingredients),
            as_attachment=True,
            filename='shopping-list.txt'
        )

    def add_to_user_chosen(self, model, user):
        recipe = self.get_object()
        create_or_validation_error(model, user=user, recipe=recipe)
        return response.Response(
            ShortRecipeSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )

    def delete_from_user_chosen(self, user_chosen_recipes, pk=None):
        get_object_or_404(user_chosen_recipes, recipe=pk).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class ShortlinkView(View):
    """
    Обработка короткой ссылки:
    перенаправление по соответствующей полной ссылке.
    """

    def get(self, request, *args, **kwargs):
        print(kwargs['key'])
        return redirect(
            get_object_or_404(PathKey, key=kwargs['key']).path
        )
