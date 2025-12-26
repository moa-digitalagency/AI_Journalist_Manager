# AI Journalist Manager

## Vue d'ensemble

AI Journalist Manager est une webapp permettant de créer et gérer des "journalistes IA" pour la production automatisée de résumés d'actualités. La plateforme intègre **Telegram**, **Email (SMTP)**, et **WhatsApp (Twilio)** pour la diffusion et l'interaction avec les abonnés.

## Fonctionnalites principales

### Journalistes IA
- Création de journalistes virtuels avec personnalité configurable
- Collecte automatique des articles toutes les 24h (configurable)
- Génération de résumés quotidiens (texte et audio)
- Interaction en langage naturel avec les utilisateurs
- Recherche d'articles par date dans l'historique
- Soutien pour plusieurs modèles IA (Gemini, Perplexity, OpenAI, OpenRouter)

### Canaux de distribution multi-canal
- **Telegram** : Bot public, conversation naturelle, validation d'abonnement
- **Email** : Envoi SMTP avec HTML/texte, configuration personnalisée
- **WhatsApp** : Intégration Twilio, conversation naturelle, recherche par date
- Chaque journaliste peut utiliser 1, 2 ou 3 canaux simultanément

### Sources d'information
- Sites web (scraping)
- Flux RSS
- Comptes Twitter/X
- Chaînes YouTube (avec transcription)

### Gestion des abonnés
- Suivi automatique des nouveaux contacts (Telegram/WhatsApp)
- Validation et gestion des forfaits par admin
- Périodes d'essai configurables
- Support multi-canal (Telegram et/ou WhatsApp)
- Messages de validation pour comptes non approuvés

### Historique d'articles
- Conservation complète de tous les articles collectés
- Recherche par date (format DD/MM/YYYY ou YYYY-MM-DD)
- Accessible via bots Telegram et WhatsApp
- Accès admin via tableau de bord

### Panel administrateur
- Tableau de bord avec statistiques en temps réel
- Gestion des journalistes et canaux de livraison
- Configuration des sources d'information
- Gestion complète des abonnés (multi-canal)
- Logs d'activité et de sécurité
- Gestion des utilisateurs et rôles
- Paramètres de la plateforme

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Backend | Python / Flask |
| Frontend | HTML, CSS, Tailwind, JavaScript |
| Base de donnees | PostgreSQL |
| IA | Google Gemini, Perplexity, OpenAI, OpenRouter |
| Text-to-Speech | Eleven Labs |
| Communication | Telegram Bot API, Twilio WhatsApp, SMTP Email |
| Ordonnanceur | APScheduler (tâches quotidiennes) |

## Demarrage rapide

1. Configurer les variables d'environnement (voir `CONFIGURATION.md`)
2. Lancer l'application : `python app.py`
3. Accéder à l'interface : `http://localhost:5000`
4. Se connecter avec les identifiants admin
5. Créer un journaliste et configurer ses canaux de livraison

## Documentation complète

- [Architecture technique](ARCHITECTURE.md) - Structure du projet et flux de données
- [Guide de configuration](CONFIGURATION.md) - Variables d'environnement et configuration
- [Modèles de données](MODELS.md) - Schéma de base de données
- [Services](SERVICES.md) - Services métier et leurs méthodes
- [Documentation API](API.md) - Routes HTTP et webhooks
- [Guide utilisateur admin](USER_GUIDE.md) - Interface d'administration
- [Guide utilisateur](GUIDE_UTILISATEUR.md) - Guide pour les utilisateurs
- [WhatsApp Bot](WHATSAPP_BOT.md) - Configuration complète du bot WhatsApp avec Twilio
