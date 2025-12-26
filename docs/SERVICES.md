# Documentation des services

## AI Service (`services/ai_service.py`)

Service d'integration avec Google Gemini pour la generation de contenu.

### Fonctionnalites

- Generation de resumes d'actualites
- Reponses aux questions des utilisateurs
- Analyse de mots-cles dans les articles

### Methodes principales

```python
def generate_summary(articles: list, journalist: Journalist) -> str
```
Genere un resume a partir d'une liste d'articles selon le style du journaliste.

```python
def answer_question(question: str, context: list, journalist: Journalist) -> str
```
Repond a une question utilisateur en analysant le contexte disponible.

```python
def extract_keywords(text: str) -> list
```
Extrait les mots-cles d'un texte.

---

## Audio Service (`services/audio_service.py`)

Service d'integration avec Eleven Labs pour la synthese vocale.

### Fonctionnalites

- Conversion texte vers audio
- Gestion des voix personnalisees

### Methodes principales

```python
def text_to_speech(text: str, voice_id: str = None) -> bytes
```
Convertit un texte en fichier audio.

```python
def get_available_voices() -> list
```
Retourne la liste des voix disponibles.

---

## Scheduler Service (`services/scheduler_service.py`)

Service de planification des taches automatisees.

### Fonctionnalites

- Collecte periodique des articles
- Generation des resumes quotidiens
- Envoi des notifications

### Taches planifiees

| Tache | Frequence | Description |
|-------|-----------|-------------|
| collect_articles | Toutes les 24h | Collecte les nouveaux articles |
| generate_summaries | Quotidien (heure configurable) | Genere les resumes |
| send_summaries | Apres generation | Envoie aux abonnes |
| cleanup_old_data | Hebdomadaire | Nettoie les donnees anciennes |

---

## Scraper Service (`services/scraper_service.py`)

Service de collecte d'informations depuis les sources.

### Fonctionnalites

- Scraping de pages web
- Parsing de flux RSS
- Collecte depuis Twitter/X

### Methodes principales

```python
def scrape_website(url: str, config: dict) -> list
```
Collecte les articles depuis un site web.

```python
def parse_rss(url: str) -> list
```
Parse un flux RSS et retourne les articles.

```python
def fetch_twitter(account: str, config: dict) -> list
```
Collecte les tweets d'un compte.

```python
def process_source(source: Source) -> list
```
Traite une source selon son type.

---

## Telegram Service (`services/telegram_service.py`)

Service de gestion des bots Telegram.

### Fonctionnalites

- Reception et traitement des messages
- Envoi de resumes aux abonnes
- Gestion des conversations

### Methodes principales

```python
def send_message(chat_id: str, text: str, token: str) -> bool
```
Envoie un message a un utilisateur.

```python
def send_audio(chat_id: str, audio: bytes, token: str) -> bool
```
Envoie un fichier audio.

```python
def handle_message(update: dict, journalist: Journalist) -> str
```
Traite un message entrant et genere une reponse.

```python
def register_subscriber(telegram_user: dict, journalist: Journalist) -> Subscriber
```
Enregistre un nouvel abonne.

---

## Delivery Service (`services/delivery_service.py`)

Service de distribution des resumes via plusieurs canaux.

### Fonctionnalites

- Envoi via Telegram (bot public)
- Envoi par Email (SMTP)
- Envoi WhatsApp (API Twilio)
- Gestion d'erreurs robuste
- Logging detaille

### Methodes principales

```python
def send_via_telegram(channel: DeliveryChannel, summary_text: str, audio_url: str = None) -> bool
```
Envoie le resume via bot Telegram public.

```python
def send_via_email(channel: DeliveryChannel, summary_text: str, audio_url: str = None, journalist_name: str = "Journalist") -> bool
```
Envoie le resume par email (HTML + texte brut).

```python
def send_via_whatsapp(channel: DeliveryChannel, summary_text: str, audio_url: str = None, journalist_name: str = "Journalist") -> bool
```
Envoie le resume via WhatsApp (requiert Twilio).

```python
def send_summary_to_channels(journalist: Journalist, summary_text: str, audio_url: str = None) -> dict
```
Envoie le resume a tous les canaux actifs du journaliste.

### Gestion d'erreurs

- Validation des credentials
- Timeout SMTP configurable (10s)
- Gestion d'authentification (SMTP)
- Truncature des messages WhatsApp (1500 chars max)
- Logging detaille avec emojis pour clarté

### Exemple d'utilisation

```python
from services.delivery_service import DeliveryService
journalist = Journalist.query.get(1)
results = DeliveryService.send_summary_to_channels(
    journalist, 
    summary_text="Resume du jour...", 
    audio_url="https://..."
)
# results = {'telegram': True, 'email': True, 'whatsapp': False}
```

---

## Integration des services

### Flux de collecte quotidien

```
1. Scheduler declenche la collecte
   ↓
2. Scraper Service collecte depuis chaque source
   ↓
3. Articles stockes en base
   ↓
4. AI Service genere le resume
   ↓
5. Audio Service cree la version audio
   ↓
6. Telegram Service envoie aux abonnes
```

### Flux de conversation

```
1. Message recu via webhook Telegram
   ↓
2. Telegram Service identifie l'abonne
   ↓
3. Verification des droits d'acces
   ↓
4. AI Service analyse la demande
   ↓
5. Recherche dans les articles si necessaire
   ↓
6. AI Service genere la reponse
   ↓
7. Telegram Service envoie la reponse
```
