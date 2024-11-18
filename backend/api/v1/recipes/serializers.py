from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from apps.recipes import models
from api.v1.users import serializers as user_serialisers
from api.utils import request_in_serializer_context



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


class RecipeListSerialiser(serializers.ModelSerializer):
    """Сериализатор для списка рецептов."""

    tags = TagSerializer(many=True)
    author = user_serialisers.CustomUserSerializer()
    # передаю как источник ингредиент из RecipeIngridients через related_name
    ingredients = IngredientForRecipeSerialiser(source='recipe_ingridients',
                                                many=True)
    is_favorite = serializers.SerializerMethodField()
    in_shoping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorite',
            'in_shoping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
    
    # DRY
    def get_is_favorite(self, instance):
        # такая же проверка в CustomUserSerializer.get_is_subscribed
        # можно переписать в общем виде через передачу кверисета для поиска в списке
        # и добавить в служебные функции может быть 
        request = self.context.get('request', None)  # на случай, если get_serializer_context() не передаст запрос
        if request is None:
            return False
        user = request.user
        return (
            user.is_authenticated and
            models.Favorite.objects.filter(user=user, recipe=instance).exists()
        )

    def get_in_shoping_cart(self, instance):
        request = self.context.get('request', None)
        if request is None:
            return False
        user = request.user
        return (
            user.is_authenticated and
            models.ShopingCart.objects.filter(user=user, recipe=instance).exists()
        )

