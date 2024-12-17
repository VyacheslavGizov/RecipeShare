from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from django.urls import reverse

from .filters import (
    CookingTimeFilter,
    RecipesExistsFilter,
    SubcribersExistsFilter,
    SubcriptionsExistsFilter,
)
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

admin.site.unregister(Group)


class RecipesCountBaseAdmin(admin.ModelAdmin):

    @admin.display(description='Рецептов')
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
        RecipesExistsFilter,
        SubcribersExistsFilter,
        SubcriptionsExistsFilter,
    )
    list_display_links = ('email', 'username')
    list_editable = ('is_staff',)

    @mark_safe
    @admin.display(description='Рецептов')
    def recipes_count(self, user):
        model = Recipe
        count = super().recipes_count(user)
        return (
            u'<a href="{}?author__id__exact={}">{}</a>'.format(
                reverse('admin:{}_{}_changelist'.format(
                    model._meta.app_label,
                    model._meta.model_name)
                ),
                user.pk,
                count
            ) if count else count
        )

    @admin.display(description='Имя_фамилия')
    def full_name(self, user):
        return user.full_name

    @admin.display(description='Подписок')
    def subscriprions_count(self, user):
        return user.subscribers.count()

    @admin.display(description='Подписчиков')
    def subscribers_count(self, user):
        return user.authors.count()

    @mark_safe
    @admin.display(description='Аватар')
    def avatar_preview(self, user):
        avatar = user.avatar
        return (
            f'<img src="{avatar.url}" style="max-height: 100px;">'
            if user.avatar else ''
        )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Подписок."""

    list_display = ('id', 'user', 'author')


@admin.register(Ingredient)
class IngredientAdmin(RecipesCountBaseAdmin):
    """Настройка административной зоны для модели Продуктов."""

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

    fieldsets = (
        (None, {
            'fields': (
                ('name', 'cooking_time',),
                'author',
                'image',
                'tags',
                'text',
            )
        }),
    )

    @admin.display(description='раз в Избранном')
    def count_favorites(self, recipe):
        return recipe.favorites.count()

    @mark_safe
    @admin.display(description='Фото блюда')
    def image_preview(self, recipe):
        return f'<img src="{recipe.image.url}" style="max-height: 100px;">'

    @mark_safe
    @admin.display(description='Теги')
    def get_tags(self, recipe):
        return self.display_description_objects(recipe.tags.all())

    @mark_safe
    @admin.display(description='Продукты')
    def get_ingredients(self, recipe):
        return self.display_description_objects(
            recipe.recipe_ingridients.all()
        )

    def display_description_objects(self, objects):
        return ',<br/>'.join([str(object) for object in objects])


@admin.register(RecipeIngridients)
class RecipeIngridientsAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Продуктов для Рецепта."""

    list_display = ('id', 'recipe', 'ingredient', 'amount',)
    search_fields = ('recipe__name',)
    list_select_related = ('recipe',)


@admin.register(Favorite, ShoppingCart)
class ShoppingCartAndFavoriteAdmin(admin.ModelAdmin):
    """Настройка административной зоны для Списка покупок и Избранного."""

    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'user__first_name',)
    list_select_related = ('user', 'recipe',)
