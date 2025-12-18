import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from security.auth import admin_required
from security.logging import log_activity
from models import db, Settings

settings_bp = Blueprint('settings', __name__)

DEFAULT_SETTINGS = {
    'general': [
        {'key': 'app_name', 'value': 'AI Journalist Manager', 'description': 'Nom de l\'application'},
        {'key': 'default_language', 'value': 'fr', 'description': 'Langue par défaut (fr, en, es, de)'},
        {'key': 'trial_days', 'value': '7', 'description': 'Durée de la période d\'essai en jours'},
        {'key': 'fetch_hour', 'value': '2', 'description': 'Heure de collecte automatique (0-23)'},
        {'key': 'summary_hour', 'value': '8', 'description': 'Heure d\'envoi des résumés (0-23)'},
        {'key': 'default_timezone', 'value': 'Europe/Paris', 'description': 'Fuseau horaire par défaut'},
    ],
    'api': [
        {'key': 'default_ai_model', 'value': 'perplexity', 'description': 'Modèle IA par défaut (perplexity, gemini, openai, openrouter)'},
        {'key': 'gemini_model', 'value': 'gemini-2.5-flash', 'description': 'Modèle Gemini à utiliser'},
        {'key': 'eleven_labs_default_voice', 'value': '21m00Tcm4TlvDq8ikWAM', 'description': 'Voice ID Eleven Labs par défaut'},
        {'key': 'summary_max_length', 'value': '2000', 'description': 'Longueur maximale des résumés (caractères)'},
        {'key': 'youtube_transcript_languages', 'value': 'fr,en,es,de', 'description': 'Langues de transcription YouTube (priorité)'},
    ],
    'notifications': [
        {'key': 'enable_email_notifications', 'value': 'false', 'description': 'Activer les notifications par email'},
        {'key': 'admin_email', 'value': '', 'description': 'Email de l\'administrateur'},
        {'key': 'notify_on_new_subscriber', 'value': 'true', 'description': 'Notification lors d\'un nouvel abonné'},
        {'key': 'notify_on_error', 'value': 'true', 'description': 'Notification en cas d\'erreur'},
    ],
    'security': [
        {'key': 'max_login_attempts', 'value': '5', 'description': 'Nombre maximum de tentatives de connexion'},
        {'key': 'session_timeout', 'value': '60', 'description': 'Timeout de session en minutes'},
        {'key': 'require_email_verification', 'value': 'false', 'description': 'Exiger la vérification email'},
        {'key': 'log_all_activities', 'value': 'true', 'description': 'Journaliser toutes les activités'},
    ],
    'seo': [
        {'key': 'meta_title', 'value': 'AI Journalist Manager', 'description': 'Titre meta pour le SEO'},
        {'key': 'meta_description', 'value': 'Plateforme de gestion de journalistes IA', 'description': 'Description meta'},
        {'key': 'meta_keywords', 'value': 'ia, journaliste, actualités, telegram, bot', 'description': 'Mots-clés meta'},
    ],
}

def get_api_status():
    """Check the status of configured APIs."""
    # Check which AI models are configured
    gemini_configured = bool(os.environ.get('GEMINI_API_KEY'))
    perplexity_configured = bool(os.environ.get('PERPLEXITY_API_KEY'))
    openai_configured = bool(os.environ.get('OPENAI_API_KEY'))
    openrouter_configured = bool(os.environ.get('OPENROUTER_API_KEY'))
    
    # At least one AI model is required
    ai_model_required = not any([gemini_configured, perplexity_configured, openai_configured, openrouter_configured])
    
    status = {
        'gemini': {
            'configured': gemini_configured,
            'name': 'Google Gemini',
            'description': 'IA pour la génération de résumés',
            'required': False
        },
        'perplexity': {
            'configured': perplexity_configured,
            'name': 'Perplexity AI',
            'description': 'IA pour la génération de résumés et conversations',
            'required': False
        },
        'openai': {
            'configured': openai_configured,
            'name': 'OpenAI',
            'description': 'IA pour la génération de résumés',
            'required': False
        },
        'openrouter': {
            'configured': openrouter_configured,
            'name': 'OpenRouter',
            'description': 'Agrégateur d\'IA (multiple modèles)',
            'required': False
        },
        'eleven_labs': {
            'configured': bool(os.environ.get('ELEVEN_LABS_API_KEY')),
            'name': 'Eleven Labs',
            'description': 'Synthèse vocale (Text-to-Speech)',
            'required': False
        },
        'database': {
            'configured': bool(os.environ.get('DATABASE_URL')),
            'name': 'PostgreSQL',
            'description': 'Base de données',
            'required': True
        }
    }
    
    # Add a status message if no AI models are configured
    status['ai_requirement'] = {
        'required': ai_model_required,
        'message': 'Au moins un modèle IA doit être configuré' if ai_model_required else 'Modèle IA configuré'
    }
    
    return status

@settings_bp.route('/')
@admin_required
def index():
    categories = ['general', 'api', 'notifications', 'security', 'seo']
    all_settings = {}
    
    for cat in categories:
        all_settings[cat] = Settings.query.filter_by(category=cat).all()
    
    api_status = get_api_status()
    
    return render_template('admin/settings/index.html', 
                         settings=all_settings,
                         api_status=api_status,
                         default_settings=DEFAULT_SETTINGS)

