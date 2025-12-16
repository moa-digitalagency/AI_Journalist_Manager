import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from models import db, Journalist, Source, Subscriber, Article, DailySummary
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.context_processor
def utility_processor():
    return {'now': datetime.utcnow}

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    journalists = Journalist.query.all()
    return render_template('index.html', journalists=journalists)

@app.route('/journalist/new', methods=['GET', 'POST'])
def create_journalist():
    if request.method == 'POST':
        name = request.form.get('name')
        telegram_token = request.form.get('telegram_token')
        personality = request.form.get('personality', 'Professional and concise news reporter')
        writing_style = request.form.get('writing_style', 'Clear, factual, and engaging')
        tone = request.form.get('tone', 'neutral')
        language = request.form.get('language', 'fr')
        eleven_labs_voice_id = request.form.get('eleven_labs_voice_id')
        
        if not name or not telegram_token:
            flash('Nom et token Telegram requis', 'error')
            return redirect(url_for('create_journalist'))
        
        existing = Journalist.query.filter_by(telegram_token=telegram_token).first()
        if existing:
            flash('Ce token Telegram est déjà utilisé', 'error')
            return redirect(url_for('create_journalist'))
        
        journalist = Journalist(
            name=name,
            telegram_token=telegram_token,
            personality=personality,
            writing_style=writing_style,
            tone=tone,
            language=language,
            eleven_labs_voice_id=eleven_labs_voice_id
        )
        db.session.add(journalist)
        db.session.commit()
        
        flash('Journaliste créé avec succès', 'success')
        return redirect(url_for('view_journalist', journalist_id=journalist.id))
    
    return render_template('journalist_form.html', journalist=None)

@app.route('/journalist/<int:journalist_id>')
def view_journalist(journalist_id):
    journalist = Journalist.query.get_or_404(journalist_id)
    sources = Source.query.filter_by(journalist_id=journalist_id).all()
    subscribers = Subscriber.query.filter_by(journalist_id=journalist_id).all()
    recent_articles = Article.query.filter_by(journalist_id=journalist_id).order_by(Article.fetched_at.desc()).limit(20).all()
    
    return render_template('journalist_detail.html', 
                         journalist=journalist, 
                         sources=sources, 
                         subscribers=subscribers,
                         recent_articles=recent_articles)

@app.route('/journalist/<int:journalist_id>/edit', methods=['GET', 'POST'])
def edit_journalist(journalist_id):
    journalist = Journalist.query.get_or_404(journalist_id)
    
    if request.method == 'POST':
        journalist.name = request.form.get('name', journalist.name)
        journalist.telegram_token = request.form.get('telegram_token', journalist.telegram_token)
        journalist.personality = request.form.get('personality', journalist.personality)
        journalist.writing_style = request.form.get('writing_style', journalist.writing_style)
        journalist.tone = request.form.get('tone', journalist.tone)
        journalist.language = request.form.get('language', journalist.language)
        journalist.eleven_labs_voice_id = request.form.get('eleven_labs_voice_id')
        journalist.is_active = 'is_active' in request.form
        
        db.session.commit()
        flash('Journaliste mis à jour', 'success')
        return redirect(url_for('view_journalist', journalist_id=journalist.id))
    
    return render_template('journalist_form.html', journalist=journalist)

@app.route('/journalist/<int:journalist_id>/delete', methods=['POST'])
def delete_journalist(journalist_id):
    journalist = Journalist.query.get_or_404(journalist_id)
    db.session.delete(journalist)
    db.session.commit()
    flash('Journaliste supprimé', 'success')
    return redirect(url_for('index'))

@app.route('/journalist/<int:journalist_id>/source/add', methods=['POST'])
def add_source(journalist_id):
    journalist = Journalist.query.get_or_404(journalist_id)
    
    source_type = request.form.get('source_type')
    url = request.form.get('url')
    name = request.form.get('name', '')
    
    if not source_type or not url:
        flash('Type et URL requis', 'error')
        return redirect(url_for('view_journalist', journalist_id=journalist_id))
    
    source = Source(
        journalist_id=journalist_id,
        source_type=source_type,
        url=url,
        name=name or url
    )
    db.session.add(source)
    db.session.commit()
    
    flash('Source ajoutée', 'success')
    return redirect(url_for('view_journalist', journalist_id=journalist_id))

@app.route('/source/<int:source_id>/delete', methods=['POST'])
def delete_source(source_id):
    source = Source.query.get_or_404(source_id)
    journalist_id = source.journalist_id
    db.session.delete(source)
    db.session.commit()
    flash('Source supprimée', 'success')
    return redirect(url_for('view_journalist', journalist_id=journalist_id))

