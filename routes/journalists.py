from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from security.auth import admin_required
from security.logging import log_activity
from models import db, Journalist, Source, Article, DailySummary
from models.journalist import TIMEZONES
from services.scraper_service import ScraperService
from services.ai_service import AIService
from services.audio_service import AudioService
from services.telegram_service import TelegramService
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import asyncio
import os

journalists_bp = Blueprint('journalists', __name__)

@journalists_bp.route('/')
@admin_required
def index():
    journalists = Journalist.query.order_by(Journalist.created_at.desc()).all()
    return render_template('admin/journalists/index.html', journalists=journalists)

@journalists_bp.route('/new', methods=['GET', 'POST'])
@admin_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        telegram_token = request.form.get('telegram_token')
        
        if not name or not telegram_token:
            flash('Nom et token requis', 'error')
            return redirect(url_for('journalists.create'))
        
        if Journalist.query.filter_by(telegram_token=telegram_token).first():
            flash('Token déjà utilisé', 'error')
            return redirect(url_for('journalists.create'))
        
        photo_url = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename:
                filename = secure_filename(f"journalist_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{photo.filename}")
                os.makedirs('static/uploads/journalists', exist_ok=True)
                photo.save(os.path.join('static/uploads/journalists', filename))
                photo_url = f"/static/uploads/journalists/{filename}"
        
        if not photo_url:
            photo_url = TelegramService.get_bot_photo_url(telegram_token)
        
        journalist = Journalist(
            name=name,
            telegram_token=telegram_token,
            photo_url=photo_url,
            personality=request.form.get('personality', 'Journaliste professionnel'),
            writing_style=request.form.get('writing_style', 'Clair et engageant'),
            spelling_style=request.form.get('spelling_style', 'standard'),
            tone=request.form.get('tone', 'neutral'),
            language=request.form.get('language', 'fr'),
            timezone=request.form.get('timezone', 'Europe/Paris'),
            eleven_labs_voice_id=request.form.get('eleven_labs_voice_id'),
            ai_provider=request.form.get('ai_provider', 'gemini'),
            ai_model=request.form.get('ai_model', 'auto'),
            fetch_time=request.form.get('fetch_time', '02:00'),
            summary_time=request.form.get('summary_time', '08:00'),
            send_time=request.form.get('send_time', '08:00')
        )
        db.session.add(journalist)
        db.session.commit()
        
        # Automatically start Telegram bot if token is provided
        if journalist.telegram_token:
            TelegramService.start_bot(journalist.id, journalist.telegram_token)
        
        log_activity('create_journalist', 'journalist', journalist.id, f'Created: {name}')
        flash('Journaliste créé', 'success')
        return redirect(url_for('journalists.view', id=journalist.id))
    
    return render_template('admin/journalists/form.html', journalist=None, timezones=TIMEZONES)

@journalists_bp.route('/<int:id>')
@admin_required
def view(id):
    journalist = Journalist.query.get_or_404(id)
    sources = Source.query.filter_by(journalist_id=id).all()
    recent_articles = Article.query.filter_by(journalist_id=id).order_by(Article.fetched_at.desc()).limit(20).all()
    recent_summaries = DailySummary.query.filter_by(journalist_id=id).order_by(DailySummary.created_at.desc()).limit(5).all()
    
    return render_template('admin/journalists/view.html', 
                         journalist=journalist,
                         sources=sources,
                         recent_articles=recent_articles,
                         recent_summaries=recent_summaries)

@journalists_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(id):
    journalist = Journalist.query.get_or_404(id)
    
    if request.method == 'POST':
        old_token = journalist.telegram_token
        old_active = journalist.is_active
        
        journalist.name = request.form.get('name', journalist.name)
        journalist.telegram_token = request.form.get('telegram_token', journalist.telegram_token)
        journalist.personality = request.form.get('personality', journalist.personality)
        journalist.writing_style = request.form.get('writing_style', journalist.writing_style)
        journalist.spelling_style = request.form.get('spelling_style', journalist.spelling_style)
        journalist.tone = request.form.get('tone', journalist.tone)
        journalist.language = request.form.get('language', journalist.language)
        journalist.timezone = request.form.get('timezone', journalist.timezone)
        journalist.eleven_labs_voice_id = request.form.get('eleven_labs_voice_id')
        journalist.ai_provider = request.form.get('ai_provider', journalist.ai_provider)
        journalist.ai_model = request.form.get('ai_model', journalist.ai_model)
        journalist.fetch_time = request.form.get('fetch_time', journalist.fetch_time)
        journalist.summary_time = request.form.get('summary_time', journalist.summary_time)
        journalist.send_time = request.form.get('send_time', journalist.send_time)
        journalist.is_active = 'is_active' in request.form
        
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename:
                filename = secure_filename(f"journalist_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{photo.filename}")
                os.makedirs('static/uploads/journalists', exist_ok=True)
                photo.save(os.path.join('static/uploads/journalists', filename))
                journalist.photo_url = f"/static/uploads/journalists/{filename}"
        elif journalist.telegram_token != old_token:
            bot_photo = TelegramService.get_bot_photo_url(journalist.telegram_token)
            if bot_photo:
                journalist.photo_url = bot_photo
        
        db.session.commit()
        
        # Handle Telegram bot updates
        new_active = journalist.is_active
        if journalist.telegram_token:
            # Token changed or journalist was deactivated then reactivated
            if journalist.telegram_token != old_token or (not old_active and new_active):
                TelegramService.start_bot(journalist.id, journalist.telegram_token)
            # Journalist was deactivated
            elif old_active and not new_active:
                TelegramService.stop_bot(journalist.id)
        
        log_activity('update_journalist', 'journalist', id, f'Updated: {journalist.name}')
        flash('Journaliste mis à jour', 'success')
        return redirect(url_for('journalists.view', id=id))
    
    return render_template('admin/journalists/form.html', journalist=journalist, timezones=TIMEZONES)

