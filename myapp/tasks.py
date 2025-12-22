from datetime import date
from .models import MayorsPermit

def mark_expired_permits():
    today = date.today()
    
    # Get all active permits that are expired
    expired_permits = MayorsPermit.objects.filter(expiry_date__lte=today, status='active')
    
    # Count them before updating
    count = expired_permits.count()
    
    # Update status to expired
    expired_permits.update(status='expired')
    
    print(f"Marked {count} permits as expired.")
