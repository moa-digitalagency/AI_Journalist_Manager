from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from security.auth import admin_required, permission_required
from security.logging import log_activity
from models import db, User, Role

users_bp = Blueprint('users', __name__)

@users_bp.route('/')
@admin_required
def index():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users/index.html', users=users)

@users_bp.route('/new', methods=['GET', 'POST'])
@admin_required
def create():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Utilisateur ou email existe déjà', 'error')
            return redirect(url_for('users.create'))
        
        user = User(
            username=username,
            email=email,
            role_id=request.form.get('role_id', type=int),
            is_superadmin='is_superadmin' in request.form
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        log_activity('create_user', 'user', user.id, f'Created: {username}')
        flash('Utilisateur créé', 'success')
        return redirect(url_for('users.index'))
    
    roles = Role.query.all()
    return render_template('admin/users/form.html', user=None, roles=roles)

@users_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.username = request.form.get('username', user.username)
        user.email = request.form.get('email', user.email)
        user.role_id = request.form.get('role_id', type=int)
        user.is_active = 'is_active' in request.form
        
        current_user = User.query.get(session.get('user_id'))
        if current_user and current_user.is_superadmin:
            user.is_superadmin = 'is_superadmin' in request.form
        
        if request.form.get('password'):
            user.set_password(request.form.get('password'))
        
        db.session.commit()
        log_activity('update_user', 'user', id, f'Updated: {user.username}')
        flash('Utilisateur mis à jour', 'success')
        return redirect(url_for('users.index'))
    
    roles = Role.query.all()
    return render_template('admin/users/form.html', user=user, roles=roles)

@users_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete(id):
    if id == session.get('user_id'):
        flash('Impossible de supprimer votre propre compte', 'error')
        return redirect(url_for('users.index'))
    
    user = User.query.get_or_404(id)
    username = user.username
    db.session.delete(user)
    db.session.commit()
    log_activity('delete_user', 'user', id, f'Deleted: {username}')
    flash('Utilisateur supprimé', 'success')
    return redirect(url_for('users.index'))

@users_bp.route('/roles')
@admin_required
def roles():
    roles = Role.query.all()
    return render_template('admin/users/roles.html', roles=roles)

@users_bp.route('/roles/new', methods=['GET', 'POST'])
@admin_required
def create_role():
    if request.method == 'POST':
        role = Role(
            name=request.form.get('name'),
            permissions=request.form.get('permissions')
        )
        db.session.add(role)
        db.session.commit()
        flash('Rôle créé', 'success')
        return redirect(url_for('users.roles'))
    
    return render_template('admin/users/role_form.html', role=None)
