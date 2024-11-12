import csv
import os

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from config.settings import BASE_DIR
from apps.recipes.models import Ingredient


# https://habr.com/ru/articles/415049/
# https://django.fun/articles/tutorials/sozdanie-polzovatelskih-komand-upravleniya-v-django/

path = os.path.join(BASE_DIR, 'data/ingredients.csv')
fieldnames = ['name', 'measurement_unit']

# добавить при вызове команды указание пути к файлу относительно
# BASE_DIR и указние полей fieldnames, если поля указаны в самом файле
# то  reader = csv.DictReader(csvfile, fieldnames=fieldnames) без fieldnames,
# и это тоже нужно указать при выхове команды
# посмотреть по исключениям от Квичанского и добавить последний рубеж


class Command(BaseCommand):
    help = 'Здесь описание команды'

    def handle(self, *args, **options):
        with open(path, 'r', encoding='utf-8') as csvfile:
            try:
                reader = csv.DictReader(csvfile, fieldnames=fieldnames)
                records = (Ingredient(**line) for line in reader)
                Ingredient.objects.bulk_create(records)  # можно все в одну строку написать
                print('Успешно')
            except IntegrityError:  # Доработать
                print('Такие записи уже есть в БД')
            except Exception:
                print('Возникла ошибка')
