from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from apps.users.models import Subscription


User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор на отображение пользователя."""  # Может назначение изменится

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(allow_null=True)

    class Meta():
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'avatar',
        ]
    
    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated and
                Subscription.objects.filter(user=user, author=obj).exists())


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватарки"""

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)

