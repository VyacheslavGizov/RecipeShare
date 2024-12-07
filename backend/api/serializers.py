from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators

# from apps.recipes.models import Recipe
# from apps.users.models import Subscription
from foodgram.models import Recipe, Subscription
import foodgram as recipes_module


User = get_user_model()

NONUNICUE_SUBSCRIPTION_MESSAGE = 'Вы уже подписаны на этого пользователя.'
YOURSELF_SUBSCRIBE_MESSAGE = 'Нельзя быть подписанным на себя.'


class UserSerializer(UserSerializer):
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

    # recipes = serializers.SerializerMethodField()
    # recipes_count = serializers.SerializerMethodField()

    class Meta():
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            # 'recipes',
            # 'recipes_count',
            'avatar',
        )

    # def get_recipes(self, instance):
    #     limit = self.context['request'].GET.get('recipes_limit')
    #     recipes = Recipe.objects.filter(author=instance)
    #     if limit:
    #         recipes = recipes[:int(limit)]
    #     return recipes_module.serializers.ShortRecipeSerializer(recipes,
    #                                                             many=True).data

    # def get_recipes_count(self, instance):
    #     return Recipe.objects.filter(author=instance).count()


class CreateSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания Подписки."""

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
                message=NONUNICUE_SUBSCRIPTION_MESSAGE,
            )
        ]

    def validate_author(self, author):
        if self.context['request'].user == author:
            raise serializers.ValidationError(YOURSELF_SUBSCRIBE_MESSAGE)
        return author

    def to_representation(self, instance):
        return UserInSubscriptionsSerializer(instance.author,
                                             context=self.context).data
