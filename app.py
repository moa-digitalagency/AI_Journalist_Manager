import os
import logging
import atexit
from datetime import datetime
from flask import Flask, session, request, redirect, url_for
from models import db, User, Role, SubscriptionPlan
from routes import register_blueprints
from utils.helpers import format_datetime, time_ago, truncate
from translations import TranslationHelper, get_translation

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 300,
    'pool_pre_ping': True,
}
app.config['LANGUAGES'] = ['fr', 'en']
app.config['DEFAULT_LANGUAGE'] = 'fr'

db.init_app(app)

@app.before_request
def before_request():
    if 'lang' not in session:
        session['lang'] = app.config['DEFAULT_LANGUAGE']

@app.route('/set-language/<lang>')
def set_language(lang):
    if lang in app.config['LANGUAGES']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('admin.dashboard'))

@app.context_processor
def utility_processor():
    lang = session.get('lang', app.config['DEFAULT_LANGUAGE'])
    _ = TranslationHelper(lang)
    return {
        'now': datetime.utcnow,
        'format_datetime': format_datetime,
        'time_ago': time_ago,
        'truncate': truncate,
        '_': _,
        't': _,
        'current_lang': lang,
        'available_languages': app.config['LANGUAGES']
    }

register_blueprints(app)

with app.app_context():
    db.create_all()

def start_services():
    """Initialize background services (scheduler and Telegram bots)."""
    try:
        from services.scheduler_service import SchedulerService
        from services.telegram_service import TelegramService
        
        # Start the scheduler for automatic article collection and summary generation
        SchedulerService.init(fetch_hour=2, summary_hour=8)
        logger.info("Scheduler service started")
        
        # Start Telegram bots for all active journalists
        TelegramService.start_all_bots()
        logger.info("Telegram bots started")
        
        # Register cleanup on exit
        atexit.register(SchedulerService.shutdown)
        atexit.register(TelegramService.stop_all_bots)
        
    except Exception as e:
        logger.error(f"Error starting services: {e}")

# Start services when not in reloader child process
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
    start_services()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
