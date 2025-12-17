# Documentation API

## Authentification

L'API utilise l'authentification par session Flask. Les utilisateurs doivent etre connectes pour acceder aux endpoints proteges.

---

## Routes publiques

### POST /login

Authentification d'un utilisateur.

**Parametres (form-data):**
- `username` : Nom d'utilisateur
- `password` : Mot de passe

**Reponse:** Redirection vers le tableau de bord ou page de login avec erreur.

### POST /logout

Deconnexion de l'utilisateur.

**Reponse:** Redirection vers la page de login.

---

## Routes Administration

### Dashboard

#### GET /admin/dashboard

Affiche le tableau de bord avec les statistiques.

**Reponse:** Page HTML du dashboard.

---

### Journalistes

#### GET /admin/journalists

Liste tous les journalistes.

#### GET /admin/journalists/new

Formulaire de creation d'un journaliste.

#### POST /admin/journalists/new

Cree un nouveau journaliste.

**Parametres:**
- `name` : Nom du journaliste
- `description` : Description
- `telegram_token` : Token du bot
- `personality` : Personnalite
- `writing_style` : Style d'ecriture
- `tone` : Ton
- `language` : Langue
- `summary_hour` : Heure du resume (0-23)

#### GET /admin/journalists/<id>

Affiche les details d'un journaliste.

#### GET /admin/journalists/<id>/edit

Formulaire de modification.

#### POST /admin/journalists/<id>/edit

Met a jour un journaliste.

#### POST /admin/journalists/<id>/delete

Supprime un journaliste.

#### POST /admin/journalists/<id>/sources

Ajoute une source au journaliste.

**Parametres:**
- `type` : Type de source (web/rss/twitter)
- `url` : URL ou identifiant
- `name` : Nom de la source
- `config` : Configuration JSON (optionnel)

---

### Abonnes

#### GET /admin/subscribers

Liste tous les abonnes.

#### GET /admin/subscribers/<id>

Details d'un abonne.

#### POST /admin/subscribers/<id>/assign-plan

Attribue un forfait a un abonne.

**Parametres:**
- `plan_id` : ID du forfait
- `end_date` : Date de fin (optionnel)

#### POST /admin/subscribers/<id>/suspend

Suspend l'abonnement.

---

### Forfaits

#### GET /admin/plans

Liste tous les forfaits.

#### GET /admin/plans/new

Formulaire de creation.

#### POST /admin/plans/new

Cree un forfait.

**Parametres:**
- `name` : Nom
- `description` : Description
- `duration_days` : Duree en jours
- `has_summary_access` : Acces resumes (bool)
- `has_chat_access` : Acces chat (bool)
- `price` : Prix (optionnel)

#### POST /admin/plans/<id>/edit

Met a jour un forfait.

#### POST /admin/plans/<id>/delete

Supprime un forfait.

---

### Logs

#### GET /admin/logs

Logs d'activite.

**Parametres query:**
- `level` : Filtrer par niveau
- `user_id` : Filtrer par utilisateur
- `date_from` : Date de debut
- `date_to` : Date de fin

#### GET /admin/logs/security

Logs de securite.

---

### Utilisateurs

#### GET /admin/users

Liste tous les utilisateurs.

#### GET /admin/users/new

Formulaire de creation.

#### POST /admin/users/new

Cree un utilisateur.

**Parametres:**
- `username` : Nom d'utilisateur
- `email` : Email
- `password` : Mot de passe
- `role` : Role

#### POST /admin/users/<id>/edit

Met a jour un utilisateur.

#### POST /admin/users/<id>/delete

Supprime un utilisateur.

---

### Parametres

#### GET /admin/settings

Affiche les parametres.

#### POST /admin/settings

Met a jour les parametres.

---

## Webhooks Telegram

### POST /api/telegram/<journalist_id>/webhook

Webhook pour recevoir les messages Telegram.

**Corps:** Update Telegram (JSON)

**Traitement:**
1. Verification du token
2. Identification de l'abonne
3. Traitement du message
4. Reponse via API Telegram
