from datetime import datetime

from rest_framework.serializers import ValidationError


# для render_shopping_cart()
REPORT_TITLE = 'СПИСОК ПОКУПОК'
CREATED_DATE = 'составлен {:%d.%m.%Y}'
INGREDIENTS_TITLE = '\nПродукты:'
INGREDIENT_FORMAT = '{} ({}): {}'
LINE_FORMAT = '  {}. {}'
RECIPES_TITLE = '\nДля приготовления блюд:'
RECIPE_FORMAT = '  - {}'

# для create_or_validation_error()
NOT_UNUNIQUE_MESSAGE = 'Попытка создать дублирующуюся запись в модели {name}.'


def render_shopping_cart(recipes, ingredients):
    ingredients_to_report = [
        LINE_FORMAT.format(
            number,
            INGREDIENT_FORMAT.format(*ingredient).capitalize()
        )
        for number, ingredient in enumerate(ingredients, 1)
    ]
    return '\n'.join([
        REPORT_TITLE,
        CREATED_DATE.format(datetime.now()),
        INGREDIENTS_TITLE,
        *ingredients_to_report,
        RECIPES_TITLE,
        *[RECIPE_FORMAT.format(recipe.name) for recipe in recipes]
    ])


def create_or_validation_error(model, **field_values):
    _, is_created = model.objects.get_or_create(**field_values)
    if not is_created:
        raise ValidationError(NOT_UNUNIQUE_MESSAGE.format(name=model))
