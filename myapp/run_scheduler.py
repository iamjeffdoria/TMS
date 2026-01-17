import os
import logging
from threading import Thread, Event
import time

from .tasks import mark_expired_permits

logger = logging.getLogger(__name__)

_started = False
_stop_event = Event()


def _run_loop(interval_seconds: int):
    logger.info("Scheduler loop started (interval=%s seconds)", interval_seconds)

    # Run initial check immediately on start
    try:
        logger.info("Running initial scheduled tasks")
        start_ts = time.time()
        results = mark_expired_permits()
        # Log counts when available
        if isinstance(results, dict):
            for k, v in results.items():
                logger.info("Expired %d rows for %s", v, k)
        else:
            logger.info("Expired result: %s", results)
        logger.info("Initial scheduled tasks completed in %.2fs", time.time() - start_ts)
    except Exception:
        logger.exception("Initial scheduled task failed")

    # Main loop
    while not _stop_event.wait(interval_seconds):
        try:
            logger.info("Running scheduled tasks")
            start_ts = time.time()
            results = mark_expired_permits()
            # Log counts when available
            if isinstance(results, dict):
                for k, v in results.items():
                    logger.info("Expired %d rows for %s", v, k)
            else:
                logger.info("Expired result: %s", results)
            logger.info("Scheduled tasks completed in %.2fs", time.time() - start_ts)
        except Exception:
            logger.exception("Scheduled task failed")


from typing import Optional

def start(interval_seconds: Optional[int] = None):
    """Start the background scheduler thread.

    interval_seconds: how often to run tasks (in seconds); defaults to the
    SCHEDULER_INTERVAL env var if set, otherwise 60 seconds (1 minute) for the
    development server convenience.
    """
    global _started
    if _started:
        logger.debug("Scheduler already started")
        return

    if interval_seconds is None:
        try:
            interval_seconds = int(os.environ.get("SCHEDULER_INTERVAL", "60"))
        except ValueError:
            interval_seconds = 60

    thread = Thread(target=_run_loop, args=(interval_seconds,), daemon=True)
    thread.setName("myapp-scheduler")
    thread.start()
    _started = True
    logger.info("Scheduler started (interval=%s seconds)", interval_seconds)


def stop():
    """Stop the background scheduler (only useful for clean shutdowns/tests)."""
    _stop_event.set()
    logger.info("Scheduler stop requested")
