from django.contrib import admin
from django.db.models import Count


LABELS = [('exists', 'да'), ('no', 'нет'), ]
LESS_FORMAT = 'до {} мин ({})'
MORE_FORMAT = 'больше ({})'


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
        time_ranges = self.get_time_ranges(recipes=recipes, ranges_number=3)
        return (time_ranges and [(range_, LESS_FORMAT.format(
            range_[1], self.get_recipes_between(recipes, range_).count()))
            if range_ != time_ranges[-1]
            else (range_, MORE_FORMAT.format(
                self.get_recipes_between(recipes, range_).count()))
            for range_ in time_ranges])

    def queryset(self, request, recipes):
        if self.value():
            return self.get_recipes_between(recipes, eval(self.value()))
        return recipes

    def get_time_ranges(self, recipes, ranges_number):
        cooking_times = sorted(list(set(
            item[0] for item in recipes.values_list('cooking_time')
        )))
        times_length = len(cooking_times)
        if times_length < ranges_number or ranges_number == 1:
            return None
        index_step = times_length // ranges_number
        return [self.get_first_and_last(
            cooking_times[i * index_step:(i + 1) * index_step])
            if i < ranges_number - 1
            else self.get_first_and_last(cooking_times[i * index_step:])
            for i in range(ranges_number)]

    @staticmethod
    def get_first_and_last(elements):
        return elements[0], elements[-1]

    @staticmethod
    def get_recipes_between(recipes, range_):
        return recipes.filter(cooking_time__range=range_)
