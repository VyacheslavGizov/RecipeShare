from datetime import datetime


def render_shopping_cart(recipes, ingredients):
    REPORT_TITLE = 'СПИСОК ПОКУПОК'
    CREATED_DATE = 'составлен {:%d.%m.%Y}'.format(datetime.now())
    INGREDIENTS_TITLE = '\nПродукты:'
    INGREDIENT_FORMAT = '  {}. {} ({}): {}'
    RECIPES_TITLE = '\nДля приготовления блюд:'
    RECIPE_FORMAT = '  - {}'

    counter = 0
    ingredients_to_report = []
    for ingredient in ingredients:
        counter += 1
        ingredients_to_report.append(INGREDIENT_FORMAT.format(
            counter,
            ingredient[0].capitalize(),
            *ingredient[1:])
        )
    return '\n'.join([
        REPORT_TITLE,
        CREATED_DATE,
        INGREDIENTS_TITLE,
        *ingredients_to_report,
        RECIPES_TITLE,
        *[RECIPE_FORMAT.format(recipe) for recipe in recipes]
    ])
