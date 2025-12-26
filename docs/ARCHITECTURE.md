# Architecture technique

## Structure des dossiers

```
/
├── app.py                 # Point d'entree de l'application Flask
├── main.py                # Module de lancement
├── models/                # Modeles de base de donnees (SQLAlchemy)
│   ├── __init__.py
│   ├── activity_log.py    # Logs d'activite
│   ├── article.py         # Articles collectes
│   ├── daily_summary.py   # Resumes quotidiens
│   ├── delivery_channel.py # Canaux de livraison
│   ├── journalist.py      # Journalistes IA
│   ├── settings.py        # Parametres systeme
│   ├── source.py          # Sources d'information
│   ├── subscriber.py      # Abonnes
│   ├── subscription_plan.py # Forfaits
│   └── user.py            # Utilisateurs admin
├── routes/                # Routes Flask (endpoints)
│   ├── __init__.py
│   ├── admin.py           # Routes administration
│   ├── api.py             # Routes API
│   ├── auth.py            # Authentification
│   ├── journalists.py     # Gestion journalistes
│   ├── logs.py            # Consultation logs
│   ├── plans.py           # Gestion forfaits
│   ├── settings.py        # Parametres
│   ├── subscribers.py     # Gestion abonnes
│   └── users.py           # Gestion utilisateurs
├── security/              # Securite
│   ├── __init__.py
│   ├── auth.py            # Authentification/autorisation
│   └── logging.py         # Logging securise
├── services/              # Services metier
│   ├── __init__.py
│   ├── ai_service.py      # Integration Gemini
│   ├── audio_service.py   # Integration Eleven Labs
│   ├── delivery_service.py # Distribution multi-canal
│   ├── scheduler_service.py # Planification taches
│   ├── scraper_service.py # Collecte articles
│   └── telegram_service.py # Integration Telegram
├── templates/             # Templates HTML (Jinja2)
│   ├── admin/             # Templates admin
│   ├── auth/              # Templates authentification
│   └── base.html          # Template de base
├── utils/                 # Utilitaires
│   └── helpers.py         # Fonctions helper
└── docs/                  # Documentation
```

## Flux de donnees

### Collecte des articles

```
Sources (Web/RSS/Twitter)
        ↓
[Scraper Service] ← Scheduler (toutes les 24h)
        ↓
   Base de donnees (articles)
        ↓
   [AI Service] ← Generation resume
        ↓
   Base de donnees (daily_summary)
        ↓
[Delivery Service] ← Distribution multi-canal
   ├─ Telegram (bot public)
   ├─ Email (SMTP)
   └─ WhatsApp (Twilio)
```

### Interaction utilisateur

```
Utilisateur Telegram
        ↓
    Bot Telegram
        ↓
[Telegram Service] ← Reception message
        ↓
   [AI Service] ← Analyse et reponse
        ↓
    Bot Telegram
        ↓
Utilisateur Telegram
```

## Base de donnees

La base de donnees PostgreSQL contient les tables suivantes :

- **users** : Administrateurs de la plateforme
- **journalists** : Configuration des journalistes IA
- **sources** : Sources d'information par journaliste
- **articles** : Articles collectes
- **daily_summaries** : Resumes generes
- **delivery_channels** : Canaux de distribution (Telegram/Email/WhatsApp)
- **subscribers** : Abonnes des bots
- **subscription_plans** : Forfaits disponibles
- **activity_logs** : Historique d'activite
- **settings** : Parametres systeme

## Securite

- Authentification par session Flask
- Hash des mots de passe (Werkzeug)
- Gestion des roles (admin, superadmin)
- Logging de toutes les actions sensibles
- Protection CSRF sur les formulaires
