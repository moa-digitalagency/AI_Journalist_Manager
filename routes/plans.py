from flask import Blueprint, render_template, request, redirect, url_for, flash
from security.auth import admin_required
from security.logging import log_activity
from models import db, SubscriptionPlan

plans_bp = Blueprint('plans', __name__)

@plans_bp.route('/')
@admin_required
def index():
    plans = SubscriptionPlan.query.order_by(SubscriptionPlan.created_at.desc()).all()
    return render_template('admin/plans/index.html', plans=plans)

@plans_bp.route('/new', methods=['GET', 'POST'])
@admin_required
def create():
    if request.method == 'POST':
        plan = SubscriptionPlan(
            name=request.form.get('name'),
            description=request.form.get('description'),
            duration_days=request.form.get('duration_days', 30, type=int),
            price=request.form.get('price', 0, type=float),
            features=request.form.get('features'),
            max_messages_per_day=request.form.get('max_messages', -1, type=int),
            can_receive_summaries='can_receive_summaries' in request.form,
            can_ask_questions='can_ask_questions' in request.form,
            can_receive_audio='can_receive_audio' in request.form,
            is_trial='is_trial' in request.form
        )
        db.session.add(plan)
        db.session.commit()
        
        log_activity('create_plan', 'plan', plan.id, f'Created: {plan.name}')
        flash('Forfait créé', 'success')
        return redirect(url_for('plans.index'))
    
    return render_template('admin/plans/form.html', plan=None)

@plans_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(id):
    plan = SubscriptionPlan.query.get_or_404(id)
    
    if request.method == 'POST':
        plan.name = request.form.get('name', plan.name)
        plan.description = request.form.get('description')
        plan.duration_days = request.form.get('duration_days', plan.duration_days, type=int)
        plan.price = request.form.get('price', plan.price, type=float)
        plan.features = request.form.get('features')
        plan.max_messages_per_day = request.form.get('max_messages', plan.max_messages_per_day, type=int)
        plan.can_receive_summaries = 'can_receive_summaries' in request.form
        plan.can_ask_questions = 'can_ask_questions' in request.form
        plan.can_receive_audio = 'can_receive_audio' in request.form
        plan.is_trial = 'is_trial' in request.form
        plan.is_active = 'is_active' in request.form
        
        db.session.commit()
        log_activity('update_plan', 'plan', id, f'Updated: {plan.name}')
        flash('Forfait mis à jour', 'success')
        return redirect(url_for('plans.index'))
    
    return render_template('admin/plans/form.html', plan=plan)

@plans_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete(id):
    plan = SubscriptionPlan.query.get_or_404(id)
    name = plan.name
    db.session.delete(plan)
    db.session.commit()
    log_activity('delete_plan', 'plan', id, f'Deleted: {name}')
    flash('Forfait supprimé', 'success')
    return redirect(url_for('plans.index'))
