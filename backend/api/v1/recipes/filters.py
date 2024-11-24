from django_filters.rest_framework import FilterSet, filters
from django.contrib.auth import get_user_model

from apps.recipes import models

User = get_user_model()

# разбираться с фильтрацией, сделать допы
# https://yourtodo.ru/ru/posts/djangofilters-i-django-rest-framework/
# https://django-filter.readthedocs.io/en/stable/ref/filters.html#label 

class IngredientFilter(FilterSet):  # может сдеать универсальным
    """Фильтр по названию ингредиента."""
    # фильтр позволяет искать по параметру в URL/?name=<> 
    # ингредиенты из по вхождению в начало значения, указанного в поле из
    # fields без учета регистра 

    # можно реализовать двойную фильтрацию(смотреть в подсказки)

    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')  # поле поиска отображаемое name= и метод поиска

    class Meta:
        model = models.Ingredient
        fields = ('name',)  # поля модели, в которых осуществляется поиск


class RecipesFilter(FilterSet):  # может сдеать универсальным
    """Фильтр по избранному, автору, списку покупок и тегам."""
    # фильтр позволяет искать по параметру в URL/?name=<> 
    # ингредиенты из по вхождению в начало значения, указанного в поле из
    # fields без учета регистра 

    # можно реализовать двойную фильтрацию(смотреть в подсказки)

    # is_favorited = filters.BooleanFilter
    # author = filters.ModelChoiceField(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        queryset=models.Tag.objects.all(),
        field_name='tags__slug',  # имя поля в теге 
        to_field_name='slug'  # имя поля, которому соответствует
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited', label='В избранном')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart', label='В списке покупок'
    )

    class Meta:
        model = models.Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart',)  # поля модели, в которых осуществляется поиск
    
    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value is True:
            return queryset.filter(favorite_records__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value is True:
            return queryset.filter(shopping_cart_records__user=self.request.user)
        return queryset
