import os
from datetime import datetime
from flask import Flask
from models import db, User, Role, SubscriptionPlan
from routes import register_blueprints
from utils.helpers import format_datetime, time_ago, truncate

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.context_processor
def utility_processor():
    return {
        'now': datetime.utcnow,
        'format_datetime': format_datetime,
        'time_ago': time_ago,
        'truncate': truncate
    }

register_blueprints(app)

def init_db():
    with app.app_context():
        db.create_all()
        
        if not Role.query.first():
            admin_role = Role(name='Admin', permissions='all')
            editor_role = Role(name='Editor', permissions='journalists,subscribers,plans')
            viewer_role = Role(name='Viewer', permissions='view')
            db.session.add_all([admin_role, editor_role, viewer_role])
            db.session.commit()
        
        if not User.query.first():
            admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            
            admin = User(
                username=admin_username,
                email=admin_email,
                is_superadmin=True,
                is_active=True
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"Admin created: {admin_username}")
        
        if not SubscriptionPlan.query.first():
            trial = SubscriptionPlan(
                name='Essai Gratuit',
                description='7 jours d\'essai',
                duration_days=7,
                price=0,
                is_trial=True,
                can_receive_summaries=True,
                can_ask_questions=True,
                can_receive_audio=False
            )
            basic = SubscriptionPlan(
                name='Basic',
                description='Accès standard',
                duration_days=30,
                price=9.99,
                can_receive_summaries=True,
                can_ask_questions=True,
                can_receive_audio=False
            )
            premium = SubscriptionPlan(
                name='Premium',
                description='Accès complet avec audio',
                duration_days=30,
                price=19.99,
                can_receive_summaries=True,
                can_ask_questions=True,
                can_receive_audio=True
            )
            db.session.add_all([trial, basic, premium])
            db.session.commit()

init_db()

if __name__ == '__main__':
    from services.scheduler_service import SchedulerService
    SchedulerService.init()
    app.run(host='0.0.0.0', port=5000, debug=True)
