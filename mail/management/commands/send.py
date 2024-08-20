from django.core.management import BaseCommand
from mail.services import my_job


class Command(BaseCommand):

    def handle(self, *args, **options):
        my_job()
