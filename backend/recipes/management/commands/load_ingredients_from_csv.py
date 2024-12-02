import csv
import os

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from apps.recipes.models import Ingredient
from config.settings import BASE_DIR


SUCCESSFULLY_MESSAGE = 'Ингредиенты успешно добавлены.'
FAILURE_MESSAGE = 'Переданные записи уже присутствуют в таблице Ингредиентов.'
SOME_ERROR_MESSAGE = 'Произошла какая-то ошибка.'
FILENAME = 'ingredients.csv'
NOT_FOUND_MESSAGE = ('Файл: {path} не найден.')

path = os.path.join(BASE_DIR, 'data/' + FILENAME)
fieldnames = ['name', 'measurement_unit']


class Command(BaseCommand):
    """Команда на запись Ингредиентвов в базу данных из ingredients.csv."""

    def handle(self, *args, **options):
        try:
            with open(path, 'r', encoding='utf-8') as csvfile:
                Ingredient.objects.bulk_create((
                    Ingredient(**line)
                    for line in csv.DictReader(csvfile, fieldnames=fieldnames)
                ))
                print(SUCCESSFULLY_MESSAGE)
        except IntegrityError:
            print(FAILURE_MESSAGE)
        except FileNotFoundError:
            print(NOT_FOUND_MESSAGE.format(path=path))
