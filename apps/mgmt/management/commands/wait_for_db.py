import time
from typing import Any, Dict, Tuple
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Pause execution until database is available.'

    def handle(self, *args: Tuple[Any, ...], **options: Dict[str, Any]) -> None:
        self.stdout.write('Waiting for database...')

        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
                db_conn.cursor()  # Try to get a cursor
            except OperationalError:
                self.stdout.write(self.style.WARNING('Database unavailable, waiting 1 second...'))
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
