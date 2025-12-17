# Documentation des modeles de donnees

## User (Utilisateur)

Represente un administrateur de la plateforme.

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Identifiant unique |
| username | String(64) | Nom d'utilisateur |
| email | String(120) | Adresse email |
| password_hash | String(256) | Hash du mot de passe |
| role | String(20) | Role (superadmin/admin/operator) |
| is_active | Boolean | Compte actif |
| created_at | DateTime | Date de creation |
| last_login | DateTime | Derniere connexion |

## Journalist (Journaliste IA)

Configuration d'un journaliste virtuel.

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Identifiant unique |
| name | String(100) | Nom du journaliste |
| description | Text | Description |
| telegram_token | String(100) | Token du bot Telegram |
| telegram_username | String(64) | Username du bot |
| personality | Text | Personnalite configurable |
| writing_style | String(50) | Style d'ecriture |
| tone | String(50) | Ton de communication |
| language | String(10) | Langue |
| is_active | Boolean | Journaliste actif |
| summary_hour | Integer | Heure d'envoi resume (0-23) |
| created_at | DateTime | Date de creation |

## Source

Source d'information liee a un journaliste.

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Identifiant unique |
| journalist_id | Integer | FK vers Journalist |
| type | String(20) | Type (web/rss/twitter) |
| url | String(500) | URL ou identifiant |
| name | String(100) | Nom de la source |
| config | JSON | Configuration specifique |
| is_active | Boolean | Source active |
| last_fetch | DateTime | Derniere collecte |

## Article

Article collecte depuis une source.

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Identifiant unique |
| source_id | Integer | FK vers Source |
| journalist_id | Integer | FK vers Journalist |
| title | String(500) | Titre |
| content | Text | Contenu |
| url | String(500) | URL originale |
| published_at | DateTime | Date de publication |
| collected_at | DateTime | Date de collecte |
| metadata | JSON | Metadonnees |

## DailySummary (Resume quotidien)

Resume genere par un journaliste.

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Identifiant unique |
| journalist_id | Integer | FK vers Journalist |
| date | Date | Date du resume |
| text_content | Text | Contenu texte |
| audio_url | String(500) | URL du fichier audio |
| article_count | Integer | Nombre d'articles resumes |
| sent_at | DateTime | Date d'envoi |
| created_at | DateTime | Date de creation |

## Subscriber (Abonne)

Utilisateur abonne a un bot journaliste.

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Identifiant unique |
| journalist_id | Integer | FK vers Journalist |
| telegram_id | String(50) | ID Telegram |
| telegram_username | String(64) | Username Telegram |
| first_name | String(64) | Prenom |
| last_name | String(64) | Nom |
| plan_id | Integer | FK vers SubscriptionPlan |
| subscription_start | DateTime | Debut abonnement |
| subscription_end | DateTime | Fin abonnement |
| is_active | Boolean | Abonnement actif |
| created_at | DateTime | Premier contact |

## SubscriptionPlan (Forfait)

Definition d'un forfait d'abonnement.

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Identifiant unique |
| name | String(100) | Nom du forfait |
| description | Text | Description |
| duration_days | Integer | Duree en jours |
| has_summary_access | Boolean | Acces aux resumes |
| has_chat_access | Boolean | Acces au chat |
| price | Decimal | Prix (optionnel) |
| is_active | Boolean | Forfait disponible |

## ActivityLog (Log d'activite)

Historique des actions sur la plateforme.

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Identifiant unique |
| user_id | Integer | FK vers User (optionnel) |
| action | String(100) | Type d'action |
| description | Text | Description detaillee |
| ip_address | String(45) | Adresse IP |
| user_agent | String(500) | User agent |
| level | String(20) | Niveau (info/warning/error) |
| created_at | DateTime | Date de l'action |

## Settings (Parametres)

Parametres de configuration systeme.

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Identifiant unique |
| key | String(100) | Cle du parametre |
| value | Text | Valeur |
| type | String(20) | Type (string/int/bool/json) |
| category | String(50) | Categorie |
| description | Text | Description |
