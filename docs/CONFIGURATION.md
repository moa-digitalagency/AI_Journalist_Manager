# Guide de Configuration - AI Journalist Manager

## Vue d'ensemble

L'application utilise PostgreSQL pour la base de données et supporte plusieurs modèles IA (Gemini, Perplexity, OpenAI, OpenRouter) pour générer les résumés.

---

## Variables d'environnement

Toutes les variables doivent être configurées dans le **Secrets** de Replit.

### Essentielles (Requises)

| Variable | Description | Requis |
|----------|-------------|--------|
| `DATABASE_URL` | URL de connexion PostgreSQL | ✅ Oui |
| `SESSION_SECRET` | Clé secrète pour les sessions Flask | ✅ Oui |
| `ADMIN_USERNAME` | Nom d'utilisateur admin | ✅ Oui |
| `ADMIN_EMAIL` | Email de l'administrateur | ✅ Oui |
| `ADMIN_PASSWORD` | Mot de passe administrateur | ✅ Oui |

### Modèles IA (Au moins 1 requis)

| Variable | Provider | Modèle | Recommandé pour Journalistes |
|----------|----------|--------|------------------------------|
| `GEMINI_API_KEY` | Google Gemini | gemini-2.5-flash | ❌ |
| `PERPLEXITY_API_KEY` | Perplexity AI | sonar | ✅ **OUI** |
| `OPENAI_API_KEY` | OpenAI | gpt-4o-mini | ❌ |
| `OPENROUTER_API_KEY` | OpenRouter | auto (multi-modèles) | ❌ |

**Important:** Au moins un modèle IA doit être configuré pour que l'application fonctionne.

### Services Optionnels

| Variable | Service | Usage |
|----------|---------|-------|
| `ELEVEN_LABS_API_KEY` | Eleven Labs | Synthèse vocale (TTS) pour les résumés |

---

## Configuration des Journalistes IA

### Propriétés configurables

**Personnalité:**
- **Nom** : Nom d'affichage du journaliste
- **Personnalité** : Description de son caractère (ex: "Journaliste indépendant, critique")
- **Style d'écriture** : Formel, décontracté, technique, etc.
- **Ton** : Neutre, enthousiaste, critique, sarcastique, etc.
- **Langue** : Langue de rédaction des résumés (fr, en, es, de, etc.)

**IA & Modèle:**
- **Provider IA** : Choix du modèle (gemini, perplexity, openai, openrouter)
- **Modèle personnalisé** : Spécifier un modèle exact (ex: "gpt-4" pour OpenAI)

**Paramètres temporels:**
- **Fuseau horaire** : Le résumé est envoyé à l'heure locale du journaliste
- **Heure de résumé** : Heure d'envoi quotidien (ex: 08:00)

**Bot Telegram:**
- **Token** : Obtenu de @BotFather sur Telegram
- **Chat ID** : ID du chat privé du bot

**Audio (Optionnel):**
- **Eleven Labs Voice ID** : ID de la voix pour la synthèse vocale TTS

---

## Configuration des Sources

Types de sources supportées :

### RSS
- URL du flux RSS (ex: `https://example.com/feed.xml`)
- Collecte automatique toutes les 24h

### Sites Web
- URL de la page
- Sélecteurs CSS pour extraire le contenu
- Collecte automatique toutes les 24h

