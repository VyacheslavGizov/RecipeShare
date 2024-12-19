from collections import Counter

from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as BaseUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Favorite,
    Ingredient,
    MIN_AMOUNT,
    Recipe,
    RecipeIngridients,
    ShoppingCart,
    Subscription,
    Tag,
)


User = get_user_model()


ADD_IMAGE_MESSAGE = 'Добавьте фото рецепта.'
NOT_ITEMS_MESSAGE = 'Данные не указаны.'
NONUNICUE_SUBSCRIPTION_MESSAGE = 'Вы уже подписаны на этого пользователя.'
NONUNIQUE_ITEMS_MESSAGE = 'Обнаружены повторы: {duplicates}.'
READD_RECIPE_MESSAGE = 'Рецепт уже добавлен.'
YOURSELF_SUBSCRIBE_MESSAGE = 'Нельзя быть подписанным на себя.'


class UserSerializer(BaseUserSerializer):
    """Сериализатор для работы с моделью Пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta():
        model = User
        fields = (
            *BaseUserSerializer.Meta.fields,
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, instance):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Subscription.objects.filter(
                user=user,
                author=instance
            ).exists()
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
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    class Meta():
        model = User
        fields = (
            *UserSerializer.Meta.fields,
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, instance):
        return ShortRecipeSerializer(
            instance.recipes.all()[:int(
                self.context['request'].GET.get('recipes_limit', 10**10))],
            many=True
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор сокращенного Рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для Тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerialiser(serializers.ModelSerializer):
    """Сериализатор для списка Продуктов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientForRecipeSerialiser(serializers.ModelSerializer):
    """Сериализатор для отображения Продукта в Рецепте."""

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
        source='recipe_ingridients',
        many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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
        read_only_fields = fields

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
    """Сериализатор для добавления Продукта в Рецепт."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField(min_value=MIN_AMOUNT)

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

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def get_duplicates_info(self, items):
        return ','.join(
            str(item) for item, count in Counter(items).items()
            if count > 1
        )

    def unique_or_validation_error(self, items):
        if not items:
            raise serializers.ValidationError(NOT_ITEMS_MESSAGE)
        if len(items) != len(set(items)):
            raise serializers.ValidationError(NONUNIQUE_ITEMS_MESSAGE.format(
                duplicates=self.get_duplicates_info(items)))

    def validate_ingredients(self, ingredients):
        self.unique_or_validation_error(
            items=[ingredient['id'] for ingredient in ingredients]
        )
        return ingredients

    def validate_tags(self, tags):
        self.unique_or_validation_error(items=tags)
        return tags

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(ADD_IMAGE_MESSAGE)
        return image

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        self.add_ingredients_and_tags(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', instance.tags)
        ingredients = validated_data.pop('ingredients', instance.ingredients)
        instance.ingredients.clear()
        self.add_ingredients_and_tags(instance, tags, ingredients)
        return super().update(instance, validated_data)

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

    def to_representation(self, instance):
        return ReadRecipeSerialiser(instance, context=self.context).data
