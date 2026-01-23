from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import (
    MayorsPermit, MayorsPermitTricycle, Admin, IDCard, 
    Mtop, Franchise, ActivityLog
)

# Helper function to get changed fields with exclusions
def get_changed_fields(instance, original, exclude_fields=None):
    """Compare two instances and return changed fields"""
    changed_fields = []
    
    if not original:
        return changed_fields
    
    # Default fields to always exclude
    default_exclude = {'id', 'created_at', 'updated_at'}
    
    # Add any custom exclusions
    if exclude_fields:
        default_exclude.update(exclude_fields)
    
    # List of fields to track
    fields_to_track = [
        field.name for field in instance._meta.fields 
        if field.name not in default_exclude
    ]
    
    for field in fields_to_track:
        old_value = getattr(original, field, None)
        new_value = getattr(instance, field, None)
        
        if old_value != new_value:
            changed_fields.append({
                'field': field,
                'old_value': str(old_value) if old_value is not None else 'None',
                'new_value': str(new_value) if new_value is not None else 'None'
            })
    
    return changed_fields


# Track Potpot Permit changes
@receiver(pre_save, sender=MayorsPermit)
def track_potpot_changes(sender, instance, **kwargs):
    if instance.pk:  # If updating existing record
        try:
            original = MayorsPermit.objects.get(pk=instance.pk)
            instance._original = original
        except MayorsPermit.DoesNotExist:
            instance._original = None
    else:
        instance._original = None


@receiver(post_save, sender=MayorsPermit)
def log_potpot_activity(sender, instance, created, **kwargs):
    # Get user info from instance (set by middleware)
    user_info = getattr(instance, '_current_user', None)
    
    if created:
        # New registration
        ActivityLog.objects.create(
            action='create',
            model_type='potpot',
            object_id=instance.control_no,
            object_name=instance.name,
            description=f'New Potpot permit registered for {instance.name} (Control #{instance.control_no})',
            user_type=user_info.get('type') if user_info else None,
            user_id=user_info.get('id') if user_info else None,
            user_name=user_info.get('name') if user_info else None,
        )
    else:
        # Update existing - EXCLUDE amount_paid from tracking
        original = getattr(instance, '_original', None)
        changed_fields = get_changed_fields(
            instance, 
            original, 
            exclude_fields={'amount_paid'}  # Exclude amount_paid for potpot
        )
        
        if changed_fields:
            # Build detailed description with before/after values with HTML styling
            descriptions = []
            for change in changed_fields:
                field = change['field']
                old_val = change['old_value']
                new_val = change['new_value']
                descriptions.append(
                    f"<strong>{field}:</strong> "
                    f"<span class='text-danger'>{old_val}</span> → "
                    f"<span class='text-success'>{new_val}</span>"
                )
            
            detail = ", ".join(descriptions)

            ActivityLog.objects.create(
                action='update',
                model_type='potpot',
                object_id=instance.control_no,
                object_name=instance.name,
                description=f"Control #{instance.control_no} - {detail}",
                user_type=user_info.get('type') if user_info else None,
                user_id=user_info.get('id') if user_info else None,
                user_name=user_info.get('name') if user_info else None,
            )


# Track Motorcycle Permit changes
@receiver(pre_save, sender=MayorsPermitTricycle)
def track_motorcycle_changes(sender, instance, **kwargs):
    if instance.pk:
        try:
            original = MayorsPermitTricycle.objects.get(pk=instance.pk)
            instance._original = original
        except MayorsPermitTricycle.DoesNotExist:
            instance._original = None
    else:
        instance._original = None


@receiver(post_save, sender=MayorsPermitTricycle)
def log_motorcycle_activity(sender, instance, created, **kwargs):
    # Get user info from instance (set by middleware)
    user_info = getattr(instance, '_current_user', None)
    
    if created:
        ActivityLog.objects.create(
            action='create',
            model_type='motorcycle',
            object_id=instance.control_no,
            object_name=instance.name,
            description=f'New Motorcycle permit registered for {instance.name} (Control #{instance.control_no})',
            user_type=user_info.get('type') if user_info else None,
            user_id=user_info.get('id') if user_info else None,
            user_name=user_info.get('name') if user_info else None,
        )
    else:
        original = getattr(instance, '_original', None)
        # No exclusions for motorcycle (since it's already working correctly)
        changed_fields = get_changed_fields(instance, original)
        
        if changed_fields:
            # Build detailed description with before/after values with HTML styling
            descriptions = []
            for change in changed_fields:
                field = change['field']
                old_val = change['old_value']
                new_val = change['new_value']
                descriptions.append(
                    f"<strong>{field}:</strong> "
                    f"<span class='text-danger'>{old_val}</span> → "
                    f"<span class='text-success'>{new_val}</span>"
                )
            
            detail = ", ".join(descriptions)

            ActivityLog.objects.create(
                action='update',
                model_type='motorcycle',
                object_id=instance.control_no,
                object_name=instance.name,
                description=f"Control #{instance.control_no} - {detail}",
                user_type=user_info.get('type') if user_info else None,
                user_id=user_info.get('id') if user_info else None,
                user_name=user_info.get('name') if user_info else None,
            )


# Track Admin creation
@receiver(post_save, sender=Admin)
def log_admin_activity(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            action='create',
            model_type='admin',
            object_id=str(instance.id),
            object_name=instance.full_name,
            description=f'New admin account created: {instance.full_name} ({instance.username})',
        )


# Track ID Card changes
@receiver(post_save, sender=IDCard)
def log_idcard_activity(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            action='create',
            model_type='idcard',
            object_id=instance.id_number,
            object_name=instance.name,
            description=f'New ID card issued for {instance.name} (ID #{instance.id_number})',
        )


# Track MTOP changes
@receiver(post_save, sender=Mtop)
def log_mtop_activity(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            action='create',
            model_type='mtop',
            object_id=instance.case_no,
            object_name=instance.name,
            description=f'New MTOP registered for {instance.name} (Case #{instance.case_no})',
        )


# Track Franchise changes
@receiver(post_save, sender=Franchise)
def log_franchise_activity(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            action='create',
            model_type='franchise',
            object_id=str(instance.id),
            object_name=instance.name,
            description=f'New franchise registered for {instance.name} (Plate #{instance.plate_no})',
        )