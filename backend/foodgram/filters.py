from django.contrib import admin
from django.db.models import Count


class ExistsBaseFilter(admin.SimpleListFilter):
    """
    Базовый класс для фильтров по признаку существования записей
    связанной вторичной модели. В parameter_name необходимо указать
    related_name вторичной модели.
    """
    # проверить оформление докстринга

    def lookups(self, request, model_admin):
        return [('exists', 'да'),
                ('no', 'нет')]

    def queryset(self, request, users):
        users = users.annotate(parameter_quantity=Count(self.parameter_name))
        if self.value() == 'exists':
            return users.filter(parameter_quantity__gt=0)
        if self.value() == 'no':
            return users.filter(parameter_quantity=0)


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

    default_time_limits = [15, 35]
    time_limits = None

    def lookups(self, request, model_admin):
        LESS_FORMAT = 'до {} мин. ({})'
        LONGER_FORMAT = 'дольше {} мин. ({})'
        recipes = model_admin.get_queryset(request)
        self.time_limits = self.get_time_limits(recipes)
        recipes_per_time_limits = [
            (time_limit, recipes.filter(cooking_time__lte=time_limit).count())
            for time_limit in self.time_limits
        ]
        return [
            (time_limit, LESS_FORMAT.format(time_limit, recipes_number))
            for time_limit, recipes_number in recipes_per_time_limits
        ] + [('long', LONGER_FORMAT.format(
            self.time_limits[-1],
            recipes.count() - recipes_per_time_limits[-1][1]
        ))]

    def queryset(self, request, recipes):
        if self.value() == 'long':
            return recipes.filter(cooking_time__gt=self.time_limits[-1])
        if self.value():
            return recipes.filter(cooking_time__lte=self.value())

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
            return [min_time, higher_limit]
        return [lower_limit, higher_limit]
