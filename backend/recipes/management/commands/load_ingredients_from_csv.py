import csv
import os

from django.core.management.base import BaseCommand

from ..utils import SOME_ERROR
from config.settings import BASE_DIR
from recipes.models import Ingredient


FILENAME = 'ingredients.csv'

path = os.path.join(BASE_DIR, f'data/{FILENAME}')


class Command(BaseCommand):
    """Команда на запись Продуктов в базу данных из ingredients.csv."""

    def handle(self, *args, **options):
        try:
            with open(path, 'r', encoding='utf-8') as csvfile:
                Ingredient.objects.bulk_create(
                    (
                        Ingredient(**line)
                        for line in csv.DictReader(
                            csvfile,
                            fieldnames=('name', 'measurement_unit')
                        )
                    ),
                    ignore_conflicts=True
                )
        except Exception as error:
            print(SOME_ERROR.format(model=Ingredient, path=path, error=error))
