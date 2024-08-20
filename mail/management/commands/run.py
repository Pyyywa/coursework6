from time import sleep
import os

from django.core.management import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler

from mail.services import my_job

scheduler = BackgroundScheduler()

scheduler.add_job(my_job, 'interval', seconds=30)


class Command(BaseCommand):

    def handle(self, *args, **options):
        scheduler.start()
        print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
        try:
            while True:
                sleep(1)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown(wait=False)
        print("END.", flush=True)
