from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User
from security.logging import log_security
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Compte désactivé', 'error')
                log_security('login_disabled', f'User: {username}')
                return redirect(url_for('auth.login'))
            
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_superadmin'] = user.is_superadmin
            
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            log_security('login_success', f'User: {username}')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Identifiants incorrects', 'error')
            log_security('login_failed', f'Attempted: {username}')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    username = session.get('username', 'Unknown')
    session.clear()
    log_security('logout', f'User: {username}')
    flash('Déconnecté avec succès', 'success')
    return redirect(url_for('auth.login'))
