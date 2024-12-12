from datetime import datetime


def render_shopping_cart(recipes, ingredients):
    current_date = datetime.now().strftime('%d.%m.%Y')
    REPORT_TITLE = 'СПИСОК ПОКУПОК ({date})'.format(date=current_date)
    INGREDIENTS_TITLE = 'Продукты:'
    INGREDIENT_FORMAT = '{number}. {}'
    ingredients = [for ingredient in ingredients]
