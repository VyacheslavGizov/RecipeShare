from django.db import models

MAX_KEY_LENGTH = 15


class LinkKey(models.Model):
    link = models.CharField(
        'Исходная ссылка',
        max_length=32,
        unique=True
    )
    key = models.CharField(
        'Исходная ссылка',
        max_length=MAX_KEY_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'Пара: ссылка-ключ'
        verbose_name_plural = 'Пары: ссылка-ключ'

    def __str__(self):
        return f'{self.link} - {self.key}'
