from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from apps.recipes import models
from api.v1.users import serializers as user_serialisers


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для списка Тегов."""

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
            models.ShopingCart.objects.filter(user=user, recipe=instance).exists()
        )


class ShortIngredientForRecipeSerialiser(serializers.ModelSerializer):
    """Сериализатор для добавления Ингредиента в Рецепт."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=models.Ingredient.objects.all()  # Потому что работаю на запись
    )
    # amount cам должен создаться

    class Meta:
        model = models.RecipeIngridients
        fields = ('id', 'amount')


class CreateUpdateRecipeSerialiser(serializers.ModelSerializer):
    """Сериализатор для создания/изменения рецепта."""

    ingredients = ShortIngredientForRecipeSerialiser(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=models.Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

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
    
    def to_representation(self, instance):
        # нужно чтобы при вызове во вьюсет serializer.data было правильное отображение
        # контекст передаю, потому что поля к методам привязанные от него рабтают
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
