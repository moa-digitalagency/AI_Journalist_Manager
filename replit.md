# AI Journalist Manager

## Overview
Application complète de gestion de journalistes IA avec panneau d'administration professionnel. Permet de créer des bots Telegram qui collectent des actualités, génèrent des résumés avec IA et les envoient aux abonnés.

## Architecture

### Backend (Python/Flask)
- `app.py` - Application Flask principale
- `models/` - Modèles SQLAlchemy
  - `user.py` - Utilisateurs et rôles admin
  - `journalist.py` - Journalistes IA
  - `source.py` - Sources d'actualités
  - `article.py` - Articles collectés
  - `subscriber.py` - Abonnés Telegram
  - `subscription_plan.py` - Forfaits d'abonnement
  - `daily_summary.py` - Résumés générés
  - `activity_log.py` - Logs d'activité
  - `settings.py` - Paramètres plateforme
- `routes/` - Blueprints Flask
  - `auth.py` - Authentification
  - `admin.py` - Dashboard
  - `journalists.py` - CRUD journalistes
  - `subscribers.py` - Gestion abonnés
  - `plans.py` - Forfaits
  - `logs.py` - Journaux
  - `users.py` - Utilisateurs admin
  - `settings.py` - Paramètres
  - `api.py` - API REST
- `services/` - Services métier
  - `ai_service.py` - Intégration Gemini
  - `scraper_service.py` - Collecte sources
  - `audio_service.py` - Eleven Labs TTS
  - `telegram_service.py` - Bot Telegram
  - `scheduler_service.py` - Tâches planifiées
- `security/` - Sécurité
  - `auth.py` - Décorateurs d'authentification
  - `logging.py` - Journalisation activités

### Frontend (HTML/Tailwind)
- `templates/admin/` - Interface d'administration
  - `base.html` - Layout avec sidebar bleu foncé
  - `dashboard.html` - Tableau de bord
  - `journalists/` - Gestion bots
  - `subscribers/` - Gestion abonnés
  - `plans/` - Forfaits
  - `logs/` - Journaux
  - `users/` - Utilisateurs admin
  - `settings/` - Paramètres

### Base de données PostgreSQL
Tables: users, roles, journalists, sources, articles, subscribers, subscription_plans, daily_summaries, activity_logs, settings

## Fonctionnalités

1. **Authentification admin** avec rôles (Admin, Editor, Viewer)
2. **Dashboard** avec statistiques et graphiques
3. **Gestion journalistes IA** - Création avec personnalité, style, ton, langue
4. **Gestion sources** - RSS, sites web, Twitter/X (via nitter), YouTube (avec transcription automatique)
5. **Collecte automatique** des actualités toutes les 24h (2:00 AM)
6. **Génération résumés** avec Gemini AI chaque matin (8:00 AM)
7. **Audio TTS** via Eleven Labs (génération automatique si configuré)
8. **Envoi Telegram** automatique aux abonnés actifs
9. **Conversation IA** - Les utilisateurs peuvent poser des questions, le bot recherche dans les articles
10. **Gestion abonnés** avec forfaits et périodes d'essai (7 jours par défaut)
11. **Logs** d'activité et de sécurité
12. **Paramètres** configurables par catégorie

## Services automatiques

- **Scheduler** : Démarre automatiquement au lancement de l'application
  - Collecte des sources à 2:00 AM
  - Génération et envoi des résumés à 8:00 AM
- **Bots Telegram** : Démarrent automatiquement pour chaque journaliste actif
  - Commandes : /start, /help, /status, /latest
  - Réponses en langage naturel avec recherche dans les articles

## API de contrôle

- `POST /api/services/fetch` - Déclencher manuellement la collecte
- `POST /api/services/summary` - Déclencher manuellement les résumés
- `POST /api/services/bot/<id>/start` - Démarrer un bot
- `POST /api/services/bot/<id>/stop` - Arrêter un bot
- `GET /api/services/status` - État des services

## Variables d'environnement

- `DATABASE_URL` - URL PostgreSQL (automatique sur Replit)
- `GEMINI_API_KEY` - Clé API Google Gemini (requis)
- `ELEVEN_LABS_API_KEY` - Clé API Eleven Labs (optionnel)

## Compte admin par défaut

- Username: `admin`
- Email: `admin@example.com`
- Password: `admin123`

## Design

- Couleur principale: Bleu foncé (#172554 à #1e3a8a)
- Framework CSS: Tailwind via CDN
- Icônes: Font Awesome
- Graphiques: Chart.js

## Démarrage

```bash
python app.py
```

Le serveur démarre sur le port 5000.
