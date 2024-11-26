import csv
import os

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from config.settings import BASE_DIR
from apps.recipes.models import Ingredient


path = os.path.join(BASE_DIR, 'data/ingredients.csv')
fieldnames = ['name', 'measurement_unit']


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(path, 'r', encoding='utf-8') as csvfile:
            try:
                Ingredient.objects.bulk_create((
                    Ingredient(**line)
                    for line in csv.DictReader(csvfile, fieldnames=fieldnames)
                ))
                print('Успешно.')
            except IntegrityError:
                print('Такие записи уже есть в БД.')
            except Exception:
                print('Возникла ошибка.')
# class Command(BaseCommand):
#     def handle(self, *args, **options):
#         with open(path, 'r', encoding='utf-8') as csvfile:
#             try:
#                 reader = csv.DictReader(csvfile, fieldnames=fieldnames)
#                 records = (Ingredient(**line) for line in reader)
#                 Ingredient.objects.bulk_create(records)  # можно все в одну строку написать
#                 print('Успешно')
#             except IntegrityError:  # Доработать
#                 print('Такие записи уже есть в БД')
#             except Exception:
#                 print('Возникла ошибка')
