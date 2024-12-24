from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
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
from .utils import render_shopping_cart
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngridients,
    ShoppingCart,
    Subscription,
    Tag,
)


User = get_user_model()

SELF_SUBSCRIPTION_MESSAGE = 'Нельзя быть подписанным на себя.'
NOT_UNUNIQUE_SUBSCRIPTION_MESSAGE = 'Вы уже подписаны на данного автора.'
NOT_UNUNIQUE_MESSAGE = 'Попытка создать дублирующуюся запись в модели {model}.'


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
        if request.method == 'POST':
            if user == author:
                raise serializers.ValidationError(SELF_SUBSCRIPTION_MESSAGE)
            _, is_created = Subscription.objects.get_or_create(
                user=user, author=author)
            if not is_created:
                raise serializers.ValidationError(
                    NOT_UNUNIQUE_MESSAGE.format(model=Subscription))
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
        if not Recipe.objects.filter(pk=pk).exists():
            raise serializers.ValidationError(pk)
        return response.Response({'short-link': request.build_absolute_uri(
            reverse('short-link', args=[pk])
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
        return FileResponse(
            render_shopping_cart(recipes, ingredients),
            as_attachment=True,
            filename='shopping-list.txt'
        )

    def add_to_user_chosen(self, model, user):
        recipe = self.get_object()
        _, is_created = model.objects.get_or_create(user=user, recipe=recipe)
        if not is_created:
            raise serializers.ValidationError(
                NOT_UNUNIQUE_MESSAGE.format(model=model))
        return response.Response(
            ShortRecipeSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )

    def delete_from_user_chosen(self, user_chosen_recipes, pk=None):
        get_object_or_404(user_chosen_recipes, recipe=pk).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
