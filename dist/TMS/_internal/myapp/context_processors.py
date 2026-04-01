
def user_session(request):
    """Make user session data available in all templates."""
    can_potpot = request.session.get('can_access_potpot_registration', False) or (request.session.get('user_type') == 'superadmin')
    can_motor = request.session.get('can_access_motorcycle_registration', False) or (request.session.get('user_type') == 'superadmin')
    return {
        'user_type': request.session.get('user_type'),
        'is_superadmin': request.session.get('user_type') == 'superadmin',
        'is_admin': request.session.get('user_type') == 'admin',
        'logged_in_user': request.session.get('full_name'),
        'can_access_potpot_registration': can_potpot,
        'can_access_motorcycle_registration': can_motor,
    }


