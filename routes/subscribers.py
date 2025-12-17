from flask import Blueprint, render_template, request, redirect, url_for, flash
from security.auth import admin_required
from security.logging import log_activity
from models import db, Subscriber, Journalist, SubscriptionPlan
from datetime import datetime, timedelta

subscribers_bp = Blueprint('subscribers', __name__)

@subscribers_bp.route('/')
@admin_required
def index():
    journalist_id = request.args.get('journalist_id', type=int)
    status = request.args.get('status')
    
    query = Subscriber.query.order_by(Subscriber.created_at.desc())
    
    if journalist_id:
        query = query.filter_by(journalist_id=journalist_id)
    
    if status == 'approved':
        query = query.filter_by(is_approved=True)
    elif status == 'pending':
        query = query.filter_by(is_approved=False)
    elif status == 'expired':
        query = query.filter(Subscriber.subscription_end < datetime.utcnow())
    
    subscribers = query.all()
    journalists = Journalist.query.all()
    plans = SubscriptionPlan.query.filter_by(is_active=True).all()
    
    return render_template('admin/subscribers/index.html', 
                         subscribers=subscribers,
                         journalists=journalists,
                         plans=plans)

@subscribers_bp.route('/<int:id>/approve', methods=['POST'])
@admin_required
def approve(id):
    subscriber = Subscriber.query.get_or_404(id)
    plan_id = request.form.get('plan_id', type=int)
    
    subscriber.is_approved = True
    subscriber.is_active = True
    
    if plan_id:
        plan = SubscriptionPlan.query.get(plan_id)
        if plan:
            subscriber.plan_id = plan_id
            subscriber.subscription_start = datetime.utcnow()
            subscriber.subscription_end = datetime.utcnow() + timedelta(days=plan.duration_days)
    
    db.session.commit()
    log_activity('approve_subscriber', 'subscriber', id)
    flash('Abonné approuvé', 'success')
    return redirect(url_for('subscribers.index'))

@subscribers_bp.route('/<int:id>/revoke', methods=['POST'])
@admin_required
def revoke(id):
    subscriber = Subscriber.query.get_or_404(id)
    subscriber.is_approved = False
    subscriber.is_active = False
    db.session.commit()
    log_activity('revoke_subscriber', 'subscriber', id)
    flash('Accès révoqué', 'success')
    return redirect(url_for('subscribers.index'))

@subscribers_bp.route('/<int:id>/extend', methods=['POST'])
@admin_required
def extend(id):
    subscriber = Subscriber.query.get_or_404(id)
    days = request.form.get('days', 7, type=int)
    
    if subscriber.subscription_end:
        subscriber.subscription_end = subscriber.subscription_end + timedelta(days=days)
    else:
        subscriber.subscription_end = datetime.utcnow() + timedelta(days=days)
    
    db.session.commit()
    log_activity('extend_subscription', 'subscriber', id, f'+{days} days')
    flash(f'Abonnement prolongé de {days} jours', 'success')
    return redirect(url_for('subscribers.index'))

@subscribers_bp.route('/<int:id>/assign-plan', methods=['POST'])
@admin_required
def assign_plan(id):
    subscriber = Subscriber.query.get_or_404(id)
    plan_id = request.form.get('plan_id', type=int)
    
    plan = SubscriptionPlan.query.get_or_404(plan_id)
    subscriber.plan_id = plan_id
    subscriber.subscription_start = datetime.utcnow()
    subscriber.subscription_end = datetime.utcnow() + timedelta(days=plan.duration_days)
    subscriber.is_approved = True
    subscriber.is_active = True
    
    db.session.commit()
    log_activity('assign_plan', 'subscriber', id, f'Plan: {plan.name}')
    flash(f'Forfait {plan.name} assigné', 'success')
    return redirect(url_for('subscribers.index'))
