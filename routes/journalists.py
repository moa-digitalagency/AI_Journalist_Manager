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
        from models import DeliveryChannel
        
        name = request.form.get('name')
        
        if not name:
            flash('Nom requis', 'error')
            return redirect(url_for('journalists.create'))
        
        import logging
        logger = logging.getLogger(__name__)
        
        photo_url = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename:
                filename = secure_filename(f"journalist_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{photo.filename}")
                os.makedirs('static/uploads/journalists', exist_ok=True)
                photo.save(os.path.join('static/uploads/journalists', filename))
                photo_url = f"/static/uploads/journalists/{filename}"
                logger.info(f"Photo uploaded: {photo_url}")
        
        if not photo_url:
            photo_url = request.form.get('photo_url')
        
        journalist = Journalist(
            name=name,
            photo_url=photo_url,
            personality=request.form.get('personality', 'Journaliste professionnel'),
            writing_style=request.form.get('writing_style', 'Clair et engageant'),
            spelling_style=request.form.get('spelling_style', 'standard'),
            tone=request.form.get('tone', 'neutral'),
            language=request.form.get('language', 'fr'),
            timezone=request.form.get('timezone', 'Europe/Paris'),
            eleven_labs_voice_id=request.form.get('eleven_labs_voice_id'),
            enable_eleven_labs='enable_eleven_labs' in request.form,
            ai_provider=request.form.get('ai_provider', 'gemini'),
            ai_model=request.form.get('ai_model', 'auto'),
            fetch_time=request.form.get('fetch_time', '02:00'),
            summary_time=request.form.get('summary_time', '08:00'),
            send_time=request.form.get('send_time', '08:00')
        )
        db.session.add(journalist)
        db.session.commit()
        
        # Handle delivery channels - Telegram (token only, everyone can message)
        if request.form.get('telegram_token'):
            telegram_channel = DeliveryChannel(
                journalist_id=journalist.id,
                channel_type='telegram',
                telegram_token=request.form.get('telegram_token'),
                is_active=True
            )
            db.session.add(telegram_channel)
            TelegramService.start_bot(journalist.id, request.form.get('telegram_token'))
        
        # Handle Email
        if request.form.get('email_address'):
            email_channel = DeliveryChannel(
                journalist_id=journalist.id,
                channel_type='email',
                email_address=request.form.get('email_address'),
                smtp_server=request.form.get('smtp_server'),
                smtp_port=int(request.form.get('smtp_port', 587)),
                smtp_username=request.form.get('smtp_username'),
                smtp_password=request.form.get('smtp_password'),
                is_active=True
            )
            db.session.add(email_channel)
        
        # Handle WhatsApp
        if request.form.get('whatsapp_phone_number'):
            whatsapp_channel = DeliveryChannel(
                journalist_id=journalist.id,
                channel_type='whatsapp',
                whatsapp_phone_number=request.form.get('whatsapp_phone_number'),
                whatsapp_api_key=request.form.get('whatsapp_api_key'),
                whatsapp_account_id=request.form.get('whatsapp_account_id'),
                is_active=True
            )
            db.session.add(whatsapp_channel)
        
        db.session.commit()
        
        log_activity('create_journalist', 'journalist', journalist.id, f'Created: {name}')
        flash('Journaliste créé avec canaux de livraison', 'success')
        return redirect(url_for('journalists.view', id=journalist.id))
    
    return render_template('admin/journalists/form.html', journalist=None, timezones=TIMEZONES)

