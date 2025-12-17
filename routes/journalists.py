from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from security.auth import admin_required
from security.logging import log_activity
from models import db, Journalist, Source, Article, DailySummary
from services.scraper_service import ScraperService
from services.ai_service import AIService
from services.audio_service import AudioService
from services.telegram_service import TelegramService
from datetime import datetime, timedelta
import asyncio

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
        
        journalist = Journalist(
            name=name,
            telegram_token=telegram_token,
            personality=request.form.get('personality', 'Journaliste professionnel'),
            writing_style=request.form.get('writing_style', 'Clair et engageant'),
            spelling_style=request.form.get('spelling_style', 'standard'),
            tone=request.form.get('tone', 'neutral'),
            language=request.form.get('language', 'fr'),
            timezone=request.form.get('timezone', 'Europe/Paris'),
            eleven_labs_voice_id=request.form.get('eleven_labs_voice_id'),
            summary_time=request.form.get('summary_time', '08:00')
        )
        db.session.add(journalist)
        db.session.commit()
        
        log_activity('create_journalist', 'journalist', journalist.id, f'Created: {name}')
        flash('Journaliste créé', 'success')
        return redirect(url_for('journalists.view', id=journalist.id))
    
    return render_template('admin/journalists/form.html', journalist=None)

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
        journalist.name = request.form.get('name', journalist.name)
        journalist.telegram_token = request.form.get('telegram_token', journalist.telegram_token)
        journalist.personality = request.form.get('personality', journalist.personality)
        journalist.writing_style = request.form.get('writing_style', journalist.writing_style)
        journalist.spelling_style = request.form.get('spelling_style', journalist.spelling_style)
        journalist.tone = request.form.get('tone', journalist.tone)
        journalist.language = request.form.get('language', journalist.language)
        journalist.timezone = request.form.get('timezone', journalist.timezone)
        journalist.eleven_labs_voice_id = request.form.get('eleven_labs_voice_id')
        journalist.summary_time = request.form.get('summary_time', journalist.summary_time)
        journalist.is_active = 'is_active' in request.form
        
        db.session.commit()
        log_activity('update_journalist', 'journalist', id, f'Updated: {journalist.name}')
        flash('Journaliste mis à jour', 'success')
        return redirect(url_for('journalists.view', id=id))
    
    return render_template('admin/journalists/form.html', journalist=journalist)

@journalists_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete(id):
    journalist = Journalist.query.get_or_404(id)
    name = journalist.name
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
            
            article = Article(
                journalist_id=id,
                source_id=source.id,
                title=data['title'],
                content=data['content'],
                url=data['url'],
                author=data['author'],
                published_at=data['published_at'],
                keywords=','.join(AIService.extract_keywords(f"{data['title']} {data['content']}"))
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
        language=journalist.language
    )
    
    audio_path = None
    if journalist.eleven_labs_voice_id and AudioService.is_available():
        audio_data = AudioService.generate_audio(summary_text, journalist.eleven_labs_voice_id)
        if audio_data:
            filename = f"summary_{id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp3"
            audio_path = AudioService.save_audio(audio_data, filename)
    
    summary = DailySummary(
        journalist_id=id,
        summary_text=summary_text,
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
