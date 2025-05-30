import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from recipes.models import Ingredient
from backend_foodgram.settings import CSV_FILES_DIR


class Command(BaseCommand):
    help = 'Загружает данные из файла ingredients.csv в Postgres'

    def handle(self, *args, **options):
        csv_file = 'ingredients.csv'
        csv_path = Path(CSV_FILES_DIR) / 'ingredients.csv'
        fieldnames = ['name', 'measurement_unit']
        try:
            with open(csv_path, encoding='utf-8') as f:
                reader = csv.DictReader(f, fieldnames)
                for row in reader:
                    Ingredient(**row).save()
            print(f'Данные из файла {csv_file} успешно загружены.')
        except FileNotFoundError:
            print(f'Файл {csv_file} не найден.')
