from django_filters.rest_framework import FilterSet, filters
from django.contrib.auth import get_user_model

from apps.recipes import models

User = get_user_model()


class IngredientFilter(FilterSet):
    """Фильтр по названию ингредиента."""

    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = models.Ingredient
        fields = ('name',)


class RecipesFilter(FilterSet):
    """Фильтр по избранному, автору, списку покупок и тегам."""

    tags = filters.ModelMultipleChoiceFilter(
        queryset=models.Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited',
                                         label='В избранном')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart', label='В списке покупок'
    )

    class Meta:
        model = models.Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart',)

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value == 1:
            return queryset.filter(favorite_records__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value == 1:
            return queryset.filter(
                shopping_cart_records__user=self.request.user
            )
        return queryset
