from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from apps.recipes import models
from api.v1.users.serializers import CustomUserSerializer


READD_RECIPE_MESSAGE = 'Рецепт уже добавлен.'
ADD_INGREDIENTS_MESSAGE = 'Добавьте ингредиенты.'
NONUNICUE_INGREDIENTS_MESSAGE = 'Все ингредиенты должны быть уникальными.'
ADD_TAGS_MESSAGE = 'Добавьте один или несколько тегов.'
NONUNICUE_TAGS_MESSAGE = 'Все теги должны быть уникальными.'
ADD_IMAGE_MESSAGE = 'Добавьте фото рецепта.'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для Тегов."""

    class Meta:
        model = models.Tag
        fields = ('id', 'name', 'slug')


class IngredientSerialiser(serializers.ModelSerializer):
    """Сериализатор для списка Ингредиентов."""

    class Meta:
        model = models.Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientForRecipeSerialiser(serializers.ModelSerializer):
    """Сериализатор для отображения Ингредиента в Рецепте."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = models.RecipeIngridients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ReadRecipeSerialiser(serializers.ModelSerializer):
    """Сериализатор для списка Рецептов."""

    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = IngredientForRecipeSerialiser(
        source='recipe_ingridients', many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = models.Recipe
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
        return self.is_user_chosen_recipe(models.Favorite, instance)

    def get_is_in_shopping_cart(self, instance):
        return self.is_user_chosen_recipe(models.ShoppingCart, instance)

    def is_user_chosen_recipe(self, model, instance):
        user = self.context['request'].user
        return (
            user.is_authenticated and
            model.objects.filter(user=user, recipe=instance).exists()
        )


class AddIngredientForRecipeSerialiser(serializers.ModelSerializer):
    """Сериализатор для добавления Ингредиента в Рецепт."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=models.Ingredient.objects.all(),
    )

    class Meta:
        model = models.RecipeIngridients
        fields = ('id', 'amount')


class CreateUpdateRecipeSerialiser(serializers.ModelSerializer):
    """Сериализатор для создания/изменения Рецепта."""

    ingredients = AddIngredientForRecipeSerialiser(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=models.Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=True, allow_null=False)
    author = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = models.Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author',
        )

    def validate_ingredients(self, ingredients):
        if not ingredients or not all(ingredients):
            raise serializers.ValidationError(ADD_INGREDIENTS_MESSAGE)
        if len(ingredients) != len(set(
            [ingredient['id'] for ingredient in ingredients]
        )):
            raise serializers.ValidationError(NONUNICUE_INGREDIENTS_MESSAGE)
        return ingredients

    def validate_tags(self, tags):
        if not tags or not all(tags):
            raise serializers.ValidationError(ADD_TAGS_MESSAGE)
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(NONUNICUE_TAGS_MESSAGE)
        return tags

    def validate_image(self, image):
        if image is None:
            raise serializers.ValidationError(ADD_IMAGE_MESSAGE)
        return image

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = models.Recipe.objects.create(**validated_data)
        return self.add_ingredients_and_tags(recipe, tags, ingredients)

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        return self.add_ingredients_and_tags(instance, tags, ingredients)

    @staticmethod
    def add_ingredients_and_tags(recipe, tags, ingredients):
        recipe.tags.set(tags)
        recipe.save()
        models.RecipeIngridients.objects.bulk_create(
            models.RecipeIngridients(
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
                recipe=recipe
            ) for ingredient in ingredients
        )
        return recipe

    def to_representation(self, instance):
        return ReadRecipeSerialiser(instance, context=self.context).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор короткого представления Рецепта."""

    class Meta:
        model = models.Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class AddRecipeInShopingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления Рецепта в Список покупок."""

    class Meta:
        model = models.ShoppingCart
        fields = ('user', 'recipe')
        read_only_fields = ('user',)

    def validate(self, attrs):
        user = self.context['request'].user
        if self.Meta.model.objects.filter(
            recipe=attrs['recipe'], user=user
        ).exists():
            raise serializers.ValidationError(READD_RECIPE_MESSAGE)
        attrs['user'] = user
        return attrs

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data


class AddRecipeInFavoriteSerializer(AddRecipeInShopingCartSerializer):
    """Сериализатор для добавления Рецепта в Избранное."""

    class Meta(AddRecipeInShopingCartSerializer.Meta):
        model = models.Favorite
