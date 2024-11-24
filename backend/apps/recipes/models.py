from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from constants import DESCRIPTION_LENGTH_LIMIT


User = get_user_model()


# Может быть сделать абстрактные модели

# Перенести все константы и сообщения в отдельне модули

MIN_COOKING_TIME = 1
MIN_AMMOUNT = 1
COOKING_TIME_MESSAGE = 'Минимальное время приготовления: {cooking_time} мин.'
INGREDIENT_AMMOUNT_MESSAGE = ('Минимальное количество ингредиента: '
                              ' {ammount} [ед.изм.].')


# проверить ordering
# Добавить индексы в поля сортировки и поиска
# добавить преобразование к нижнему регистру, чтобы в базе все было одинаково
class Tag(models.Model):
    """Модель Тега."""

    # нужна ли вся эта лабуда с цветами тегов
    LILAC = '#E26CFD'
    BLUE = '#ADD8E6'
    PEACH = '#FFDAB9'

    TAG_COLORS = [
        (LILAC, 'Сиреневый'),  # запишется в БД/отобразится при выборе
        (BLUE, 'Голубой'),
        (PEACH, 'Первсиковый'),
    ]

    name = models.CharField(
        'Уникальное название',
        max_length=32,
        unique=True,
    )
    # color = models.CharField(  # может сделать отдельный тип поля для цветов
    #     'Цвет тега',
    #     max_length=7,
    #     choices=TAG_COLORS,
    #     default=LILAC,
    #     help_text='Выберите предустановленный цвет тега'
    # )
    color = models.CharField(  # оставить просто текстовым полем, и установить один дефолтный цвет
        'Цвет тега в hex-формате',
        max_length=7,
        help_text='Введите цвет тега (например: #ADD8E6)',
        validators=[
            RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6})$',
                message='Требуемый формат: HEX'
            )
        ]
    )
    # в документации string or null, в то же время обязательно к заполнению
    # c пустой строкой не даст заполнить
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

    name = models.CharField(
        'Название',
        max_length=128,
        db_index=True,
    )

    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=64,
    )

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
        # почему, а если рецепт классный, может добавить,
        # что нельзя подписаться, и на странице рецепта
        # что-то типо: пользователь удален
        # можно сделать
        # def get_sentinel_user():
        #     return get_user_model().objects.get_or_create(username='deleted')[0]

        # class MyModel(models.Model):
        #     user = models.ForeignKey(
        #         settings.AUTH_USER_MODEL,
        #         on_delete=models.SET(get_sentinel_user),
        # ) https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.CASCADE
        on_delete=models.CASCADE,
        help_text='Автор рецепта',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=256,
    )
    image = models.ImageField(
        'Фото блюда',
        upload_to='recipe_images/',
    )
    text = models.TextField(
        'Описание рецепта',
        help_text='Опишите способ приготовления блюда',
        # наверно нужно ограничить максимальную длину
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngridients',
        verbose_name='Ингридиенты',
        help_text='Укажите необходимые ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text='Выберите один или несколько тегов'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=[
            MinValueValidator(  # можн проверить, что не ноль
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
    """Ингредиенты для рецепта - промежуточная модель."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingridients',
        verbose_name='Название рецепта',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        # Запрещает удалять ингридиент, пока он используется в рецепте
        on_delete=models.PROTECT,
        related_name='recipes_with_ingridient',
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
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return (f'{self.recipe}: {self.ingredient} - {self.amount}')


class Favorite(models.Model):
    """Модель Избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        # related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        # related_name='favorites_among_users',
        verbose_name='Рецепт',
    )

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


class ShoppingCart(models.Model):
    """Модель Списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        # related_name='shoping_cart_recipes',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        # related_name='users_add_in_shoping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart_records'  # добавил
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