@settings_bp.route('/initialize', methods=['POST'])
@admin_required
def initialize():
    """Initialize default settings if they don't exist."""
    count = 0
    for category, settings_list in DEFAULT_SETTINGS.items():
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
    log_activity('initialize_settings', details=f'Initialized {count} default settings')
    flash(f'{count} paramètres par défaut initialisés', 'success')
    return redirect(url_for('settings.index'))

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

@settings_bp.route('/api-status')
@admin_required
def api_status():
    """Return API status as JSON."""
    return jsonify(get_api_status())

@settings_bp.route('/test-gemini', methods=['POST'])
@admin_required
def test_gemini():
    """Test Gemini API connection."""
    from services.ai_service import AIService
    
    if not AIService.is_available():
        return jsonify({'success': False, 'message': 'Clé API Gemini non configurée'})
    
    try:
        client = AIService.get_client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Dis bonjour en une phrase."
        )
        if response.text:
            return jsonify({'success': True, 'message': 'Connexion Gemini réussie', 'response': response.text[:100]})
        return jsonify({'success': False, 'message': 'Réponse vide de Gemini'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@settings_bp.route('/test-perplexity', methods=['POST'])
@admin_required
def test_perplexity():
    """Test Perplexity API connection."""
    if not os.environ.get('PERPLEXITY_API_KEY'):
        return jsonify({'success': False, 'message': 'Clé API Perplexity non configurée'})
    
    try:
        import requests
        api_key = os.environ.get('PERPLEXITY_API_KEY')
        response = requests.post(
            "https://api.perplexity.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar-small-online",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 50
            },
            timeout=15
        )
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('choices'):
                    return jsonify({'success': True, 'message': 'Connexion Perplexity réussie'})
                return jsonify({'success': False, 'message': 'Réponse invalide de Perplexity'})
            except:
                return jsonify({'success': False, 'message': 'Réponse non-JSON de Perplexity'})
        elif response.status_code == 401:
            return jsonify({'success': False, 'message': 'Clé API Perplexity invalide'})
        else:
            return jsonify({'success': False, 'message': f'Erreur Perplexity: {response.status_code}'})
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'message': 'Timeout - Perplexity ne répond pas'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})


@settings_bp.route('/test-openai', methods=['POST'])
@admin_required
def test_openai():
    """Test OpenAI API connection."""
    if not os.environ.get('OPENAI_API_KEY'):
        return jsonify({'success': False, 'message': 'Clé API OpenAI non configurée'})
    
    try:
        import requests
        api_key = os.environ.get('OPENAI_API_KEY')
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Bonjour"}],
                "max_tokens": 50
            },
            timeout=10
        )
        if response.status_code == 200:
            return jsonify({'success': True, 'message': 'Connexion OpenAI réussie'})
        return jsonify({'success': False, 'message': f'Erreur: {response.status_code}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@settings_bp.route('/test-openrouter', methods=['POST'])
@admin_required
def test_openrouter():
    """Test OpenRouter API connection."""
    if not os.environ.get('OPENROUTER_API_KEY'):
        return jsonify({'success': False, 'message': 'Clé API OpenRouter non configurée'})
    
    try:
        import requests
        api_key = os.environ.get('OPENROUTER_API_KEY')
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "openrouter/auto",
                "messages": [{"role": "user", "content": "Bonjour"}],
                "max_tokens": 50
            },
            timeout=10
        )
        if response.status_code == 200:
            return jsonify({'success': True, 'message': 'Connexion OpenRouter réussie'})
        return jsonify({'success': False, 'message': f'Erreur: {response.status_code}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@settings_bp.route('/test-elevenlabs', methods=['POST'])
@admin_required
def test_elevenlabs():
    """Test Eleven Labs API connection."""
    from services.audio_service import AudioService
    
    if not AudioService.is_available():
        return jsonify({'success': False, 'message': 'Clé API Eleven Labs non configurée'})
    
    try:
        import requests
        api_key = os.environ.get('ELEVEN_LABS_API_KEY')
        response = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": api_key},
            timeout=10
        )
        if response.status_code == 200:
            voices = response.json().get('voices', [])
            return jsonify({
                'success': True, 
                'message': f'Connexion réussie - {len(voices)} voix disponibles'
            })
        return jsonify({'success': False, 'message': f'Erreur: {response.status_code}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@settings_bp.route('/test-telegram', methods=['POST'])
@admin_required
def test_telegram():
    """Test Telegram Bot API with all active journalists."""
    from models import Journalist
    import requests
    
    journalists = Journalist.query.filter_by(is_active=True).all()
    
    if not journalists:
        return jsonify({'success': False, 'message': 'Aucun journaliste actif configuré'})
    
    results = []
    for journalist in journalists:
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{journalist.telegram_token}/getMe",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_name = data.get('result', {}).get('username', 'Unknown')
                    results.append({'name': journalist.name, 'bot': bot_name, 'status': 'ok'})
                else:
                    results.append({'name': journalist.name, 'status': 'error', 'message': data.get('description', 'Erreur')})
            else:
                results.append({'name': journalist.name, 'status': 'error', 'message': f'HTTP {response.status_code}'})
        except Exception as e:
            results.append({'name': journalist.name, 'status': 'error', 'message': str(e)})
    
    ok_count = len([r for r in results if r['status'] == 'ok'])
    
    if ok_count == len(results):
        return jsonify({
            'success': True,
            'message': f'{ok_count} bot(s) Telegram connecté(s)',
            'details': results
        })
    elif ok_count > 0:
        return jsonify({
            'success': True,
            'message': f'{ok_count}/{len(results)} bot(s) fonctionnel(s)',
            'details': results
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Aucun bot Telegram fonctionnel',
            'details': results
        })