### Twitter/X
- Identifiant du compte (via Nitter pour éviter l'authentification)

### YouTube
- URL de la chaîne ou vidéo
- Transcription automatique en plusieurs langues (fr, en, es, de)

### Medium
- Sélection de publications Medium

---

## Configuration des Forfaits d'abonnement

### Paramètres

| Propriété | Description |
|-----------|-------------|
| Nom | Nom du forfait (ex: "Basic", "Premium") |
| Description | Description pour les utilisateurs |
| Durée | Durée en jours (ex: 30 pour mensuel) |
| Prix | Montant (optionnel, 0 pour gratuit/essai) |
| Essai gratuit | Marquer comme forfait d'essai |
| Résumés | Utilisateur reçoit les résumés quotidiens |
| Questions | Utilisateur peut poser des questions au bot |
| Audio | Utilisateur reçoit les résumés en audio |

### Forfaits par défaut

- **Essai Gratuit** : 7 jours (résumés + questions)
- **Basic** : 30 jours / 9.99€ (résumés + questions)
- **Premium** : 30 jours / 19.99€ (résumés + questions + audio)

---

## Paramètres de l'application

Accessibles via `/admin/settings/` :

### Général
- Nom de l'application
- Langue par défaut
- Fuseau horaire par défaut
- Durée de l'essai gratuit
- Heures de collecte et résumés

### API
- Modèle IA par défaut
- Modèle Gemini spécifique
- Voice ID Eleven Labs
- Longueur max des résumés
- Langues de transcription YouTube

### Notifications
- Notifications email (activé/désactivé)
- Email de l'admin
- Notifications nouvel abonné
- Notifications erreurs

### Sécurité
- Tentatives de connexion max
- Timeout de session (minutes)
- Vérification email requise
- Journalisation d'activité

### SEO
- Titre meta
- Description meta
- Mots-clés meta

---

## Fonctionnement avec Perplexity

### Pourquoi Perplexity ?

✅ **Recherche temps réel** : Perplexity accède à Internet en temps réel pour les actualités les plus récentes  
✅ **Idéal pour journalistes** : Peut trouver et synthétiser les dernières news automatiquement  
✅ **Moins cher** : Tarification compétitive par rapport à OpenAI  
✅ **Intégré** : Pleinement supporté avec tests API intégrés  

### Configuration complète

1. **Obtenir la clé API**
   - Allez sur https://www.perplexity.ai/
   - Créez un compte ou connectez-vous
   - Allez à https://www.perplexity.ai/api
   - Générez une clé API

2. **Configurer dans Replit**
   - Allez dans **Secrets**
   - Ajoutez `PERPLEXITY_API_KEY` avec votre clé

3. **Configurer dans l'application**
   - Allez dans `/admin/settings/`
   - Dans "Configuration API", sélectionnez "Perplexity AI" comme modèle par défaut
   - Testez avec le bouton "PPX"

4. **Créer un journaliste avec Perplexity**
   - Allez dans "Journalistes"
   - Créez un nouveau journaliste
   - Sélectionnez "perplexity" comme Provider IA
   - Laissez "auto" pour le modèle (utilise "sonar" par défaut)

### Vérification du fonctionnement

**Via le dashboard:**
- Allez dans `/admin/settings/`
- Section "Statut des APIs"
- Cliquez sur "Tester" pour Perplexity
- Vous verrez "Connexion Perplexity réussie" si configuré correctement

**Via les tâches:**
- `/api/services/fetch` : Lance la collecte des sources
- `/api/services/summary` : Force la génération des résumés avec Perplexity

---

## Vérification de la configuration

### Checklist de démarrage

- [ ] `DATABASE_URL` configuré
- [ ] `SESSION_SECRET` configuré  
- [ ] `ADMIN_*` configurés (USERNAME, EMAIL, PASSWORD)
- [ ] Au moins une clé IA configurée (idéalement `PERPLEXITY_API_KEY`)
- [ ] Connexion admin fonctionnelle (`/admin/`)
- [ ] Test API en `/admin/settings/` réussi
- [ ] Au moins 1 journaliste créé
- [ ] Au moins 1 source ajoutée au journaliste
- [ ] Forfait d'essai actif

### Troubleshooting

**"Identifiants incorrects" lors de la connexion**
- Vérifiez que `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` sont corrects
- Rafraîchissez la page (Ctrl+F5)

**"Clé API non configurée" en settings**
- Allez dans Secrets et vérifiez le nom exact de la variable
- Le scheduler à besoin d'au moins une clé IA

**Résumés ne sont pas générés**
- Vérifiez que le journaliste a au moins 1 source active
- Vérifiez que le fuseau horaire et l'heure de résumé sont corrects
- Testez manuellement via `/api/services/summary`

---

## Notes importantes

1. **Clés API sécurisées** - Toutes les clés sont stockées dans Secrets, jamais en .env
2. **Chaque journaliste a son IA** - Vous pouvez mixer Gemini, Perplexity, etc. pour différents journalistes
3. **Fuseaux horaires** - Chaque journaliste a son propre fuseau horaire, indépendant du serveur
4. **Essai gratuit** - Dure 7 jours par défaut, configurable
5. **Telegram requis** - Un token Telegram valide est nécessaire pour chaque journaliste
