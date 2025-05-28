from django.core.management.base import BaseCommand
import csv
from datetime import datetime
from home.models import Holiday

class Command(BaseCommand):
    help = 'import holidays from csv'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type = str, help = 'path to csv file')

    def handle(self, *args, **options):
        csv_path = options['csv_path']

        with open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                name = row['Name']
                date_str = row['Date']
                date = datetime.strptime(date_str, '%d-%b-%Y').date()
                _, created = Holiday.objects.get_or_create(name=name, date=date)
                if created:
                    count = count + 1
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} holiday(s)'))
