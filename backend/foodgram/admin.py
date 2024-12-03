from django.contrib import admin
from django.contrib.auth import get_user_model

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

admin.site.empty_value_display = 'Не задано'
RECIPE_DISPLAY_MESSAGE = 'Пользователей добавило в "Избранное"'
FULL_NAME_TITLE = 'Имя_фамилия'
RECIPES_COUNT_TITLE = 'Рецептов'
SUBSCRIBERS_TITLE = 'Подписчиков'
SUBSCRIPTIONS_TITLE = 'Подписок'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Пользователя."""

    list_display = (
        'id',
        'username',
        'full_name',
        'email',
        'is_staff',
        'recipes_count',
        'subscriprions_count',
        'subscribers_count',
    )
    search_fields = ('email', 'username')
    list_filter = ('is_staff',)
    list_display_links = ('email', 'username')
    list_editable = ('is_staff',)

    @admin.display(description=FULL_NAME_TITLE)
    def full_name(self, object):
        return object.full_name

    @admin.display(description=RECIPES_COUNT_TITLE)
    def recipes_count(self, object):
        return object.number_of_recipes

    @admin.display(description=SUBSCRIPTIONS_TITLE)
    def subscriprions_count(self, object):
        return object.number_of_subscriptions

    @admin.display(description=SUBSCRIBERS_TITLE)
    def subscribers_count(self, object):
        return object.number_of_subscribers


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Подписок."""

    list_display = ('id', 'user', 'author')


admin.site.empty_value_display = 'Не задано'

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Ингредиентов."""

    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Тегов."""

    list_display = ('id', 'name', 'slug',)
    list_display_links = ('name', 'slug',)


class RecipeIngridientsInline(admin.TabularInline):
    """Представление Ингредиентов в Рецепте."""

    model = RecipeIngridients
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Рецептов."""

    list_display = ('id', 'name', 'count_favorites', 'author',)
    list_display_links = ('name',)
    search_fields = ('author__username', 'author__first_name', 'name')
    list_select_related = ('author',)
    list_filter = ('tags', 'author')
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

    @admin.display(description=RECIPE_DISPLAY_MESSAGE)
    def count_favorites(self, object):
        return object.favorite.count()


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

