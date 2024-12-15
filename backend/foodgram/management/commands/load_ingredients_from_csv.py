import csv
import os

from django.core.management.base import BaseCommand

from ..utils import NOT_FOUND_MESSAGE
from config.settings import BASE_DIR
from foodgram.models import Ingredient


FILENAME = 'ingredients.csv'

path = os.path.join(BASE_DIR, 'data/' + FILENAME)


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
        except FileNotFoundError:
            print(NOT_FOUND_MESSAGE.format(path=path))
