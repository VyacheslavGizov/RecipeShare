from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from constants import DESCRIPTION_LENGTH_LIMIT


User = get_user_model()


MIN_COOKING_TIME = 1
MIN_AMMOUNT = 1
COOKING_TIME_MESSAGE = 'Минимальное время приготовления: {cooking_time} мин.'
INGREDIENT_AMMOUNT_MESSAGE = ('Минимальное количество ингредиента: '
                              ' {ammount} [ед.изм.].')
COLOR_HELP_TEXT = 'Введите цвет тега (например: #ADD8E6)',
COLOR_VALIDATOR_MESSAGE = 'Требуемый формат: HEX'
INGREDIENT_HELP_TEXT = 'Укажите необходимые ингредиенты'
TAG_HELP_TEXT = 'Выберите один или несколько тегов'


class Tag(models.Model):
    """Модель Тега."""

    BLACK = '#000000'

    name = models.CharField('Уникальное название', max_length=32, unique=True,)
    color = models.CharField(
        'Цвет тега в hex-формате',
        max_length=7,
        default=BLACK,
        help_text=COLOR_HELP_TEXT,
        validators=[
            RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6})$',
                message=COLOR_VALIDATOR_MESSAGE
            )
        ]
    )
    slug = models.SlugField(
        'Уникальный Slug',
        max_length=32,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return (f'{self.name} | {self.slug}')


class Ingredient(models.Model):
    """Модель ингредента."""

    name = models.CharField('Название', max_length=128, db_index=True,)
    measurement_unit = models.CharField('Единица измерения', max_length=64,)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name', 'id')
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_measurement_unit',
            )
        ]

    def __str__(self):
        return (
            f'{self.name[:DESCRIPTION_LENGTH_LIMIT]}, '
            f'{self.measurement_unit[:DESCRIPTION_LENGTH_LIMIT]}'
        )


class Recipe(models.Model):
    """Модель Рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text='Автор рецепта',
        verbose_name='Автор рецепта',
    )
    name = models.CharField('Название рецепта', max_length=256,)
    image = models.ImageField('Фото блюда', upload_to='recipes_images/',)
    text = models.TextField('Описание рецепта', max_length=2200,)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngridients',
        verbose_name='Ингредиенты',
        help_text=INGREDIENT_HELP_TEXT
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text=TAG_HELP_TEXT
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message=COOKING_TIME_MESSAGE.format(
                    cooking_time=MIN_COOKING_TIME)
            )
        ],
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
    )

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
    """Ингредиенты для Рецепта - промежуточная модель."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Название рецепта',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                MIN_AMMOUNT,
                message=INGREDIENT_AMMOUNT_MESSAGE.format(
                    ammount=MIN_AMMOUNT)
            )
        ],
    )

    class Meta:
        verbose_name = 'Ингредиенты для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'
        default_related_name = 'recipe_ingridients'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return (f'{self.recipe}: {self.ingredient} - {self.amount}')


class FavoriteShoppingCartBaseModel(models.Model):
    """Абстрактная модель для Избранного и Списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True


class Favorite(FavoriteShoppingCartBaseModel):
    """Модель Избранного."""

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorite_records'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_favorite'
            )
        ]

    def __str__(self):
        return (
            f'{self.user}: '
            f'({self.recipe.__str__()[:DESCRIPTION_LENGTH_LIMIT]})'
            '- в Избранном'
        )


class ShoppingCart(FavoriteShoppingCartBaseModel):
    """Модель Списка покупок."""

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart_records'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe', ],
                name='unique_recipe_in_shoping_cart'
            )
        ]

    def __str__(self):
        return (
            f'{self.user}: '
            f'({self.recipe.__str__()[:DESCRIPTION_LENGTH_LIMIT]})'
            '- в Списке покупок'
        )
