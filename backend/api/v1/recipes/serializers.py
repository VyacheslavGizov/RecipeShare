from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from apps.recipes import models
from api.v1.users import serializers as user_serialisers


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
        # прописать ограничение из модели, оно не подтянулось


class IngredientForRecipeSerialiser(serializers.ModelSerializer):
    """Сериализатор для модели Ингредиента для отображения в Рецептах."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = models.RecipeIngridients
        fields = ('id', 'name', 'measurement_unit', 'amount')
        # прописать ограничение из модели, оно не подтянулось, если сериализатор для записи


class ReadRecipeSerialiser(serializers.ModelSerializer):
    """Сериализатор для списка рецептов."""

    tags = TagSerializer(many=True)
    author = user_serialisers.CustomUserSerializer()
    # передаю как источник ингредиент из RecipeIngridients через related_name
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
    
    # DRY
    def get_is_favorited(self, instance):
        user = self.context['request'].user
        return (
            user.is_authenticated and
            models.Favorite.objects.filter(user=user, recipe=instance).exists()
        )

    def get_is_in_shopping_cart(self, instance):
        user = self.context['request'].user
        return (
            user.is_authenticated and
            models.ShoppingCart.objects.filter(user=user, recipe=instance).exists()
        )


class ShortIngredientForRecipeSerialiser(serializers.ModelSerializer):
    """Сериализатор для добавления Ингредиента в Рецепт."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=models.Ingredient.objects.all(),  # Потому что работаю на запись
    )
    # amount cам должен создаться

    class Meta:
        model = models.RecipeIngridients
        fields = ('id', 'amount')


class CreateUpdateRecipeSerialiser(serializers.ModelSerializer):
    """Сериализатор для создания/изменения рецепта."""

    ingredients = ShortIngredientForRecipeSerialiser(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=models.Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
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
    
    # возможно написать отдельный валидатор универсальный и его использовать прям в полях
    def validate_ingredients(self, ingredients):
        if not ingredients or not all(ingredients):
            raise serializers.ValidationError('Добавьте ингридиенты.')
        if len(ingredients) != len(set(
            [ingredient['id'] for ingredient in ingredients]
        )):
            raise serializers.ValidationError('Все ингредиенты должны быть уникальными.')
        return ingredients
        
    def validate_tags(self, tags):
        if not tags or not all(tags):
            raise serializers.ValidationError('Добавьте один или несколько тегов.')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Все теги должны быть уникальными.')
        return tags
        
    def validate_image(self, image):
        if image is None:
            raise serializers.ValidationError('Добавьте фото рецепта.')
        return image
    
    def to_representation(self, instance):
        return ReadRecipeSerialiser(instance, context=self.context).data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = models.Recipe.objects.create(**validated_data)
        # добавляет записи в число связанных с текущей, перезаписывая прошлые
        # на случай обновления тегов использую для встроенной связи()
        recipe.tags.set(tags)
        recipe.save()
        # делаю запись связанных моделей руками
        models.RecipeIngridients.objects.bulk_create(
            models.RecipeIngridients(
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
                recipe=recipe
            ) for ingredient in ingredients
        )
        return recipe  # почему нужно вернуть запись

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.ingredients.clear()
        models.RecipeIngridients.objects.bulk_create(
            models.RecipeIngridients(
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
                recipe=instance
            ) for ingredient in ingredients
        )
        super().update(instance, validated_data)
        return instance  # вроде внутри update
    

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
        # extra_kwargs = {'user': {'read_only': True}}

    def validate(self, attrs):
        user = self.context['request'].user
        if models.ShoppingCart.objects.filter(
            recipe=attrs['recipe'], user=user
        ).exists():
            raise serializers.ValidationError('Рецепт уже добавлен в Список покупок.')
        attrs['user'] = user
        return attrs

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data


class AddRecipeInFavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления Рецепта в Избранное."""

    class Meta:
        model = models.Favorite
        fields = ('user', 'recipe')
        read_only_fields = ('user',)
        # extra_kwargs = {'user': {'read_only': True}}

    def validate(self, attrs):
        user = self.context['request'].user
        if models.Favorite.objects.filter(
            recipe=attrs['recipe'], user=user
        ).exists():
            raise serializers.ValidationError('Рецепт уже добавлен в Избранное.')
        attrs['user'] = user
        return attrs

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data
