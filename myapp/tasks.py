from datetime import date
import logging
from .models import MayorsPermit, MayorsPermitTricycle, MayorsPermitHistory, MayorsPermitTricycleHistory

logger = logging.getLogger(__name__)

def mark_expired_mayors_permits():
    """Expire regular Mayor's Permits and return count."""
    today = date.today()

    qs = MayorsPermit.objects.filter(
        expiry_date__lte=today,
        status='active'
    )

    count = qs.count()
    if not count:
        return 0

    # ✅ Step 1: snapshot permits BEFORE update
    permits = list(qs)

    # ✅ Step 2: original behavior (UNCHANGED)
    qs.update(status='expired')

    # ✅ Step 3: record history
    histories = [
        MayorsPermitHistory(
            permit=permit,
            previous_status='active',
            new_status='expired',
            remarks='Automatically expired by system'
        )
        for permit in permits
    ]
    MayorsPermitHistory.objects.bulk_create(histories)

    print(f"Marked {count} permits as expired.")
    logger.info("Expired %d MayorsPermit(s)", count)
    return count

def mark_expired_tricycle_permits():
    """Expire tricycle permits and return count."""
    today = date.today()
    qs = MayorsPermitTricycle.objects.filter(
        expiry_date__lte=today,
        status='active'
    )

    count = qs.count()
    if count:
        # ✅ RECORD HISTORY (minimal addition)
        for permit in qs:
            MayorsPermitTricycleHistory.objects.create(
                permit=permit,
                previous_status='active',
                new_status='expired',
                remarks='Automatically expired by system'
            )

        # ✅ KEEP EXISTING LOGIC
        qs.update(status='expired')

        print(f"Marked {count} tricycle permit(s) as expired.")
        logger.info("Expired %d MayorsPermitTricycle(s)", count)

    return count


def mark_expired_permits():
    """Run both expiration routines and return a dict with counts."""
    res1 = mark_expired_mayors_permits()
    res2 = mark_expired_tricycle_permits()
    results = {
        'mayors_permit': res1,
        'tricycle_permit': res2,
    }
    logger.info("Expiration summary: %s", results)
    return results
