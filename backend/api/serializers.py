from collections import Counter

from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as BaseUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators

from foodgram.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngridients,
    ShoppingCart,
    Subscription,
    Tag,
    MIN_AMMOUNT
)


User = get_user_model()

NONUNICUE_SUBSCRIPTION_MESSAGE = 'Вы уже подписаны на этого пользователя.'
YOURSELF_SUBSCRIBE_MESSAGE = 'Нельзя быть подписанным на себя.'

READD_RECIPE_MESSAGE = 'Рецепт уже добавлен.'
ADD_INGREDIENTS_MESSAGE = 'Добавьте ингредиенты.'
NONUNIQUE_INGREDIENTS_MESSAGE = 'Найдены повторяющиеся продукты: {duplicates}.'
ADD_TAGS_MESSAGE = 'Добавьте один или несколько тегов.'
NONUNIQUE_TAGS_MESSAGE = 'Найдены повторяющиеся теги: {duplicates}.'
ADD_IMAGE_MESSAGE = 'Добавьте фото рецепта.'


class UserSerializer(BaseUserSerializer):
    """Сериализатор для работы с моделью Пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta():
        model = User
        fields = BaseUserSerializer.Meta.fields + (
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, instance):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Subscription.objects.filter(user=user,
                                            author=instance).exists()
        )


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления/удаления аватарки Пользователя."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class UserInSubscriptionsSerializer(UserSerializer):
    """Сериализатор для представления Пользователя в Подписках."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta():
        model = User
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, instance):
        return ShortRecipeSerializer(
            Recipe.objects.filter(author=instance)[:int(
                self.context['request'].GET.get('recipes_limit', 10**10))],
            many=True
        ).data

    def get_recipes_count(self, instance):
        return Recipe.objects.filter(author=instance).count()


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор сокращенного Рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для Тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerialiser(serializers.ModelSerializer):
    """Сериализатор для списка Ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientForRecipeSerialiser(serializers.ModelSerializer):
    """Сериализатор для отображения Ингредиента в Рецепте."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngridients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ReadRecipeSerialiser(serializers.ModelSerializer):
    """Сериализатор для списка Рецептов."""

    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientForRecipeSerialiser(
        source='recipe_ingridients', many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    # image = Base64ImageField()  # лишнее поле

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, instance):
        return self.is_user_chosen_recipe(Favorite, instance)

    def get_is_in_shopping_cart(self, instance):
        return self.is_user_chosen_recipe(ShoppingCart, instance)

    def is_user_chosen_recipe(self, model, instance):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and model.objects.filter(user=user, recipe=instance).exists()
        )


class AddIngredientInRecipeSerialiser(serializers.ModelSerializer):
    """Сериализатор для добавления Ингредиента в Рецепт."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField(min_value=MIN_AMMOUNT)

    class Meta:
        model = RecipeIngridients
        fields = ('id', 'amount')


class WriteRecipeSerialiser(serializers.ModelSerializer):
    """Сериализатор для создания/изменения Рецепта."""

    ingredients = AddIngredientInRecipeSerialiser(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True
    )
    image = Base64ImageField()
    author = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault(),)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author',
        )

    def get_duplicates_info(self, elements):
        return ';'.join([
            f'{element} ({count})'
            for element, count in dict(Counter(elements)).items()
            if count > 1
        ])

    def validate_ingredients(self, recipe_ingredients):
        if not recipe_ingredients or not all(recipe_ingredients):
            raise serializers.ValidationError(ADD_INGREDIENTS_MESSAGE)
        ingredients = [ingredient['id'] for ingredient in recipe_ingredients]
        if len(recipe_ingredients) != len(set(ingredients)):
            raise serializers.ValidationError(
                NONUNIQUE_INGREDIENTS_MESSAGE.format(
                    duplicates=self.get_duplicates_info(ingredients)
                ))
        return recipe_ingredients

    def validate_tags(self, tags):
        if not tags or not all(tags):
            raise serializers.ValidationError(ADD_TAGS_MESSAGE)
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(NONUNIQUE_TAGS_MESSAGE.format(
                duplicates=self.get_duplicates_info(tags)
            ))
        return tags

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(ADD_IMAGE_MESSAGE)
        return image

    def create(self, validated_data):
        tags, ingredients = self.extract_tags_and_ingredients(validated_data)
        recipe = super().create(validated_data)
        return self.add_ingredients_and_tags(recipe, tags, ingredients)

    def update(self, instance, validated_data):  # проверить, работает ли в приложении обновление
        tags, ingredients = self.extract_tags_and_ingredients(validated_data)
        instance.ingredients.clear()
        return self.add_ingredients_and_tags(
            super().update(instance, validated_data),
            tags,
            ingredients
        )

    @staticmethod
    def extract_tags_and_ingredients(validated_data):
        return (validated_data.pop('tags'), validated_data.pop('ingredients'))

    @staticmethod
    def add_ingredients_and_tags(recipe, tags, ingredients):
        recipe.tags.set(tags)
        RecipeIngridients.objects.bulk_create(
            RecipeIngridients(
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
                recipe=recipe
            ) for ingredient in ingredients
        )
        return recipe

    def to_representation(self, instance):
        return ReadRecipeSerialiser(instance, context=self.context).data
