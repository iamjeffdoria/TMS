
def user_session(request):
    """Make user session data available in all templates."""
    return {
        'user_type': request.session.get('user_type'),
        'is_superadmin': request.session.get('user_type') == 'superadmin',
        'is_admin': request.session.get('user_type') == 'admin',
        'logged_in_user': request.session.get('full_name'),
    }