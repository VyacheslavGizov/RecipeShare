from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserSerializer

from apps.users.models import Subscription
from .serializer_fields import Base64ImageField


User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор на отображение пользователя."""  # Может назначение изменится

    is_subscribed = serializers.SerializerMethodField()
    # avatar = Base64ImageField()

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
    

# class AvatarSerialiser(serializers.ModelSerializer):
#     """Сериализатор для добавления или удаления аватара."""

#     avatar = Base64ImageField()  # Есть pip install django-extra-fields с Base64ImageField

#     class Meta():
#         model = User
#         fields = ['avatar',]

