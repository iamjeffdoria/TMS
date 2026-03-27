from datetime import date
import logging
from .models import MayorsPermit, MayorsPermitTricycle, MayorsPermitHistory, MayorsPermitTricycleHistory, Tricycle, TricycleHistory,  Franchise

logger = logging.getLogger(__name__)

def mark_expired_tricycles():
    today = date.today()

    qs = Tricycle.objects.filter(
        date_expired__lte=today
    ).exclude(status='Expired')

    count = qs.count()
    if not count:
        return 0

    tricycles = list(qs)

    # ✅ Never touch remarks here
    qs.update(status='Expired')

    histories = [
        TricycleHistory(
            tricycle=tricycle,
            action='expired',
            previous_status=tricycle.status,
            new_status='Expired',
            remarks='Automatically expired by system',
            created_by='system'
        )
        for tricycle in tricycles
    ]
    TricycleHistory.objects.bulk_create(histories)

    logger.info("Expired %d Tricycle(s)", count)
    print(f"Marked {count} tricycle(s) as expired.")
    return count

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
    ).select_related('tricycle')  # ← add this for efficiency

    count = qs.count()
    if count:
        # ✅ RECORD HISTORY
        for permit in qs:
            MayorsPermitTricycleHistory.objects.create(
                permit=permit,
                previous_status='active',
                new_status='expired',
                remarks='Automatically expired by system'
            )
            
            # ✅ UPDATE TRICYCLE REMARKS when permit auto-expires
            if permit.tricycle:
                Tricycle.objects.filter(
                    body_number=permit.tricycle.body_number
                ).update(remarks='without_mayors_permit')

        # ✅ KEEP EXISTING LOGIC
        qs.update(status='expired')

        print(f"Marked {count} tricycle permit(s) as expired.")
        logger.info("Expired %d MayorsPermitTricycle(s)", count)

    return count


def mark_expired_franchises():
    """Automatically expire Franchise records based on valid_until date."""
    today = date.today()

    qs = Franchise.objects.filter(
        valid_until__lt=today
    ).exclude(status='Expired')

    count = qs.count()
    if not count:
        return 0

    # ✅ Only update franchise status, do NOT touch tricycle remarks
    qs.update(status='Expired')

    print(f"Marked {count} franchise(s) as expired.")
    logger.info("Expired %d Franchise(s)", count)
    return count


def mark_expired_permits():
    """Run all expiration routines and return a dict with counts."""
    res1 = mark_expired_mayors_permits()
    res2 = mark_expired_tricycle_permits()
    res3 = mark_expired_tricycles()
    res4 = mark_expired_franchises()
    results = {
        'mayors_permit': res1,
        'tricycle_permit': res2,
        'tricycles': res3,
        'franchises': res4,
    }
    logger.info("Expiration summary: %s", results)
    return results
