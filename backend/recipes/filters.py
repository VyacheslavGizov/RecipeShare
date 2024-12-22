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

    default_time_limits = [5, 15, 35]
    time_limits = None

    def lookups(self, request, model_admin):
        LINE_FORMAT = 'до {} мин. ({})'
        recipes = model_admin.get_queryset(request)
        self.time_limits = self.get_time_limits(recipes)
        return [(
            limit, LINE_FORMAT.format(
                limit, self.get_recipes_between(recipes, range_).count())
        ) for limit, range_ in self.time_limits.items()]

    def queryset(self, request, recipes):
        if self.value() in self.time_limits:
            return self.get_recipes_between(recipes,
                                            self.time_limits[self.value()])
        return recipes

    def get_time_limits(self, recipes):
        cooking_times = list(set(
            [item[0] for item in recipes.values_list('cooking_time')]
        ))
        if len(cooking_times) < 3:
            times = self.default_time_limits
        else:
            min_time = min(cooking_times)
            max_time = max(cooking_times)
            normal_time = round(0.5 * (max_time + min_time))
            short_time = round(0.5 * (normal_time + min_time))
            if short_time == normal_time:
                times = [min_time, normal_time, max_time]
            else:
                times = [short_time, normal_time, max_time]
        lower_limits = [0]
        lower_limits[1:] = times[:-1]
        return {str(range_[-1]): range_ for range_ in zip(lower_limits, times)}

    @staticmethod
    def get_recipes_between(recipes, range_):
        return recipes.filter(Q(cooking_time__gt=range_[0]) &
                              Q(cooking_time__lte=range_[1]))
