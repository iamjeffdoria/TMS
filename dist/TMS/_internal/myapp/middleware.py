from threading import local
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Thread-local storage for current request
_thread_locals = local()


def get_current_request():
    """Get the current request from thread-local storage"""
    return getattr(_thread_locals, 'request', None)


class CurrentUserMiddleware:
    """
    Middleware to automatically attach current user info to model instances before saving.
    This works seamlessly with your existing login system.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store request in thread-local storage
        _thread_locals.request = request
        
        response = self.get_response(request)
        
        # Clean up thread-local storage
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        
        return response


# Signal to attach user info to all model saves
@receiver(pre_save)
def attach_user_to_model(sender, instance, **kwargs):
    """
    Automatically attach current user info to any model instance being saved.
    Only applies to models we want to track (MayorsPermit, MayorsPermitTricycle, etc.)
    """
    from .models import MayorsPermit, MayorsPermitTricycle, IDCard, Mtop, Franchise
    
    # Only track specific models
    tracked_models = (MayorsPermit, MayorsPermitTricycle, IDCard, Mtop, Franchise)
    
    if not isinstance(instance, tracked_models):
        return
    
    # Skip if user info already attached (manually set)
    if hasattr(instance, '_current_user') and instance._current_user:
        return
    
    # Get current request
    request = get_current_request()
    if not request:
        return
    
    # Extract user info from session
    user_type = request.session.get('user_type')
    if not user_type:
        return
    
    # Attach user info to instance
    if user_type == 'superadmin':
        instance._current_user = {
            'type': 'superadmin',
            'id': request.session.get('superadmin_id'),
            'name': request.session.get('full_name')
        }
    elif user_type == 'admin':
        instance._current_user = {
            'type': 'admin',
            'id': request.session.get('admin_id'),
            'name': request.session.get('full_name')
        }