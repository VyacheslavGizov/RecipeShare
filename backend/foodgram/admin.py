from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from .filters import (CookingTimeFilter, RecipesExistsFilter,
                      SubcribersExistsFilter, SubcriptionsExistsFilter)
from .models import (Favorite, Ingredient, Recipe, RecipeIngridients,
                     ShoppingCart, Subscription, Tag)


AVATAR_TITLE = 'Аватар'
EMPTY_AVATAR = 'Не задан'
FAVORITE_RESIPE_TITLE = 'раз в Избранном'
FULL_NAME_TITLE = 'Имя_фамилия'
INGREDIENTS_TITLE = 'Продукты'
RECIPE_IMAGE_TITLE = 'Фото блюда'
RECIPES_COUNT_TITLE = 'Рецептов'
SUBSCRIBERS_TITLE = 'Подписчиков'
SUBSCRIPTIONS_TITLE = 'Подписок'
TAGS_TITLE = 'Теги'

User = get_user_model()

admin.site.unregister(Group)


class RecipesCountBaseAdmin(admin.ModelAdmin):

    @admin.display(description=RECIPES_COUNT_TITLE)
    def recipes_count(self, object):
        return object.recipes.count()


@admin.register(User)
class UserAdmin(RecipesCountBaseAdmin):
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
        SubcriptionsExistsFilter,
    )
    list_display_links = ('email', 'username')
    list_editable = ('is_staff',)

    @admin.display(description=FULL_NAME_TITLE)
    def full_name(self, object):
        return object.full_name

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
class IngredientAdmin(RecipesCountBaseAdmin):
    """Настройка административной зоны для модели Ингредиентов."""

    list_display = ('id', 'name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


@admin.register(Tag)
class TagAdmin(RecipesCountBaseAdmin):
    """Настройка административной зоны для модели Тегов."""

    list_display = ('id', 'name', 'slug', 'recipes_count')
    list_display_links = ('name', 'slug',)


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
    list_filter = ('tags', 'author', CookingTimeFilter)
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

    @mark_safe
    @admin.display(description=TAGS_TITLE)
    def get_tags(self, object):
        return self.display_description_objects(object.tags.all())

    @mark_safe
    @admin.display(description=INGREDIENTS_TITLE)
    def get_ingredients(self, object):
        return self.display_description_objects(object.ingredients.all())

    def display_description_objects(self, objects):
        return ',<br/>'.join([str(object) for object in objects])


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
