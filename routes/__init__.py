from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.journalists import journalists_bp
from routes.subscribers import subscribers_bp
from routes.plans import plans_bp
from routes.logs import logs_bp
from routes.users import users_bp
from routes.settings import settings_bp
from routes.api import api_bp
from routes.journalist_stats import journalist_stats_bp
from routes.whatsapp import whatsapp_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(journalist_stats_bp, url_prefix='/admin/journalist-stats')
    app.register_blueprint(journalists_bp, url_prefix='/admin/journalists')
    app.register_blueprint(subscribers_bp, url_prefix='/admin/subscribers')
    app.register_blueprint(plans_bp, url_prefix='/admin/plans')
    app.register_blueprint(logs_bp, url_prefix='/admin/logs')
    app.register_blueprint(users_bp, url_prefix='/admin/users')
    app.register_blueprint(settings_bp, url_prefix='/admin/settings')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(whatsapp_bp)
