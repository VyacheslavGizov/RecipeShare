from secrets import token_urlsafe

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


TAG_HELP_TEXT = 'Выберите один или несколько тегов.'
INGREDIENT_HELP_TEXT = 'Укажите необходимые продукты.'
DESCRIPTION_LENGTH_LIMIT = 20
MIN_AMOUNT = 1
MIN_COOKING_TIME = 1
MAX_LINK_LENGTH = 5
LENGTH_IN_BYTES = 2


def get_link():
    return token_urlsafe(LENGTH_IN_BYTES)
# def get_link():
#     alphabet = ''.join([string.ascii_letters, string.digits])
#     return ''.join(random.choice(alphabet) for _ in range(MAX_LINK_LENGTH))


class User(AbstractUser):
    """Модель Пользователя."""

    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    email = models.EmailField('Электронная почта', max_length=254, unique=True)
    avatar = models.ImageField(
        'Аватар',
        upload_to='users_avatars/',
        blank=True,
        null=True
    )
    username = models.CharField(
        'Псевдоним',
        max_length=150,
        unique=True,
        validators=[RegexValidator(regex=r'^[\w.@+-]+\Z')]
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return (
            f'{self.first_name[:DESCRIPTION_LENGTH_LIMIT]} '
            f'{self.last_name[:DESCRIPTION_LENGTH_LIMIT]} | '
            f'{self.username[:DESCRIPTION_LENGTH_LIMIT]}'
        )


User = get_user_model()


class Subscription(models.Model):
    """Модель Подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Пользватель'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Автор'
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
                check=~models.Q(author=models.F('user')),
                name='unsubscribe_to_yourself',
            )
        ]

    def __str__(self):
        return f'{self.user} - подписан на: {self.author}'


class Tag(models.Model):
    """Модель Тега."""

    name = models.CharField('Название', max_length=32, unique=True,)
    slug = models.SlugField(
        'Метка',
        max_length=32,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} | {self.slug}'


class Ingredient(models.Model):
    """Модель Продукта."""

    name = models.CharField('Название', max_length=128, db_index=True,)
    measurement_unit = models.CharField('Единица измерения', max_length=64,)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_measurement_unit',
            )
        ]

    def __str__(self):
        return (f'{self.name[:DESCRIPTION_LENGTH_LIMIT]} '
                f'({self.measurement_unit})')


class Recipe(models.Model):
    """Модель Рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text='Автор',
        verbose_name='Автор',
    )
    name = models.CharField('Название', max_length=256,)
    image = models.ImageField('Фото блюда', upload_to='recipes_images/',)
    text = models.TextField('Описание', max_length=2200,)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngridients',
        verbose_name='Продукты',
        help_text=INGREDIENT_HELP_TEXT
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text=TAG_HELP_TEXT
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления, мин.',
        validators=[MinValueValidator(MIN_COOKING_TIME)],
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ('-pub_date', 'name')

    def __str__(self):
        return (
            f'{self.name[:DESCRIPTION_LENGTH_LIMIT]}: '
            f'{self.cooking_time} мин. - {self.author}'
        )


class RecipeIngridients(models.Model):
    """Продукты для Рецепта - промежуточная модель."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        verbose_name='Продукт'
    )
    amount = models.PositiveSmallIntegerField(
        'Мера',
        validators=[MinValueValidator(MIN_AMOUNT)],
    )

    class Meta:
        verbose_name = 'Продукты для рецепта'
        verbose_name_plural = 'Продукты для рецепта'
        default_related_name = 'recipe_ingridients'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient', ],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.ingredient}: {self.amount}'


class UserAndRecipeModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        default_related_name = '%(class)ss'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe', ],
                name='unique_users_%(class)s_records'
            )
        ]

    def __str__(self):
        return (
            f'{self.user}: '
            f'({self.recipe.__str__()[:DESCRIPTION_LENGTH_LIMIT]})'
        )


class Favorite(UserAndRecipeModel):
    """Модель Избранного."""

    class Meta(UserAndRecipeModel.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(UserAndRecipeModel):
    """Модель Списка покупок."""

    class Meta(UserAndRecipeModel.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Link(models.Model):
    """Модель Ссылки."""

    short_link = models.CharField(
        'Короткая ссылка',
        primary_key=True,
        max_length=MAX_LINK_LENGTH,
        unique=True,
        default=get_link
    )

    source_link = models.CharField(
        'Исходная ссылка',
        max_length=124,
        unique=True
    )

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'

    def __str__(self):
        return f'{self.source_link} -> {self.short_link}'
