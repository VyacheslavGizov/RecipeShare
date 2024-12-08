from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as BaseUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators

from foodgram.models import Recipe, Subscription


User = get_user_model()

NONUNICUE_SUBSCRIPTION_MESSAGE = 'Вы уже подписаны на этого пользователя.'
YOURSELF_SUBSCRIBE_MESSAGE = 'Нельзя быть подписанным на себя.'


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

    avatar = Base64ImageField()  # в рецептах это поле указано как лишнее

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
