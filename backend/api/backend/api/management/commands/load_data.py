import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from recipes.models import Ingredient
from backend_foodgram.settings import CSV_FILES_DIR
from constants import INGREDIENT_CSV_FILE


class Command(BaseCommand):
    help = 'Загружает данные из файла ingredients.csv в Postgres'

    def handle(self, *args, **options):
        csv_path = Path(CSV_FILES_DIR) / INGREDIENT_CSV_FILE
        fieldnames = ['name', 'measurement_unit']
        try:
            with open(csv_path, encoding='utf-8') as f:
                reader = csv.DictReader(f, fieldnames)
                for row in reader:
                    Ingredient(**row).save()
        except FileNotFoundError:
            ...
