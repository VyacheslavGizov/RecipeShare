from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngridients,
    ShoppingCart,
    Tag,
)


admin.site.empty_value_display = 'Не задано'

INGREDIENT_SEARCH_HELP_TEXT = 'Поиск по полям: "НАЗВАНИЕ"'
RECIPE_SEARCH_HELP_TEXT = 'Поиск по: "ИМЯ ПОЛЬЗОВАТЕЛЯ", "НАЗВАНИЕ РЕЦЕПТА"'
RECIPE_DISPLAY_MESSAGE = 'Пользователей добавило в "Избранное"'
RECIPE_INGREDIENTS_SEARCH_HELP_TEXT = 'Поиск по полям: "НАЗВАНИЕ РЕЦЕПТА"'
SHOPING_CART_FAVORITE_SEARCH_HELP_TEXT = ('Поиск по: "ИМЯ_ПОЛЬЗОВАТЕЛЯ", '
                                          '"РЕЦЕПТ"')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Ингредиентов."""

    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)
    search_help_text = INGREDIENT_SEARCH_HELP_TEXT


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Тегов."""

    list_display = ('id', 'name', 'slug', 'color')
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
    search_help_text = RECIPE_SEARCH_HELP_TEXT
    list_select_related = ('author',)
    list_filter = ('tags', 'ingredients')
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
        return object.favorite_records.count()


@admin.register(RecipeIngridients)
class RecipeIngridientsAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Ингредиентов для Рецепта."""

    list_display = ('id', 'recipe', 'ingredient', 'amount',)
    search_fields = ('recipe__name',)
    search_help_text = RECIPE_INGREDIENTS_SEARCH_HELP_TEXT
    list_select_related = ('recipe',)


@admin.register(Favorite, ShoppingCart)
class ShoppingCartAndFavoriteAdmin(admin.ModelAdmin):
    """Настройка административной зоны для Списка покупок и Избранного."""

    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'user__first_name',)
    search_help_text = SHOPING_CART_FAVORITE_SEARCH_HELP_TEXT
    list_select_related = ('user', 'recipe',)
