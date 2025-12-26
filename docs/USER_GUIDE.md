# Guide utilisateur administrateur

## Connexion

1. Accéder à l'interface web
2. Entrer les identifiants administrateur
3. Cliquer sur "Se connecter"

## Tableau de bord

Le tableau de bord affiche :
- Nombre total de journalistes
- Nombre d'abonnés actifs
- Articles collectés aujourd'hui
- Résumés générés cette semaine
- Statistiques par canal de livraison
- Graphiques de tendances

## Gestion des journalistes

### Créer un journaliste

1. Menu latéral → "Journalistes"
2. Cliquer sur "Nouveau journaliste"
3. Remplir les informations :
   - **Nom** du journaliste
   - **Description**
   - **Personnalité** : Comment le journaliste se présente
   - **Style d'écriture** : Formel, décontracté, technique, etc.
   - **Ton** : Neutre, enthousiaste, critique, etc.
   - **Langue** : Langue de rédaction des résumés
   - **Fuseau horaire** : Heure locale pour les envois
   - **Modèle IA** : Choix du fournisseur (Gemini, Perplexity, OpenAI, etc.)

### Configurer les canaux de livraison

Les journalistes modernes supportent **3 canaux simultanément** :

#### Telegram (Bot Public)
1. Dans la fiche journaliste
2. Section "Canaux de livraison"
3. Ajouter **Telegram** :
   - Token bot (obtenu de @BotFather)
   - Automatiquement actif pour les bots publics

#### Email (SMTP)
1. Ajouter **Email** :
   - Adresse email destinataire
   - Serveur SMTP (ex: smtp.gmail.com)
   - Port SMTP (défaut: 587)
   - Identifiant SMTP
   - Mot de passe SMTP

#### WhatsApp (Twilio)
1. Ajouter **WhatsApp** :
   - Numéro de téléphone (+1234567890)
   - Account ID Twilio
   - API Key Twilio
   - [Guide complet de configuration Twilio](WHATSAPP_BOT.md)

### Configurer les sources

1. Ouvrir la fiche d'un journaliste
2. Section "Sources" (en bas)
3. Ajouter une source :
   - **Type** : Web, RSS, Twitter, YouTube
   - **URL** ou identifiant
   - **Nom** : Nom de la source
   - **Paramètres spécifiques** : Configuration selon le type
4. Sauvegarder

**Types de sources :**
- **Web** : URL d'un site d'actualités
- **RSS** : Flux RSS d'un site
- **Twitter/X** : Identifiant du compte
- **YouTube** : URL de la chaîne ou vidéo

### Personnaliser le style

Dans la fiche journaliste :
- **Personnalité** : Caractéristiques du journaliste
- **Style d'écriture** : Formel, décontracté, concis, détaillé...
- **Ton** : Neutre, enthousiaste, critique, sarcastique...
- **Langue** : fr (français), en (anglais), es (espagnol), de (allemand), etc.

## Gestion des abonnes

### Voir les abonnes

Menu lateral → "Abonnes"

Liste tous les utilisateurs ayant contacte un bot.

### Valider un abonne

1. Cliquer sur un abonne
2. Selectionner un forfait
3. Definir la date de fin
4. Valider

### Revoquer l'acces

1. Ouvrir la fiche abonne
2. Cliquer sur "Suspendre"
3. Confirmer

## Gestion des forfaits

### Creer un forfait

1. Menu lateral → "Forfaits"
2. "Nouveau forfait"
3. Configurer :
   - Nom
   - Duree
   - Fonctionnalites incluses
4. Sauvegarder

## Consultation des logs

### Logs d'activite

Menu lateral → "Logs" → "Activite"

Affiche toutes les actions effectuees.

### Logs de securite

Menu lateral → "Logs" → "Securite"

Affiche les connexions et tentatives d'acces.

## Gestion des utilisateurs

### Creer un administrateur

1. Menu lateral → "Utilisateurs"
2. "Nouvel utilisateur"
3. Remplir les informations
4. Attribuer un role
5. Valider

### Roles disponibles

- **Superadmin** : Acces complet
- **Admin** : Gestion courante
- **Operateur** : Consultation seule

## Parametres

### Configuration generale

- Nom de la plateforme
- Email de contact
- Fuseau horaire

### SEO

- Titre du site
- Description
- Mots-cles
