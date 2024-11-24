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


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройка административной зоны для Ингредиентов"""

    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)
    search_help_text = 'Поиск по полям: "НАЗВАНИЕ"'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройка административной зоны для Тегов"""

    list_display = ('id', 'name', 'slug', 'color')
    list_display_links = ('name', 'slug',)


class RecipeIngridientsInline(admin.TabularInline):
    """Представление Ингредиентов в Рецепте"""

    model = RecipeIngridients
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройка административной зоны для Рецептов"""

    list_display = ('id', 'name', 'count_favorites', 'author',)
    list_display_links = ('name',)
    search_fields = ('author__username', 'author__first_name', 'name')
    search_help_text = (
        'Поиск по: "ИМЯ ПОЛЬЗОВАТЕЛЯ", '
        '"НАЗВАНИЕ РЕЦЕПТА"'
    )
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

    @admin.display(description='Пользователей добавило в "Избранное"')
    def count_favorites(self, object):
        return object.favorite_records.count()


@admin.register(RecipeIngridients)
class RecipeIngridientsAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Рецпт-Ингредиент"""

    list_display = ('id', 'recipe', 'ingredient', 'amount',)
    search_fields = ('recipe__name',)
    search_help_text = 'Поиск по полям: "НАЗВАНИЕ РЕЦЕПТА"'
    list_select_related = ('recipe',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Настройка административной зоны для Cписка покупок"""

    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'user__first_name',)
    search_help_text = 'Поиск по полям: "ПОЛЬЗОВАТЕЛЬ", "РЕЦЕПТ"'
    list_select_related = ('user', 'recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Настройка административной зоны для Избранного"""

    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'user__first_name',)
    search_help_text = 'Поиск по полям: "ПОЛЬЗОВАТЕЛЬ", "РЕЦЕПТ"'
    list_select_related = ('user', 'recipe',)
