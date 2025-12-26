# Configuration WhatsApp Bot - Guide Complet

## 🎯 Vue d'ensemble

Le bot WhatsApp permet de distribuer des résumés et d'interagir avec les abonnés sur WhatsApp, similaire au bot Telegram. Les utilisateurs peuvent :
- Recevoir les résumés quotidiens automatiquement
- Poser des questions en langage naturel
- Rechercher des articles par date
- Être validés par un administrateur avant l'accès

---

## 📋 Prérequis

- **Compte Twilio** (gratuit ou payant)
- **Numéro de téléphone Twilio** (ou number WhatsApp Business)
- **Credentials Twilio** (Account SID, Auth Token)
- **URL publique** de votre app (pour le webhook)

---

## 🚀 Étape 1 : Créer un compte Twilio

### 1.1 Inscription

1. Aller sur [twilio.com](https://www.twilio.com)
2. Cliquer sur **"Sign Up"** (gratuit)
3. Remplir le formulaire avec :
   - Email
   - Mot de passe
   - Nom complet
4. Vérifier votre email et confirmer

### 1.2 Vérification du téléphone

1. Twilio vous demandera de vérifier un numéro de téléphone
2. Entrer votre numéro au format international : `+33612345678` (France)
3. Recevoir un code par SMS
4. Entrer le code pour confirmer

### 1.3 Accéder au Tableau de bord Twilio

1. Une fois connecté, vous arrivez sur le **Twilio Console**
2. Vous verrez votre **Account SID** et **Auth Token** (les sauvegarder !)
3. C'est ici qu'on configurera WhatsApp

---

## 📱 Étape 2 : Configurer WhatsApp sur Twilio

### 2.1 Activer WhatsApp

1. Sur le **Twilio Console**, chercher **"Messaging"** → **"Try it out"** ou **"Messaging"** → **"Services"**
2. Ou directement : aller à [console.twilio.com/us/account/messaging/services](https://console.twilio.com/us/account/messaging/services)
3. Cliquer sur **"Explore Products"** → **"Messaging"**
4. Chercher **"WhatsApp"** dans le menu à gauche

### 2.2 Configurer le sandbox WhatsApp (Gratuit - Pour test)

**Pour tester rapidement :**

1. Aller à **Messaging** → **Try it Out** → **WhatsApp**
2. Vous verrez un **Sandbox WhatsApp** pré-configuré
3. **Numéro Twilio WhatsApp** : quelque chose comme `+1(XXX) XXX-XXXX`
4. Pour envoyer un message test :
   - Ouvrir WhatsApp
   - Envoyer `join <code>` au numéro Twilio
   - Exemple : `join rapid-lion` (le code sera affiché dans Twilio)

### 2.3 Configurer WhatsApp Business (Production)

**Pour utiliser en production avec votre propre numéro :**

1. Aller à **Messaging** → **WhatsApp Senders**
2. Cliquer **"Create Sender"**
3. Remplir les informations :
   - Nom de l'entreprise
   - Catégorie
   - Numéro de téléphone (votre numéro business)
4. Twilio vous guidera pour :
   - Vérifier le numéro
   - Obtenir l'approbation de Meta/WhatsApp
5. Une fois approuvé, vous aurez accès à votre numéro business

---

## 🔑 Étape 3 : Obtenir les Credentials

### 3.1 Account SID et Auth Token

1. Aller au [Twilio Console](https://console.twilio.com)
2. En haut, vous verrez :
   ```
   Account SID: ACxxxxxxxxxxxxxxxxxxxxxxxxx
   Auth Token: (cliquer sur l'œil pour afficher)
   ```
3. **Les copier et les sauvegarder** (vous les utiliserez dans la config)

### 3.2 Numéro WhatsApp

1. Si vous utilisez le **Sandbox** : le numéro est affiché dans Messaging → WhatsApp
2. Si vous avez **WhatsApp Business** : le numéro sera affiché après approbation

---

## 🔗 Étape 4 : Configurer le Webhook

### 4.1 Obtenir votre URL publique

Votre app doit être **accessible publiquement** depuis Internet.

**Sur Replit :**
- L'URL publique est automatiquement générée
- Format : `https://[project-name].replit.dev`

**Sur votre serveur :**
- Utiliser votre domaine ou adresse IP publique
- S'assurer que le port 5000 est exposé (ou votre port)

### 4.2 URL du webhook

L'URL du webhook pour le **journaliste N°1** serait :
```
https://[votre-domain]/whatsapp/webhook/1
```

Remplacer :
- `[votre-domain]` par votre URL publique
- `1` par l'ID du journaliste (visible dans l'admin)

### 4.3 Configurer dans Twilio

1. Aller à **Messaging** → **Settings** → **WhatsApp**
2. Ou **Phone Numbers** → sélectionner votre numéro → **Webhooks**
3. Chercher **"When a message comes in"**
4. Entrer votre URL du webhook :
   ```
   https://[votre-domain]/whatsapp/webhook/1
   ```
5. **Cocher** "Use webhook"
6. Sauvegarder

### 4.5 (Optionnel) Configurer les webhooks de statut

Pour suivre si les messages sont livrés/lus :

1. **When message status changes** : entrer la même URL
2. Sauvegarder

---

## ⚙️ Étape 5 : Configurer dans AI Journalist Manager

### 5.1 Créer/Modifier un Journaliste

1. Aller à `/admin/journalists/`
2. Créer ou modifier un journaliste
3. Aller à la section **"Canaux de livraison"**
4. Cliquer **"Ajouter WhatsApp"**

### 5.2 Remplir les informations WhatsApp

```
Numéro de téléphone WhatsApp : +1234567890
    (Format international, avec le +)

Account ID Twilio : ACxxxxxxxxxxxxxxxxxxxxxxxxx
    (Votre Account SID du dashboard Twilio)

API Key Twilio : 89xxxxxxxxxxxxxxxxxxxxxxxxx
    (Votre Auth Token du dashboard Twilio)
```

### 5.3 Tester

1. Depuis WhatsApp sur votre téléphone
2. Envoyer un message au numéro Twilio WhatsApp
3. Si bien configuré, le bot devrait répondre

---

## 💬 Utilisation du Bot WhatsApp

### Commandes disponibles

- **`/latest`** - Récupère le dernier résumé
- **`/articles DD/MM/YYYY`** - Recherche les articles d'une date spécifique
- **Texte libre** - Question en langage naturel

### Exemples

```
Utilisateur : /latest
Bot : [Envoie le dernier résumé généré]

Utilisateur : /articles 26/12/2025
Bot : [Affiche les articles du 26/12/2025]

Utilisateur : Qu'y a-t-il de nouveau en intelligence artificielle ?
Bot : [Recherche dans les articles et répond]
```

### Validation des abonnés

- **Nouveau utilisateur** : Automatiquement créé comme "non approuvé"
- **Message reçu** : Le bot notifie que l'accès est en attente d'approbation
- **Admin approuve** : Va dans `/admin/subscribers/`, trouve l'utilisateur, marque "approuvé"
- **Ensuite** : L'utilisateur peut utiliser le bot normalement

---

## 🛠️ Dépannage

### "Le webhook ne reçoit pas de messages"

1. Vérifier que l'URL du webhook est correcte dans Twilio
2. Tester l'URL publiquement : aller sur `https://votre-domain/whatsapp/webhook/1`
   - Devrait retourner `403 Forbidden` (c'est normal, pas de GET)
3. Vérifier les logs de Twilio (Console → Message Logs)
4. Vérifier les logs de votre app (`/admin/logs/`)

### "Messages d'erreur 'Unauthorized' ou 'Forbidden'"

1. Vérifier le token dans Twilio Console (peut avoir changé)
2. Vérifier que le Account SID est correct
3. Twilio peut regénérer l'Auth Token - utiliser le nouveau

### "Le bot ne répond pas"

1. Vérifier que le journaliste est **actif**
2. Vérifier que le journaliste a au moins **1 source active**
3. Vérifier que le modèle IA est configuré
4. Regarder les logs : `/admin/logs/`

### "Le webhook retourne une erreur 500"

1. Regarder dans `/admin/logs/` pour l'erreur exacte
2. Vérifier que tous les champs WhatsApp sont remplis
3. Vérifier que le journaliste existe (id correct dans l'URL du webhook)

---

## 💰 Coûts Twilio

### Gratuit (avec crédit d'essai)
- Twilio donne $15 de crédit d'essai
- Sandbox WhatsApp : **gratuit pour tester**
- Idéal pour développement/test

### Production
- **WhatsApp Message Template** : ~$0.003 par message
- **Inbound Message** : ~$0.0085 par message
- **Coûts varient par région**

Voir [Twilio Pricing](https://www.twilio.com/pricing) pour détails complets.

---

## 📊 Monitorer les messages

### Via Twilio Console

1. **Messaging** → **Logs** → **Message Logs**
2. Vous verrez tous les messages envoyés/reçus
3. Statuts : Queued, Failed, Sent, Delivered, Undelivered, Read

### Via AI Journalist Manager

1. `/admin/logs/` - Tous les logs d'activité
2. Rechercher les messages WhatsApp
3. Voir les erreurs et succès

---

## 🔒 Sécurité

- **Ne jamais** partager votre Auth Token
- **Stocker** dans Replit Secrets, pas en .env
- **Webhooks** vérifiés par token (voir `routes/whatsapp.py`)
- **Abonnés** doivent être approuvés par admin

---

## 📞 Support

- **Twilio Help** : [support.twilio.com](https://support.twilio.com)
- **Documentation Twilio WhatsApp** : [twilio.com/docs/whatsapp](https://www.twilio.com/docs/whatsapp)
- **Vérifier les logs** : `/admin/logs/` dans votre app
- **Contactez l'admin** de votre instance AI Journalist Manager

---

## 🎓 Résumé de la configuration

| Étape | Action |
|-------|--------|
| 1 | Créer compte Twilio (gratuit) |
| 2 | Activer WhatsApp (Sandbox ou Business) |
| 3 | Copier Account SID et Auth Token |
| 4 | Configurer webhook dans Twilio |
| 5 | Ajouter WhatsApp à un journaliste |
| 6 | Tester en envoyant un message |
| 7 | Admin approuve le nouvel utilisateur |
| 8 | Utilisateur peut utiliser le bot |

---

*Guide mis à jour : Décembre 2025*  
*AI Journalist Manager v1.0 - WhatsApp Integration*
