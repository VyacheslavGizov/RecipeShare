from django_filters.rest_framework import FilterSet, filters

from apps.recipes import models


class IngredientFilter(FilterSet):  # может сдеать универсальным
    """Фильтр по названию ингредиента."""
    # фильтр позволяет искать по параметру в URL/?name=<> 
    # ингредиенты из по вхождению в начало значения, указанного в поле из
    # fields без учета регистра 

    # можно реализовать двойную фильтрацию(смотреть в подсказки)

    name = filters.CharFilter(lookup_expr='istartswith')  # поле поиска отображаемое name= и метод поиска

    class Meta:
        model = models.Ingredient
        fields = ('name',)  # поля модели, в которых осуществляется поиск