@journalists_bp.route('/<int:id>')
@admin_required
def view(id):
    from zoneinfo import ZoneInfo
    from sqlalchemy import func
    from models import DeliveryChannel
    
    journalist = Journalist.query.get_or_404(id)
    sources = Source.query.filter_by(journalist_id=id).all()
    recent_articles = Article.query.filter_by(journalist_id=id).order_by(Article.fetched_at.desc()).limit(20).all()
    recent_summaries = DailySummary.query.filter_by(journalist_id=id).order_by(DailySummary.created_at.desc()).limit(5).all()
    delivery_channels = DeliveryChannel.query.filter_by(journalist_id=id).all()
    
    # Get current time in journalist's timezone
    try:
        tz = ZoneInfo(journalist.timezone or 'Europe/Paris')
    except:
        tz = ZoneInfo('Europe/Paris')
    
    now_local = datetime.now(tz)
    now_utc = datetime.utcnow()
    
    # Parse scheduled times
    fetch_hour, fetch_minute = map(int, journalist.fetch_time.split(':'))
    summary_hour, summary_minute = map(int, journalist.summary_time.split(':'))
    send_hour, send_minute = map(int, journalist.send_time.split(':'))
    
    # Calculate next scheduled times
    def get_next_time(hour, minute, reference_time):
        next_time = reference_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_time <= reference_time:
            next_time += timedelta(days=1)
        return next_time
    
    next_fetch = get_next_time(fetch_hour, fetch_minute, now_local)
    next_summary = get_next_time(summary_hour, summary_minute, now_local)
    next_send = get_next_time(send_hour, send_minute, now_local)
    
    # Get last events
    last_summary = DailySummary.query.filter_by(journalist_id=id).order_by(
        DailySummary.created_at.desc()
    ).first()
    
    last_summary_created = last_summary.created_at if last_summary else None
    last_summary_sent = last_summary.sent_at if last_summary else None
    
    # Get last fetch time
    last_fetch_source = Source.query.filter_by(journalist_id=id).order_by(
        Source.last_fetched_at.desc()
    ).first()
    last_fetch_time = last_fetch_source.last_fetched_at if last_fetch_source else None
    
    # Get today's statistics
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # Articles fetched today by source
    source_stats = []
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    for source in sources:
        articles_today = Article.query.filter_by(
            source_id=source.id
        ).filter(Article.fetched_at >= today_start).count()
        
        articles_week = Article.query.filter_by(
            source_id=source.id
        ).filter(Article.fetched_at >= week_ago).count()
        
        source_stats.append({
            'id': source.id,
            'url': source.url,
            'name': source.name,
            'source_type': source.source_type,
            'is_active': source.is_active,
            'last_fetched_at': source.last_fetched_at,
            'articles_today': articles_today,
            'articles_week': articles_week,
            'fetch_count': source.fetch_count,
            'error_count': source.error_count,
            'last_error': source.last_error
        })
    
    total_articles_today = sum([s['articles_today'] for s in source_stats])
    total_articles_week = Article.query.filter_by(
        journalist_id=id
    ).filter(Article.fetched_at >= week_ago).count()
    
    summaries_today = DailySummary.query.filter_by(journalist_id=id).filter(
        DailySummary.created_at >= today_start
    ).count()
    
    summaries_sent_today = DailySummary.query.filter_by(journalist_id=id).filter(
        DailySummary.sent_at >= today_start,
        DailySummary.sent_at.isnot(None)
    ).count()
    
    stats_data = {
        'now_local': now_local,
        'next_fetch': next_fetch,
        'next_summary': next_summary,
        'next_send': next_send,
        'last_fetch_time': last_fetch_time,
        'last_summary_created': last_summary_created,
        'last_summary_sent': last_summary_sent,
        'fetch_time': journalist.fetch_time,
        'summary_time': journalist.summary_time,
        'send_time': journalist.send_time,
        'source_stats': source_stats,
        'total_articles_today': total_articles_today,
        'total_articles_week': total_articles_week,
        'summaries_today': summaries_today,
        'summaries_sent_today': summaries_sent_today,
        'timezone': journalist.timezone
    }
    
    return render_template('admin/journalists/view.html', 
                         journalist=journalist,
                         sources=sources,
                         recent_articles=recent_articles,
                         recent_summaries=recent_summaries,
                         delivery_channels=delivery_channels,
                         stats=stats_data)

