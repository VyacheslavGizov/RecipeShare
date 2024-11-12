from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserSerializer

from apps.users.models import Subscription


User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор на отображение пользователя."""  # Может назначение изменится

    is_subscribed = serializers.SerializerMethodField()

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
