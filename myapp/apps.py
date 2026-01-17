import os
import sys
import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        """Start background scheduler when running the development server.

        Uses two guards to avoid starting multiple times:
        - only when `runserver` is in sys.argv (we only want this for dev server)
        - only when the autoreloader's child process is running (RUN_MAIN=="true")
        """
        try:
            # Only start when managing the dev server (manage.py runserver)
            if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') == 'true':
                # Import and start the scheduler
                from . import run_scheduler

                logger.info("Starting myapp scheduler from AppConfig.ready()")
                run_scheduler.start()
        except Exception:
            logger.exception("Failed to start scheduler in AppConfig.ready()")

