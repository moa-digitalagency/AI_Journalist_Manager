from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            flash('Veuillez vous connecter', 'error')
            return redirect(url_for('auth.login'))
        
        from models import User
        user = User.query.get(user_id)
        if not user or not user.is_active:
            session.clear()
            flash('Session invalide', 'error')
            return redirect(url_for('auth.login'))
        
        if not user.is_superadmin and not user.has_admin_access():
            flash('Accès refusé - Permissions administrateur requises', 'error')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                flash('Veuillez vous connecter', 'error')
                return redirect(url_for('auth.login'))
            
            from models import User
            user = User.query.get(user_id)
            if not user or not user.is_active:
                session.clear()
                flash('Session invalide', 'error')
                return redirect(url_for('auth.login'))
            
            if not user.has_permission(permission):
                flash('Permission refusée', 'error')
                return redirect(url_for('admin.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    from models import User
    return User.query.get(user_id)
