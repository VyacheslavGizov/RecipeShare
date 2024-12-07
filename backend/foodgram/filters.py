from django.contrib import admin
from django.db.models import Count


class ExistsBaseFilter(admin.SimpleListFilter):

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

    time_costs = {  # написать функцию вычисления на основе данных
        'fast': 15,
        'normal': 35
    }

    def lookups(self, request, model_admin):
        LESS_FORMAT = 'до {} мин. ({})'
        LESS_FORMAT = 'дольше {} мин. ({})'
        recipes = model_admin.get_queryset(request)
        recipes_per_time_costs = {
            legend: recipes.filter(cooking_time__lte=time_cost).count()
            for legend, time_cost in self.time_costs.items()
        }
        recipes_per_time_costs['slow'] = (
            recipes.count() - recipes_per_time_costs['normal']
        )
        return [
            (time_cost, LESS_FORMAT.format(
                time_cost, recipes_per_time_costs[legend]
            )) for legend, time_cost in self.time_costs.items()
        ] + [('slow', LESS_FORMAT.format(self.time_costs['normal'],
                                         recipes_per_time_costs['slow']))]

    def queryset(self, request, recipes):
        if self.value() == 'slow':
            return recipes.filter(cooking_time__gt=self.time_costs['normal'])
        if self.value():
            return recipes.filter(cooking_time__lte=self.value())
