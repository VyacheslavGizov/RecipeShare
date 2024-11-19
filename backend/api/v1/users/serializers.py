from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from apps.users.models import Subscription


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


class SubscriptionSerialiser(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = '__all__'
        depth = 1