@journalists_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete(id):
    journalist = Journalist.query.get_or_404(id)
    name = journalist.name
    
    # Stop Telegram bot if it's running
    TelegramService.stop_bot(id)
    
    db.session.delete(journalist)
    db.session.commit()
    log_activity('delete_journalist', 'journalist', id, f'Deleted: {name}')
    flash('Journaliste supprimé', 'success')
    return redirect(url_for('journalists.index'))

@journalists_bp.route('/<int:id>/source/add', methods=['POST'])
@admin_required
def add_source(id):
    journalist = Journalist.query.get_or_404(id)
    
    source = Source(
        journalist_id=id,
        source_type=request.form.get('source_type'),
        url=request.form.get('url'),
        name=request.form.get('name') or request.form.get('url')
    )
    db.session.add(source)
    db.session.commit()
    
    log_activity('add_source', 'source', source.id, f'Added to {journalist.name}')
    flash('Source ajoutée', 'success')
    return redirect(url_for('journalists.view', id=id))

@journalists_bp.route('/source/<int:source_id>/delete', methods=['POST'])
@admin_required
def delete_source(source_id):
    source = Source.query.get_or_404(source_id)
    journalist_id = source.journalist_id
    db.session.delete(source)
    db.session.commit()
    flash('Source supprimée', 'success')
    return redirect(url_for('journalists.view', id=journalist_id))

@journalists_bp.route('/<int:id>/fetch', methods=['POST'])
@admin_required
def fetch_sources(id):
    journalist = Journalist.query.get_or_404(id)
    fetched = 0
    
    for source in journalist.sources:
        if not source.is_active:
            continue
        
        articles_data = ScraperService.fetch_source(source.source_type, source.url)
        
        for data in articles_data:
            if data['url'] and Article.query.filter_by(journalist_id=id, url=data['url']).first():
                continue
            
            keywords = AIService.extract_keywords(
                f"{data['title']} {data['content']}", 
                provider=journalist.ai_provider if hasattr(journalist, 'ai_provider') else 'gemini',
                model=journalist.ai_model if hasattr(journalist, 'ai_model') else 'auto'
            )
            
            article = Article(
                journalist_id=id,
                source_id=source.id,
                title=data['title'],
                content=data['content'],
                url=data['url'],
                author=data['author'],
                published_at=data['published_at'],
                keywords=','.join(keywords)
            )
            db.session.add(article)
            fetched += 1
        
        source.last_fetched_at = datetime.utcnow()
        source.fetch_count += 1
    
    db.session.commit()
    log_activity('fetch_sources', 'journalist', id, f'Fetched {fetched} articles')
    return jsonify({'message': f'{fetched} articles récupérés'})

@journalists_bp.route('/<int:id>/summary', methods=['POST'])
@admin_required
def generate_summary(id):
    journalist = Journalist.query.get_or_404(id)
    
    yesterday = datetime.utcnow() - timedelta(days=1)
    articles = Article.query.filter(
        Article.journalist_id == id,
        Article.fetched_at >= yesterday
    ).all()
    
    if not articles:
        return jsonify({'message': 'Aucun article récent'})
    
    articles_data = [
        {'title': a.title, 'content': a.content, 'source': a.source.name if a.source else 'Unknown'}
        for a in articles
    ]
    
    summary_text = AIService.generate_summary(
        articles=articles_data,
        personality=journalist.personality,
        writing_style=journalist.writing_style,
        tone=journalist.tone,
        language=journalist.language,
        provider=journalist.ai_provider,
        model=journalist.ai_model
    )
    
    # Clean HTML from summary before audio generation
    from services.ai_service import clean_html
    clean_summary = clean_html(summary_text)
    
    audio_path = None
    if journalist.eleven_labs_voice_id and AudioService.is_available():
        audio_data = AudioService.generate_audio(clean_summary, journalist.eleven_labs_voice_id)
        if audio_data:
            filename = f"summary_{id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp3"
            audio_path = AudioService.save_audio(audio_data, filename)
    
    summary = DailySummary(
        journalist_id=id,
        summary_text=clean_summary,
        audio_url=audio_path,
        articles_count=len(articles)
    )
    db.session.add(summary)
    journalist.last_summary_at = datetime.utcnow()
    db.session.commit()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    sent = loop.run_until_complete(TelegramService.send_to_subscribers(id, summary_text, audio_path))
    loop.close()
    
    summary.sent_count = sent
    summary.sent_at = datetime.utcnow()
    db.session.commit()
    
    log_activity('generate_summary', 'journalist', id, f'Sent to {sent} subscribers')
    return jsonify({'message': f'Résumé envoyé à {sent} abonnés', 'summary': summary_text})

@journalists_bp.route('/<int:id>/summaries', methods=['GET'])
@admin_required
def summaries_history(id):
    journalist = Journalist.query.get_or_404(id)
    summaries = DailySummary.query.filter_by(journalist_id=id).order_by(DailySummary.created_at.desc()).all()
    return render_template('admin/journalists/summaries_history.html', journalist=journalist, summaries=summaries)