@journalists_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(id):
    from models import DeliveryChannel
    
    journalist = Journalist.query.get_or_404(id)
    
    if request.method == 'POST':
        old_active = journalist.is_active
        
        journalist.name = request.form.get('name', journalist.name)
        journalist.personality = request.form.get('personality', journalist.personality)
        journalist.writing_style = request.form.get('writing_style', journalist.writing_style)
        journalist.spelling_style = request.form.get('spelling_style', journalist.spelling_style)
        journalist.tone = request.form.get('tone', journalist.tone)
        journalist.language = request.form.get('language', journalist.language)
        journalist.timezone = request.form.get('timezone', journalist.timezone)
        journalist.eleven_labs_voice_id = request.form.get('eleven_labs_voice_id')
        journalist.enable_eleven_labs = 'enable_eleven_labs' in request.form
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
        else:
            new_photo_url = request.form.get('photo_url')
            if new_photo_url and new_photo_url != journalist.photo_url:
                journalist.photo_url = new_photo_url
        
        db.session.commit()
        
        # Update delivery channels
        # Telegram
        tg_channel = DeliveryChannel.query.filter_by(journalist_id=id, channel_type='telegram').first()
        if request.form.get('enable_telegram') and request.form.get('telegram_token'):
            if not tg_channel:
                tg_channel = DeliveryChannel(journalist_id=id, channel_type='telegram')
            tg_channel.telegram_token = request.form.get('telegram_token')
            tg_channel.is_active = True
            db.session.add(tg_channel)
            TelegramService.start_bot(journalist.id, request.form.get('telegram_token'))
        elif tg_channel:
            db.session.delete(tg_channel)
            TelegramService.stop_bot(journalist.id)
        
        # Email
        email_channel = DeliveryChannel.query.filter_by(journalist_id=id, channel_type='email').first()
        if request.form.get('enable_email') and request.form.get('email_address'):
            if not email_channel:
                email_channel = DeliveryChannel(journalist_id=id, channel_type='email')
            email_channel.email_address = request.form.get('email_address')
            email_channel.smtp_server = request.form.get('smtp_server')
            email_channel.smtp_port = int(request.form.get('smtp_port', 587))
            email_channel.smtp_username = request.form.get('smtp_username')
            email_channel.smtp_password = request.form.get('smtp_password')
            email_channel.is_active = True
            db.session.add(email_channel)
        elif email_channel:
            db.session.delete(email_channel)
        
        # WhatsApp
        wa_channel = DeliveryChannel.query.filter_by(journalist_id=id, channel_type='whatsapp').first()
        if request.form.get('enable_whatsapp') and request.form.get('whatsapp_phone_number'):
            if not wa_channel:
                wa_channel = DeliveryChannel(journalist_id=id, channel_type='whatsapp')
            wa_channel.whatsapp_phone_number = request.form.get('whatsapp_phone_number')
            wa_channel.whatsapp_api_key = request.form.get('whatsapp_api_key')
            wa_channel.whatsapp_account_id = request.form.get('whatsapp_account_id')
            wa_channel.is_active = True
            db.session.add(wa_channel)
        elif wa_channel:
            db.session.delete(wa_channel)
        
        db.session.commit()
        
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

@journalists_bp.route('/<int:id>/summary/text', methods=['POST'])
@admin_required
def generate_summary_text(id):
    """Generate text summary only (no audio)."""
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
    
    from services.ai_service import clean_html
    clean_summary = clean_html(summary_text)
    
    summary = DailySummary(
        journalist_id=id,
        summary_text=clean_summary,
        audio_url=None,
        articles_count=len(articles)
    )
    db.session.add(summary)
    journalist.last_summary_at = datetime.utcnow()
    db.session.commit()
    
    log_activity('generate_summary_text', 'journalist', id, f'Generated text summary from {len(articles)} articles')
    return jsonify({'message': f'Résumé texte généré avec {len(articles)} articles', 'summary': summary_text})

@journalists_bp.route('/<int:id>/summary/audio', methods=['POST'])
@admin_required
def generate_summary_audio(id):
    """Generate audio for the most recent text summary."""
    journalist = Journalist.query.get_or_404(id)
    
    # Get the most recent summary
    latest_summary = DailySummary.query.filter_by(journalist_id=id).order_by(DailySummary.created_at.desc()).first()
    
    if not latest_summary:
        return jsonify({'message': 'Aucun résumé texte trouvé. Générez d\'abord un résumé texte.'})
    
    if not journalist.enable_eleven_labs:
        return jsonify({'message': 'Eleven Labs n\'est pas activé pour ce journaliste'})
    
    if not journalist.eleven_labs_voice_id:
        return jsonify({'message': 'Veuillez configurer une voix Eleven Labs pour ce journaliste'})
    
    if not AudioService.is_available():
        return jsonify({'message': 'Service Eleven Labs non disponible'})
    
    # Generate audio from the summary text
    audio_data, error_msg = AudioService.generate_audio(latest_summary.summary_text, journalist.eleven_labs_voice_id)
    
    if audio_data:
        filename = f"summary_{id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp3"
        audio_path = AudioService.save_audio(audio_data, filename)
        
        # Update the summary with audio
        latest_summary.audio_url = audio_path
        db.session.commit()
        
        log_activity('generate_summary_audio', 'journalist', id, f'Generated audio summary')
        return jsonify({'message': 'Audio généré et sauvegardé avec succès'})
    else:
        return jsonify({'message': error_msg or 'Erreur lors de la génération audio'})

@journalists_bp.route('/<int:id>/summary', methods=['POST'])
@admin_required
def generate_summary(id):
    """Legacy endpoint - generates text summary only."""
    return generate_summary_text(id)

@journalists_bp.route('/<int:id>/summaries', methods=['GET'])
@admin_required
def summaries_history(id):
    journalist = Journalist.query.get_or_404(id)
    summaries = DailySummary.query.filter_by(journalist_id=id).order_by(DailySummary.created_at.desc()).all()
    return render_template('admin/journalists/summaries_history.html', journalist=journalist, summaries=summaries)