@app.route('/subscriber/<int:subscriber_id>/approve', methods=['POST'])
def approve_subscriber(subscriber_id):
    subscriber = Subscriber.query.get_or_404(subscriber_id)
    subscriber.is_approved = True
    subscriber.is_active = True
    db.session.commit()
    flash('Abonné approuvé', 'success')
    return redirect(url_for('view_journalist', journalist_id=subscriber.journalist_id))

@app.route('/subscriber/<int:subscriber_id>/revoke', methods=['POST'])
def revoke_subscriber(subscriber_id):
    subscriber = Subscriber.query.get_or_404(subscriber_id)
    subscriber.is_approved = False
    subscriber.is_active = False
    db.session.commit()
    flash('Accès révoqué', 'success')
    return redirect(url_for('view_journalist', journalist_id=subscriber.journalist_id))

@app.route('/subscriber/<int:subscriber_id>/extend', methods=['POST'])
def extend_trial(subscriber_id):
    subscriber = Subscriber.query.get_or_404(subscriber_id)
    days = int(request.form.get('days', 7))
    
    if subscriber.trial_end:
        subscriber.trial_end = subscriber.trial_end + timedelta(days=days)
    else:
        subscriber.trial_end = datetime.utcnow() + timedelta(days=days)
    
    db.session.commit()
    flash(f'Période d\'essai étendue de {days} jours', 'success')
    return redirect(url_for('view_journalist', journalist_id=subscriber.journalist_id))

@app.route('/api/journalist/<int:journalist_id>/fetch', methods=['POST'])
def trigger_fetch(journalist_id):
    from scraper import fetch_source
    from ai_service import extract_keywords
    
    journalist = Journalist.query.get_or_404(journalist_id)
    fetched_count = 0
    
    for source in journalist.sources:
        if not source.is_active:
            continue
        
        try:
            articles_data = fetch_source(source.source_type, source.url)
            
            for article_data in articles_data:
                existing = Article.query.filter_by(
                    journalist_id=journalist.id,
                    url=article_data['url']
                ).first() if article_data['url'] else None
                
                if not existing:
                    keywords = extract_keywords(f"{article_data['title']} {article_data['content']}")
                    
                    article = Article(
                        journalist_id=journalist.id,
                        source_id=source.id,
                        title=article_data['title'],
                        content=article_data['content'],
                        url=article_data['url'],
                        author=article_data['author'],
                        published_at=article_data['published_at'],
                        keywords=','.join(keywords)
                    )
                    db.session.add(article)
                    fetched_count += 1
            
            source.last_fetched_at = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'message': f'{fetched_count} nouveaux articles récupérés'})

@app.route('/api/journalist/<int:journalist_id>/summary', methods=['POST'])
def trigger_summary(journalist_id):
    from ai_service import generate_news_summary
    from audio_service import generate_audio, save_audio_file
    import asyncio
    from telegram_bot import send_summary_to_subscribers
    
    journalist = Journalist.query.get_or_404(journalist_id)
    
    yesterday = datetime.utcnow() - timedelta(days=1)
    articles = Article.query.filter(
        Article.journalist_id == journalist.id,
        Article.fetched_at >= yesterday
    ).all()
    
    if not articles:
        return jsonify({'message': 'Aucun nouvel article à résumer'})
    
    articles_data = [
        {
            'title': a.title,
            'content': a.content,
            'source': a.source.name if a.source else 'Unknown',
            'url': a.url
        }
        for a in articles
    ]
    
    summary_text = generate_news_summary(
        articles=articles_data,
        personality=journalist.personality,
        writing_style=journalist.writing_style,
        tone=journalist.tone,
        language=journalist.language
    )
    
    audio_path = None
    if journalist.eleven_labs_voice_id:
        audio_data = generate_audio(summary_text, journalist.eleven_labs_voice_id)
        if audio_data:
            filename = f"summary_{journalist.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp3"
            audio_path = save_audio_file(audio_data, filename)
    
    daily_summary = DailySummary(
        journalist_id=journalist.id,
        summary_text=summary_text,
        audio_url=audio_path
    )
    db.session.add(daily_summary)
    journalist.last_summary_at = datetime.utcnow()
    db.session.commit()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_summary_to_subscribers(journalist.id, summary_text, audio_path))
    loop.close()
    
    daily_summary.sent_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Résumé généré et envoyé', 'summary': summary_text})

if __name__ == '__main__':
    from scheduler import init_scheduler
    init_scheduler(app)
    app.run(host='0.0.0.0', port=5000, debug=True)
