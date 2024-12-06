from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.db.models import Count, Q


from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngridients,
    ShoppingCart,
    Subscription,
    Tag,
)


User = get_user_model()

FAVORITE_RESIPE_TITLE = 'раз в Избранном'
FULL_NAME_TITLE = 'Имя_фамилия'
RECIPES_COUNT_TITLE = 'Рецептов'
SUBSCRIBERS_TITLE = 'Подписчиков'
SUBSCRIPTIONS_TITLE = 'Подписок'
AVATAR_TITLE = 'Аватар'
EMPTY_AVATAR = 'Не задан'
RECIPE_IMAGE_TITLE = 'Фото блюда'  # есть в моделях, может объединить
TAGS_TITLE = 'Теги'
INGREDIENTS_TITLE = 'Продукты'

# создать базовый класс с дублирующимися методами


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


class RecipesFilter(admin.SimpleListFilter):
    title = 'время приготовления'
    parameter_name = 'cooking_time'

    time_costs = {  # написать функцию вычисления на основе данных
        'fast': 15,
        'normal': 35
    }

    def lookups(self, request, model_admin):
        LABEL_FORMAT_1 = 'до {} мин. ({})'
        LABEL_FORMAT_2 = 'дольше {} мин. ({})'
        recipes = model_admin.get_queryset(request)
        recipes_per_time_costs = {
            key: recipes.filter(cooking_time__lte=value).count()
            for key, value in self.time_costs.items()
        }
        recipes_per_time_costs['slow'] = (
            recipes.count() - recipes_per_time_costs['normal']
        )
        return [
            (value, LABEL_FORMAT_1.format(value, recipes_per_time_costs[key]))
            for key, value in self.time_costs.items()
        ] + [('slow', LABEL_FORMAT_2.format(self.time_costs['normal'],
                                            recipes_per_time_costs['slow']))]

    def queryset(self, request, recipes):
        if self.value() == 'slow':
            return recipes.filter(cooking_time__gt=self.time_costs['normal'])
        if self.value():
            return recipes.filter(cooking_time__lte=self.value())


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Пользователя."""

    list_display = (
        'id',
        'avatar_preview',
        'username',
        'full_name',
        'email',
        'recipes_count',
        'subscriprions_count',
        'subscribers_count',
        'is_staff',
    )
    search_fields = ('email', 'username')
    list_filter = (
        'is_staff',
        RecipesExistsFilter,
        SubcribersExistsFilter,
        SubcriptionsExistsFilter
    ) 
    list_display_links = ('email', 'username')
    list_editable = ('is_staff',)

    @admin.display(description=FULL_NAME_TITLE)
    def full_name(self, object):
        return object.full_name

    @admin.display(description=RECIPES_COUNT_TITLE)
    def recipes_count(self, object):
        return object.recipes.count()

    @admin.display(description=SUBSCRIPTIONS_TITLE)
    def subscriprions_count(self, object):
        return object.subscribers.count()

    @admin.display(description=SUBSCRIBERS_TITLE)
    def subscribers_count(self, object):
        return object.authors.count()

    @mark_safe
    @admin.display(description=AVATAR_TITLE)
    def avatar_preview(self, object):
        avatar = object.avatar
        if avatar:
            return f'<img src="{avatar.url}" style="max-height: 100px;">'
        return EMPTY_AVATAR

    def has_recipes(self):
        return bool(self.recipes_count())


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Подписок."""

    list_display = ('id', 'user', 'author')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Ингредиентов."""

    list_display = ('id', 'name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)

    @admin.display(description=RECIPES_COUNT_TITLE)
    def recipes_count(self, object):  # повторяется
        return object.recipes.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Тегов."""

    list_display = ('id', 'name', 'slug', 'recipes_count')
    list_display_links = ('name', 'slug',)

    @admin.display(description=RECIPES_COUNT_TITLE)
    def recipes_count(self, object):  # повторяется
        return object.recipes.count()


class RecipeIngridientsInline(admin.TabularInline):
    """Представление Ингредиентов в Рецепте."""

    model = RecipeIngridients
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Рецептов."""

    list_display = (
        'id',
        'name',
        'image_preview',
        'get_tags',
        'cooking_time',
        'get_ingredients',
        'author',
        'count_favorites',
    )
    list_display_links = ('name',)
    search_fields = ('author__username', 'author__first_name', 'name')
    list_select_related = ('author',)
    list_filter = ('tags', 'author', RecipesFilter)
    filter_horizontal = ('tags',)
    inlines = (RecipeIngridientsInline,)
    readonly_fields = ('count_favorites',)

    fieldsets = (
        (None, {
            'fields': (
                'count_favorites',
                ('name', 'cooking_time',),
                'author',
                'image',
                'tags',
                'text',
            )
        }),
    )

    @admin.display(description=FAVORITE_RESIPE_TITLE)
    def count_favorites(self, object):
        return object.favorite.count()

    @mark_safe
    @admin.display(description=RECIPE_IMAGE_TITLE)
    def image_preview(self, object):
        return f'<img src="{object.image.url}" style="max-height: 100px;">'

    # наверно нужно оптимизировать и убрать дублирование
    @mark_safe
    @admin.display(description=TAGS_TITLE)
    def get_tags(self, object):
        return ',<br/>'.join([str(tag) for tag in object.tags.all()])

    @mark_safe
    @admin.display(description=INGREDIENTS_TITLE)
    def get_ingredients(self, object):
        return ',<br/>'.join([str(ingredient)
                              for ingredient in object.ingredients.all()])


@admin.register(RecipeIngridients)
class RecipeIngridientsAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Ингредиентов для Рецепта."""

    list_display = ('id', 'recipe', 'ingredient', 'amount',)
    search_fields = ('recipe__name',)
    list_select_related = ('recipe',)


@admin.register(Favorite, ShoppingCart)
class ShoppingCartAndFavoriteAdmin(admin.ModelAdmin):
    """Настройка административной зоны для Списка покупок и Избранного."""

    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'user__first_name',)
    list_select_related = ('user', 'recipe',)
