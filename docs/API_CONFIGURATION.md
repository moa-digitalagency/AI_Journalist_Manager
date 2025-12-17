# Configuration des APIs - AI Journalist Manager

## Variables d'environnement requises

### Base de données (Automatique sur Replit)

| Variable | Description | Obligatoire |
|----------|-------------|-------------|
| `DATABASE_URL` | URL de connexion PostgreSQL | Oui |
| `PGHOST` | Hôte PostgreSQL | Auto |
| `PGPORT` | Port PostgreSQL | Auto |
| `PGUSER` | Utilisateur PostgreSQL | Auto |
| `PGPASSWORD` | Mot de passe PostgreSQL | Auto |
| `PGDATABASE` | Nom de la base de données | Auto |

### Sécurité

| Variable | Description | Obligatoire |
|----------|-------------|-------------|
| `SESSION_SECRET` | Clé secrète pour les sessions Flask | Oui |

### APIs externes

| Variable | Description | Obligatoire | Obtention |
|----------|-------------|-------------|-----------|
| `GEMINI_API_KEY` | Clé API Google Gemini pour l'IA | Oui | [Google AI Studio](https://aistudio.google.com/apikey) |
| `ELEVEN_LABS_API_KEY` | Clé API Eleven Labs pour la synthèse vocale | Non | [Eleven Labs](https://elevenlabs.io/api) |

---

## Configuration détaillée des APIs

### 1. Google Gemini (IA - Obligatoire)

**Utilisation dans l'application :**
- Génération des résumés d'actualités
- Réponses aux questions des utilisateurs
- Extraction de mots-clés des articles

**Comment obtenir la clé :**
1. Aller sur [Google AI Studio](https://aistudio.google.com/)
2. Créer un projet ou en sélectionner un existant
3. Cliquer sur "Get API Key"
4. Copier la clé générée

**Configuration :**
```bash
GEMINI_API_KEY=votre_cle_api_gemini
```

**Modèle utilisé :** `gemini-2.5-flash`

**Limites :**
- Rate limit: Dépend de votre plan Google AI
- Tokens: Maximum ~1M tokens par requête

---

### 2. Eleven Labs (Audio - Optionnel)

**Utilisation dans l'application :**
- Conversion text-to-speech des résumés
- Génération audio avec voix personnalisée

**Comment obtenir la clé :**
1. Créer un compte sur [Eleven Labs](https://elevenlabs.io/)
2. Aller dans Profile Settings > API
3. Copier votre clé API

**Configuration :**
```bash
ELEVEN_LABS_API_KEY=votre_cle_eleven_labs
```

**Voice ID :**
- Défaut: `21m00Tcm4TlvDq8ikWAM` (Rachel)
- Vous pouvez spécifier un Voice ID personnalisé par journaliste

**Modèle utilisé :** `eleven_multilingual_v2`

---

### 3. Telegram Bot (Par journaliste)

**Utilisation dans l'application :**
- Envoi des résumés aux abonnés
- Réception et réponse aux messages
- Gestion des abonnements

**Comment créer un bot :**
1. Ouvrir Telegram et chercher `@BotFather`
2. Envoyer `/newbot`
3. Suivre les instructions pour nommer votre bot
4. Copier le token fourni

**Configuration :**
- Le token est configuré par journaliste dans l'interface admin
- Chaque journaliste a son propre bot Telegram

---

## Paramètres configurables dans l'interface

### Section "API" des paramètres

| Paramètre | Description | Valeur par défaut |
|-----------|-------------|-------------------|
| `gemini_model` | Modèle Gemini à utiliser | gemini-2.5-flash |
| `eleven_labs_default_voice` | Voice ID par défaut | 21m00Tcm4TlvDq8ikWAM |
| `summary_max_length` | Longueur max des résumés | 2000 |

### Section "Général"

| Paramètre | Description | Valeur par défaut |
|-----------|-------------|-------------------|
| `app_name` | Nom de l'application | AI Journalist Manager |
| `default_language` | Langue par défaut | fr |
| `trial_days` | Durée période d'essai | 7 |
| `fetch_hour` | Heure de collecte | 2 |
| `summary_hour` | Heure des résumés | 8 |

### Section "Notifications"

| Paramètre | Description | Valeur par défaut |
|-----------|-------------|-------------------|
| `enable_email_notifications` | Activer emails | false |
| `admin_email` | Email admin | - |

### Section "Sécurité"

| Paramètre | Description | Valeur par défaut |
|-----------|-------------|-------------------|
| `max_login_attempts` | Tentatives max connexion | 5 |
| `session_timeout` | Timeout session (minutes) | 60 |
| `require_email_verification` | Vérification email | false |

---

## Vérification de la configuration

### Statut des APIs

L'application vérifie automatiquement :
- **Gemini API** : Affiché dans les paramètres (Configuré/Non configuré)
- **Eleven Labs API** : Affiché dans les paramètres (Configuré/Non configuré)
- **Database** : Connexion automatique

### Test manuel

Utilisez l'API de contrôle pour tester :

```bash
# Vérifier le statut des services
GET /api/services/status

# Déclencher manuellement la collecte
POST /api/services/fetch

# Déclencher manuellement les résumés
POST /api/services/summary
```

---

## Dépannage

### Gemini API ne fonctionne pas
1. Vérifiez que `GEMINI_API_KEY` est défini
2. Testez la clé sur Google AI Studio
3. Vérifiez les quotas de votre compte

### Eleven Labs audio non généré
1. Vérifiez que `ELEVEN_LABS_API_KEY` est défini
2. Vérifiez que le Voice ID est valide
3. Vérifiez les crédits sur votre compte Eleven Labs

### Bot Telegram ne répond pas
1. Vérifiez le token dans les paramètres du journaliste
2. Vérifiez que le bot est actif (is_active = true)
3. Consultez les logs pour les erreurs

---

## Support

Pour toute question sur la configuration, consultez la documentation complète dans le dossier `docs/`.
