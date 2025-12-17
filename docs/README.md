# AI Journalist Manager

## Vue d'ensemble

AI Journalist Manager est une webapp permettant de creer et gerer des "journalistes IA" pour la production automatisee de resumes d'actualites. La plateforme integre Telegram pour la diffusion et l'interaction avec les abonnes.

## Fonctionnalites principales

### Journalistes IA
- Creation de journalistes virtuels avec personnalite configurable
- Liaison avec des bots Telegram pour la communication
- Collecte automatique des actualites toutes les 24h
- Generation de resumes quotidiens (texte et audio)
- Interaction en langage naturel avec les utilisateurs

### Sources d'information
- Sites web (scraping)
- Flux RSS
- Comptes Twitter/X

### Gestion des abonnes
- Suivi automatique des nouveaux contacts
- Validation et gestion des forfaits
- Periodes d'essai configurables

### Panel administrateur
- Tableau de bord avec statistiques
- Gestion des bots journalistes
- Gestion des abonnes et forfaits
- Logs d'activite et securite
- Gestion des utilisateurs et roles
- Parametres de la plateforme

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Backend | Python / Flask |
| Frontend | HTML, CSS, Tailwind, JavaScript |
| Base de donnees | PostgreSQL |
| IA | Google Gemini |
| Text-to-Speech | Eleven Labs |
| Communication | Telegram Bot API |

## Demarrage rapide

1. Configurer les variables d'environnement (voir `CONFIGURATION.md`)
2. Lancer l'application : `python app.py`
3. Acceder a l'interface : `http://localhost:5000`
4. Se connecter avec les identifiants admin

## Documentation

- [Architecture technique](ARCHITECTURE.md)
- [Guide de configuration](CONFIGURATION.md)
- [Guide utilisateur](USER_GUIDE.md)
- [Documentation API](API.md)
- [Modeles de donnees](MODELS.md)
- [Services](SERVICES.md)
