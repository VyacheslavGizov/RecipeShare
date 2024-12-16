from django.contrib import admin
from django.db.models import Count, Q


class ExistsBaseFilter(admin.SimpleListFilter):
    """
    Базовый класс для фильтров по признаку существования записей
    связанной вторичной модели. В parameter_name необходимо указать
    related_name вторичной модели.
    """

    def lookups(self, request, model_admin):
        return [
            ('exists', 'да'),
            ('no', 'нет'),
        ]

    def queryset(self, request, users):
        users_with_count = users.annotate(
            parameter_quantity=Count(self.parameter_name))
        if self.value() == 'exists':
            return users_with_count.filter(parameter_quantity__gt=0)
        if self.value() == 'no':
            return users_with_count.filter(parameter_quantity=0)
        return users


class RecipesExistsFilter(ExistsBaseFilter):
    title = 'есть рецепты'
    parameter_name = 'recipes'


class SubcribersExistsFilter(ExistsBaseFilter):
    title = 'есть подписчики'
    parameter_name = 'authors'


class SubcriptionsExistsFilter(ExistsBaseFilter):
    title = 'есть подписки'
    parameter_name = 'subscribers'


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    default_time_limits = [0, 15, 35]

    def lookups(self, request, model_admin):
        LINE_FORMAT = 'до {} мин. ({})'
        recipes = model_admin.get_queryset(request)
        self.time_limits = self.get_time_limits(recipes)
        return [(
            limit, LINE_FORMAT.format(
                limit, self.get_recipes_between(recipes, limit).count())
        ) for limit in self.time_limits]

    def queryset(self, request, recipes):
        if self.value() in map(str, self.time_limits):
            return self.get_recipes_between(recipes, int(self.value()))
        return recipes

    def get_time_limits(self, recipes):
        cooking_times = list(set(
            [item[0] for item in recipes.values_list('cooking_time')]
        ))
        if len(cooking_times) < 3:
            return self.default_time_limits
        min_time = min(cooking_times)
        max_time = max(cooking_times)
        higher_limit = round(0.5 * (max_time + min_time))
        lower_limit = round(0.5 * (higher_limit + min_time))
        if lower_limit == higher_limit:
            return [min_time, higher_limit, max_time]
        return [lower_limit, higher_limit, max_time]

    def get_recipes_between(self, recipes, limit):
        limits = [0]
        limits.extend(self.time_limits)
        index = limits.index(limit)
        return recipes.filter(Q(cooking_time__gt=limits[index-1]) &
                              Q(cooking_time__lte=limits[index]))
