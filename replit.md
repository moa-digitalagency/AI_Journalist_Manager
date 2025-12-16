# AI Journalist Manager

## Overview
Application de gestion de journalistes IA qui collectent des actualités, génèrent des résumés et les envoient via Telegram.

## Architecture

### Backend (Python/Flask)
- `app.py` - Application Flask principale avec API REST
- `models.py` - Modèles SQLAlchemy (Journalist, Source, Article, Subscriber, DailySummary)
- `config.py` - Configuration de l'application
- `ai_service.py` - Intégration Gemini pour génération de résumés
- `scraper.py` - Collecte des sources (RSS, websites)
- `audio_service.py` - Intégration Eleven Labs pour audio
- `telegram_bot.py` - Gestion des bots Telegram
- `scheduler.py` - Tâches automatiques (collecte + résumés)

### Frontend (HTML/Tailwind)
- `templates/` - Templates Jinja2
  - `base.html` - Layout de base
  - `index.html` - Tableau de bord
  - `journalist_form.html` - Formulaire création/édition journaliste
  - `journalist_detail.html` - Détails et gestion d'un journaliste

### Base de données PostgreSQL
Tables: journalists, sources, articles, subscribers, daily_summaries

## Fonctionnalités

1. **Création de journalistes IA** avec personnalité, style et ton configurables
2. **Gestion des sources** (RSS, sites web, Twitter/X)
3. **Collecte automatique** des actualités toutes les 24h
4. **Génération de résumés** avec Gemini AI
5. **Audio TTS** via Eleven Labs (optionnel)
6. **Envoi via Telegram** aux abonnés
7. **Gestion des abonnés** avec période d'essai

## Variables d'environnement requises

- `DATABASE_URL` - URL PostgreSQL (automatique)
- `GEMINI_API_KEY` - Clé API Google Gemini
- `ELEVEN_LABS_API_KEY` - Clé API Eleven Labs (optionnel)

## Démarrage

```bash
python app.py
```

Le serveur démarre sur le port 5000.
