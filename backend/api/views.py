from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.permissions import CurrentUserOrAdmin
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import decorators, permissions, response, status, viewsets, serializers
from rest_framework.reverse import reverse

from .pagination import PageNumberPaginationWithLimit
from foodgram.models import (
    Subscription,
    Tag,
    Ingredient,
    Recipe,
    RecipeIngridients,
    Favorite,
    ShoppingCart
)
from .filters import IngredientFilter, RecipesFilter
from .serializers import (
    AvatarSerializer,
    IngredientSerialiser,
    ReadRecipeSerialiser,
    TagSerializer,
    UserInSubscriptionsSerializer,
    WriteRecipeSerialiser,
    ShortRecipeSerializer
)
from .pagination import PageNumberPaginationWithLimit
from .permissions import IsAuthorOrReadOnly


User = get_user_model()

VALIDATION_ERROR_MESSAGE = 'Ошибка валидации - {error}'
RECIPE_NOT_EXIST_MESSAGE = 'Рецепт с id={id} не найден.'


class UserViewSet(BaseUserViewSet):
    pagination_class = PageNumberPaginationWithLimit

    def get_permissions(self):
        if self.action == 'me':
            return (CurrentUserOrAdmin(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('subscribe', 'subscriptions'):
            return UserInSubscriptionsSerializer
        return super().get_serializer_class()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = False
        return super().update(request, *args, **kwargs)

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
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            try:
                Subscription.objects.create(user=user, author=author)
            except (IntegrityError, ValidationError) as error:
                raise serializers.ValidationError(
                    VALIDATION_ERROR_MESSAGE.format(error=error)
                )
            return response.Response(
                self.get_serializer(author).data,
                status=status.HTTP_201_CREATED
            )
        get_object_or_404(author.authors, user=user).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=False, url_name='subscribtions')
    def subscriptions(self, request):
        queryset = User.objects.filter(authors__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Тега обеспечивающий только чтение данных."""

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
    """Вьюсет для модели Рецептов обеспечивающий операции CRUD."""

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
        permission_classes=(permissions.AllowAny,),  # добавил возможно не нужно в приложении
        url_path='get-link',
        url_name='get_link',
    )
    def get_link(self, request, pk=None):
        self.recipe_exist_or_400(pk)
        return response.Response({'short-link': request.build_absolute_uri(
            reverse('api:recipes-detail', args=[pk])
        )})

    @decorators.action(
        methods=('post', 'delete',),
        permission_classes=(permissions.IsAuthenticated,),  # добавил возможно не нужно в приложении
        detail=True,
        url_name='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            return self.add_to_user_chosen(ShoppingCart, user)
        return self.delete_from_user_chosen(user.shoppingcart, pk)

    @decorators.action(
        methods=('post', 'delete',),
        permission_classes=(permissions.IsAuthenticated,),  # добавил возможно не нужно в приложении
        detail=True,
        url_name='favorite'
    )
    def favorite(self, request, pk=None):
        user = request.user
        if request.method == 'POST':
            return self.add_to_user_chosen(Favorite, user)
        return self.delete_from_user_chosen(user.favorite, pk)

    
# жестко переписать
    @decorators.action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),  # добавил возможно не нужно в приложении
        url_name='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        user = request.user
        recipes = Recipe.objects.filter(shoppingcart__user=user).values('name')
        ingredients = RecipeIngridients.objects.filter(
            recipe__shoppingcart__user=user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit',
        ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')
        print(recipes)
        print(ingredients)
        return response.Response(status=status.HTTP_200_OK)

    def recipe_exist_or_400(self, pk):
        if not self.queryset.filter(pk=pk).exists():
            raise serializers.ValidationError(
                RECIPE_NOT_EXIST_MESSAGE.format(id=pk))

    def add_to_user_chosen(self, model, user):
        recipe = self.get_object()
        try:
            model.objects.create(user=user, recipe=recipe)
        except (IntegrityError, ValidationError) as error:
            raise serializers.ValidationError(
                VALIDATION_ERROR_MESSAGE.format(error=error))
        return response.Response(ShortRecipeSerializer(recipe).data,
                                 status=status.HTTP_201_CREATED)

    def delete_from_user_chosen(self, user_chosen_recipes, pk=None):
        get_object_or_404(user_chosen_recipes, recipe=pk).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
