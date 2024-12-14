import os

from django.core.management.base import BaseCommand

from ..utils import load_from_json
from config.settings import BASE_DIR
from foodgram.models import Tag

FILENAME = 'tags.json'
path = os.path.join(BASE_DIR, 'data/' + FILENAME)


class Command(BaseCommand):
    """Команда на запись Тегов в базу данных из tags.json."""

    def handle(self, *args, **options):
        load_from_json(model=Tag, path=path)
