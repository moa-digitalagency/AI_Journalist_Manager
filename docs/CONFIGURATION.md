# Guide de configuration

## Variables d'environnement

Les variables suivantes doivent etre configurees dans le fichier `.env` ou via l'interface Replit :

### Base de donnees

| Variable | Description | Exemple |
|----------|-------------|---------|
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql://user:pass@host:5432/dbname` |

### Session Flask

| Variable | Description |
|----------|-------------|
| `SESSION_SECRET` | Cle secrete pour les sessions |

### APIs externes

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Cle API Google Gemini |
| `ELEVENLABS_API_KEY` | Cle API Eleven Labs |

### Administration

| Variable | Description | Defaut |
|----------|-------------|--------|
| `ADMIN_USERNAME` | Nom utilisateur admin initial | `admin` |
| `ADMIN_PASSWORD` | Mot de passe admin initial | (genere) |
| `ADMIN_EMAIL` | Email admin | `admin@example.com` |

## Configuration des journalistes

Chaque journaliste IA peut etre configure avec :

### Personnalite
- **Nom** : Nom d'affichage du journaliste
- **Style d'ecriture** : Formel, decontracte, technique, etc.
- **Ton** : Neutre, enthousiaste, critique, etc.
- **Langue** : Langue de redaction

### Bot Telegram
- **Token** : Token du bot genere par @BotFather
- **Username** : Nom d'utilisateur du bot

### Planification
- **Heure de resume** : Heure d'envoi du resume quotidien
- **Frequence de collecte** : Intervalle de scraping

## Configuration des sources

Types de sources supportes :

### Sites web
- URL de la page a scraper
- Selecteurs CSS pour le contenu

### Flux RSS
- URL du flux RSS

### Twitter/X
- Identifiant du compte a suivre
- Credentials API Twitter (si necessaire)

## Configuration des forfaits

Parametres configurables :
- **Nom** : Nom du forfait
- **Duree** : Duree en jours
- **Acces resume** : Oui/Non
- **Acces chat** : Oui/Non
- **Prix** : Montant (optionnel)
