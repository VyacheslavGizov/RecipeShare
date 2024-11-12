from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

from constants import DESCRIPTION_LENGTH_LIMIT


class CustomUser(AbstractUser):
    """Модель пользователя."""

    # Администратор будет реализован через is_staff,
    
    # добавил, потому что в AbstractUser они могут быть пустыми
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    email = models.EmailField('E-mail', max_length=254, unique=True)
    avatar = models.ImageField(
        'Аватар',
        upload_to='users_avatars/',
        blank=True,
        null=True
        # сделать дефолтную аватарку как в киттиграме
    )
    # username задан в AbstractUser

    # def_get_full_name(self):
    #    return f'{self.first_name self.second_name}'
    # можно использовать что-то подобное, если будет необходимо

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return (
            f'{self.first_name[:DESCRIPTION_LENGTH_LIMIT]} '
            f'{self.last_name[:DESCRIPTION_LENGTH_LIMIT]} | '
            f'{self.username[:DESCRIPTION_LENGTH_LIMIT]} | '
            f'{self.email}'
        )


User = get_user_model()


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользватель'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписан на автора'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),  # почитать еще про F-объекты
                name='unsubcribe_to_yourself',
                violation_error_message='Пользователь не может быть подписан на себя.'
            )
        ]

    def __str__(self):
        return (f'{self.user} - подписан на: {self.author}')
