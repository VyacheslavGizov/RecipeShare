from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Subscription


# Донастроить по-нормальному когда будут данные
User = get_user_model()

admin.site.empty_value_display = 'Не задано'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Пользователя."""

    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff'
    )
    search_fields = ('email', 'username')
    search_help_text = 'Поиск по полям: "ИМЯ ПОЛЬЗОВАТЕЛЯ", "E-MAIL"'
    list_filter = ('is_staff',)
    list_display_links = ('email', 'username')
    list_editable = ('is_staff',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настройка административной зоны для модели Подписок."""

    list_display = ('id', 'user', 'author')
