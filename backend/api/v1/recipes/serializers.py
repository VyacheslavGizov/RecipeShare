from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from apps.recipes import models


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
