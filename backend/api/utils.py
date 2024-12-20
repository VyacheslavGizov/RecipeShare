from datetime import datetime
from string import capwords
import random
import string

from django.shortcuts import get_object_or_404
from rest_framework.serializers import ValidationError


# для render_shopping_cart()
REPORT_TITLE = 'СПИСОК ПОКУПОК'
CREATED_DATE = 'составлен {:%d.%m.%Y}'
INGREDIENTS_TITLE = '\nПродукты:'
INGREDIENT_FORMAT = '  {}. {} ({}): {}'
RECIPES_TITLE = '\nДля приготовления блюд:'
RECIPE_FORMAT = '  - {}'

# для create_or_validation_error()
NOT_UNUNIQUE_MESSAGE = 'Попытка создать дублирующуюся запись в модели {name}.'


def render_shopping_cart(recipes, ingredients):
    ingredients_to_report = [
        capwords(INGREDIENT_FORMAT.format(number, *ingredient))
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


def get_random_string(string_length):
    alphabet = ''.join([string.ascii_letters, string.digits])
    return ''.join(random.choice(alphabet) for _ in range(string_length))
