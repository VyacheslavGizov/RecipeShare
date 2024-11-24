from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators

from apps.users.models import Subscription
from apps.recipes.models import Recipe
import api.v1.recipes as recipes_module



User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор для работы с моделью Пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta():
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'avatar',
        )
        read_only_fields = ('id',)

    def get_is_subscribed(self, instance):
        user = self.context['request'].user
        return (
            user.is_authenticated and
            Subscription.objects.filter(user=user, author=instance).exists()
        )


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления/удаления аватарки Пользователя."""

    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ('avatar',)


class UserInSubscriptionsSerializer(CustomUserSerializer): # допилить, оптимизировать, что на чтение туда-сюда
    """Сериализатор для представления пользователя в подписках."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta():
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )
        read_only_fields = ('id',)

    def get_recipes(self, instance):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit') # разобраться
        recipes = Recipe.objects.filter(author=instance) # # разобраться
        if limit and limit.isdigit(): # разобраться
            recipes = recipes[:int(limit)] # разобраться
        return recipes_module.serializers.ShortRecipeSerializer(recipes, many=True).data
    
    def get_recipes_count(self, instance):
        return Recipe.objects.filter(author=instance).count()


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки."""

    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Subscription
        fields = ('author', 'user')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('author', 'user'),
                message='Вы уже подписаны на этого пользователя',
            )
        ]

    def validate_author(self, author):
        if self.context['request'].user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return author

    def to_representation(self, instance):
        return UserInSubscriptionsSerializer(instance.author, context=self.context).data
