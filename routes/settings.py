from flask import Blueprint, render_template, request, redirect, url_for, flash
from security.auth import admin_required
from security.logging import log_activity
from models import db, Settings

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/')
@admin_required
def index():
    categories = ['general', 'seo', 'notifications', 'api', 'security']
    all_settings = {}
    
    for cat in categories:
        all_settings[cat] = Settings.query.filter_by(category=cat).all()
    
    return render_template('admin/settings/index.html', settings=all_settings)

@settings_bp.route('/update', methods=['POST'])
@admin_required
def update():
    for key, value in request.form.items():
        if key.startswith('setting_'):
            setting_key = key[8:]
            category = request.form.get(f'category_{setting_key}', 'general')
            Settings.set(setting_key, value, category)
    
    log_activity('update_settings', details='Settings updated')
    flash('Paramètres enregistrés', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/new', methods=['POST'])
@admin_required
def create():
    key = request.form.get('key')
    value = request.form.get('value')
    category = request.form.get('category', 'general')
    description = request.form.get('description')
    
    if key:
        Settings.set(key, value, category, description)
        flash('Paramètre ajouté', 'success')
    
    return redirect(url_for('settings.index'))

@settings_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete(id):
    setting = Settings.query.get_or_404(id)
    db.session.delete(setting)
    db.session.commit()
    flash('Paramètre supprimé', 'success')
    return redirect(url_for('settings.index'))
