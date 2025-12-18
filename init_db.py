#!/usr/bin/env python3
"""
Database initialization script for AI Journalist Manager.
Run this script to initialize the database schema and default data.
"""
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

REQUIRED_ENV_VARS = [
    ('DATABASE_URL', True, 'PostgreSQL database connection URL'),
    ('SECRET_KEY', False, 'Flask session secret key (has default fallback)'),
    ('GEMINI_API_KEY', False, 'Google Gemini API key for AI features'),
    ('PERPLEXITY_API_KEY', False, 'Perplexity API key for AI features (alternative to Gemini)'),
    ('ELEVEN_LABS_API_KEY', False, 'Eleven Labs API key for audio generation'),
]

def check_environment():
    """Check that required environment variables are set."""
    logger.info("Checking environment variables...")
    missing_required = []
    missing_optional = []
    
    for var_name, required, description in REQUIRED_ENV_VARS:
        value = os.environ.get(var_name)
        if value:
            logger.info(f"  [OK] {var_name} is configured")
        elif required:
            logger.error(f"  [MISSING] {var_name} - {description} (REQUIRED)")
            missing_required.append(var_name)
        else:
            logger.warning(f"  [MISSING] {var_name} - {description} (optional)")
            missing_optional.append(var_name)
    
    if missing_required:
        logger.error(f"\nMissing required environment variables: {', '.join(missing_required)}")
        logger.error("Please set these variables in the Secrets tab on Replit")
        return False
    
    if missing_optional:
        logger.warning(f"\nOptional variables not set: {', '.join(missing_optional)}")
        logger.warning("Some features may be limited without these.")
    
    return True

def init_database():
    """Initialize database tables."""
    from app import app
    from models import db
    
    with app.app_context():
        logger.info("Creating database tables...")
        db.create_all()
        logger.info("Database tables created successfully")

def init_roles():
    """Initialize default user roles."""
    from app import app
    from models import db, Role
    
    with app.app_context():
        if Role.query.first():
            logger.info("Roles already exist, skipping...")
            return
        
        logger.info("Creating default roles...")
        roles = [
            Role(name='Admin', permissions='all'),
            Role(name='Editor', permissions='journalists,subscribers,plans'),
            Role(name='Viewer', permissions='view'),
        ]
        db.session.add_all(roles)
        db.session.commit()
        logger.info("Default roles created")

def init_admin():
    """Initialize admin user if none exists."""
    from app import app
    from models import db, User
    
    with app.app_context():
        if User.query.first():
            logger.info("Users already exist, skipping admin creation...")
            return
        
        logger.info("Creating admin user...")
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
        logger.info(f"Admin user created: {admin_username}")

def init_subscription_plans():
    """Initialize default subscription plans."""
    from app import app
    from models import db, SubscriptionPlan
    
    with app.app_context():
        if SubscriptionPlan.query.first():
            logger.info("Subscription plans already exist, skipping...")
            return
        
        logger.info("Creating default subscription plans...")
        plans = [
            SubscriptionPlan(
                name='Essai Gratuit',
                description='7 jours pour découvrir le service',
                duration_days=7,
                price=0,
                is_trial=True,
                can_receive_summaries=True,
                can_ask_questions=True,
                can_receive_audio=False
            ),
            SubscriptionPlan(
                name='Basic',
                description='Accès aux résumés et questions',
                duration_days=30,
                price=9.99,
                can_receive_summaries=True,
                can_ask_questions=True,
                can_receive_audio=False
            ),
            SubscriptionPlan(
                name='Premium',
                description='Accès complet avec résumés audio',
                duration_days=30,
                price=19.99,
                can_receive_summaries=True,
                can_ask_questions=True,
                can_receive_audio=True
            ),
        ]
        db.session.add_all(plans)
        db.session.commit()
        logger.info("Default subscription plans created")

def init_default_settings():
    """Initialize default application settings."""
    from app import app
    from models import db, Settings
    
    default_settings = {
        'general': [
            {'key': 'app_name', 'value': 'AI Journalist Manager', 'description': 'Nom de l\'application'},
            {'key': 'default_language', 'value': 'fr', 'description': 'Langue par défaut'},
            {'key': 'trial_days', 'value': '7', 'description': 'Durée de la période d\'essai en jours'},
            {'key': 'fetch_hour', 'value': '2', 'description': 'Heure de collecte automatique (0-23)'},
            {'key': 'summary_hour', 'value': '8', 'description': 'Heure d\'envoi des résumés (0-23)'},
            {'key': 'default_timezone', 'value': 'Europe/Paris', 'description': 'Fuseau horaire par défaut'},
        ],
        'api': [
            {'key': 'gemini_model', 'value': 'gemini-2.5-flash', 'description': 'Modèle Gemini à utiliser'},
            {'key': 'eleven_labs_default_voice', 'value': '21m00Tcm4TlvDq8ikWAM', 'description': 'Voice ID Eleven Labs par défaut'},
            {'key': 'summary_max_length', 'value': '2000', 'description': 'Longueur maximale des résumés'},
            {'key': 'youtube_transcript_languages', 'value': 'fr,en,es,de', 'description': 'Langues de transcription YouTube'},
        ],
        'notifications': [
            {'key': 'enable_email_notifications', 'value': 'false', 'description': 'Activer les notifications email'},
            {'key': 'admin_email', 'value': '', 'description': 'Email de l\'administrateur'},
            {'key': 'notify_on_new_subscriber', 'value': 'true', 'description': 'Notification nouvel abonné'},
            {'key': 'notify_on_error', 'value': 'true', 'description': 'Notification en cas d\'erreur'},
        ],
        'security': [
            {'key': 'max_login_attempts', 'value': '5', 'description': 'Tentatives de connexion maximum'},
            {'key': 'session_timeout', 'value': '60', 'description': 'Timeout de session (minutes)'},
            {'key': 'require_email_verification', 'value': 'false', 'description': 'Exiger vérification email'},
            {'key': 'log_all_activities', 'value': 'true', 'description': 'Journaliser toutes les activités'},
        ],
        'seo': [
            {'key': 'meta_title', 'value': 'AI Journalist Manager', 'description': 'Titre meta SEO'},
            {'key': 'meta_description', 'value': 'Plateforme de gestion de journalistes IA', 'description': 'Description meta'},
            {'key': 'meta_keywords', 'value': 'ia, journaliste, actualités, telegram, bot', 'description': 'Mots-clés meta'},
        ],
    }
    
    with app.app_context():
        count = 0
        for category, settings_list in default_settings.items():
            for setting_data in settings_list:
                existing = Settings.query.filter_by(key=setting_data['key']).first()
                if not existing:
                    setting = Settings(
                        key=setting_data['key'],
                        value=setting_data['value'],
                        category=category,
                        description=setting_data.get('description')
                    )
                    db.session.add(setting)
                    count += 1
        
        db.session.commit()
        if count > 0:
            logger.info(f"Initialized {count} default settings")
        else:
            logger.info("Settings already exist, skipping...")

def run_initialization():
    """Run the full database initialization."""
    logger.info("=" * 50)
    logger.info("AI Journalist Manager - Database Initialization")
    logger.info("=" * 50)
    
    if not check_environment():
        logger.error("Environment check failed. Please configure required variables.")
        return False
    
    try:
        init_database()
        init_roles()
        init_admin()
        init_subscription_plans()
        init_default_settings()
        
        logger.info("=" * 50)
        logger.info("Database initialization completed successfully!")
        logger.info("=" * 50)
        return True
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        return False

if __name__ == '__main__':
    success = run_initialization()
    sys.exit(0 if success else 1)
