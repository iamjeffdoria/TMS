import time
import schedule
from django.core.management.base import BaseCommand
from myapp.tasks import mark_expired_permits

class Command(BaseCommand):
    help = 'Run the scheduler to mark expired permits'
    # just call the function once before starting scheduler
  

    def handle(self, *args, **kwargs):
        mark_expired_permits()
        schedule.every(1).minutes.do(mark_expired_permits)  # Run daily at midnight

        self.stdout.write(self.style.SUCCESS('Scheduler started...'))
        while True:
            schedule.run_pending()  
            time.sleep(1)
