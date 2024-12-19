from django_filters.rest_framework import filters, FilterSet
from django.contrib.auth import get_user_model

from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class IngredientFilter(FilterSet):
    """Фильтр по названию продукта."""

    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipesFilter(FilterSet):
    """Фильтр по избранному, автору, списку покупок и тегам."""

    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited',
        label='В избранном',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart',
        label='В списке покупок'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, recipes, name, value):
        if self.request.user.is_authenticated and value == 1:
            return recipes.filter(favorites__user=self.request.user)
        return recipes

    def get_is_in_shopping_cart(self, recipes, name, value):
        if self.request.user.is_authenticated and value == 1:
            return recipes.filter(shoppingcarts__user=self.request.user)
        return recipes
