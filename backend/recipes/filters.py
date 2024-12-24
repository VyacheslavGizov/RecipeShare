from django.contrib import admin
from django.db.models import Count


LABELS = [('exists', 'да'), ('no', 'нет'), ]
LINE_FORMAT = 'до {} мин. ({})'


class ExistsBaseFilter(admin.SimpleListFilter):
    """
    Базовый класс для фильтров по признаку существования записей
    связанной вторичной модели. В parameter_name необходимо указать
    related_name вторичной модели.
    """

    def lookups(self, request, model_admin):
        return LABELS

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

    def lookups(self, request, model_admin):
        recipes = model_admin.get_queryset(request)
        time_limits = self.get_time_limits(recipes)
        return (
            time_limits
            and [(range_, LINE_FORMAT.format(
                limit, self.get_recipes_between(recipes, range_).count()
            )) for limit, range_ in time_limits.items()]
        )

    def queryset(self, request, recipes):
        if self.value():
            return self.get_recipes_between(recipes, eval(self.value()))
        return recipes

    def get_time_limits(self, recipes):
        cooking_times = list(set(
            item[0] for item in recipes.values_list('cooking_time')
        ))
        if len(cooking_times) < 3:
            return None
        min_time = min(cooking_times)
        max_time = max(cooking_times)
        normal_time = round((max_time + min_time) // 2)
        short_time = round((normal_time + min_time) // 2)
        if short_time == normal_time:
            times = [min_time, normal_time, max_time]
        else:
            times = [short_time, normal_time, max_time]
        return {str(range_[-1]): range_
                for range_ in zip([0] + times[:-1], times)}

    @staticmethod
    def get_recipes_between(recipes, range_):
        return recipes.filter(cooking_time__range=range_)
