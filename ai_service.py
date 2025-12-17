import os
import logging
from google import genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_client = None

def get_client():
    global _client
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    if _client is None:
        _client = genai.Client(api_key=api_key)
    return _client

def is_ai_available():
    return os.environ.get("GEMINI_API_KEY") is not None

def generate_news_summary(articles: list, personality: str, writing_style: str, tone: str, language: str = "fr") -> str:
    if not articles:
        return "Aucune nouvelle actualité à résumer aujourd'hui."
    
    client = get_client()
    if client is None:
        logger.warning("GEMINI_API_KEY not configured - returning basic summary")
        titles = [a.get('title', 'Article') for a in articles[:10]]
        return "Résumé des actualités:\n\n" + "\n".join([f"- {t}" for t in titles])
    
    articles_text = "\n\n".join([
        f"Source: {a.get('source', 'Unknown')}\nTitre: {a.get('title', 'Sans titre')}\nContenu: {a.get('content', '')[:1000]}"
        for a in articles
    ])
    
    prompt = f"""Tu es un journaliste IA avec les caractéristiques suivantes:
- Personnalité: {personality}
- Style d'écriture: {writing_style}
- Ton: {tone}

Génère un résumé d'actualités concis et engageant en {language} à partir des articles suivants. 
Le résumé doit:
- Être structuré avec les points clés
- Mentionner les sources
- Être adapté pour une lecture Telegram (formatage Markdown)
- Ne pas dépasser 2000 caractères

Articles à résumer:
{articles_text}

Résumé:"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text or "Erreur lors de la génération du résumé."
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return f"Erreur lors de la génération du résumé: {str(e)}"

def answer_user_question(question: str, articles: list, personality: str, writing_style: str, tone: str, language: str = "fr") -> str:
    client = get_client()
    if client is None:
        return "Le service IA n'est pas configuré. Contactez l'administrateur."
    
    articles_context = "\n\n".join([
        f"[{a.get('source', 'Unknown')}] {a.get('title', '')}: {a.get('content', '')[:500]}"
        for a in articles[:10]
    ])
    
    prompt = f"""Tu es un journaliste IA avec les caractéristiques suivantes:
- Personnalité: {personality}
- Style d'écriture: {writing_style}
- Ton: {tone}

Réponds à la question de l'utilisateur en te basant sur ta base de données d'articles.
Mentionne toujours la source de l'information.
Réponds en {language}.

Base de données d'articles récents:
{articles_context}

Question de l'utilisateur: {question}

Réponse:"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text or "Je n'ai pas pu trouver d'information pertinente."
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        return f"Erreur: {str(e)}"

def extract_keywords(text: str) -> list:
    client = get_client()
    if client is None:
        return []
    
    prompt = f"""Extrais les mots-clés principaux du texte suivant.
Retourne uniquement une liste de mots-clés séparés par des virgules.

Texte: {text[:2000]}

Mots-clés:"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        keywords = response.text.strip() if response.text else ""
        return [kw.strip() for kw in keywords.split(",") if kw.strip()]
    except Exception as e:
        logger.error(f"Error extracting keywords: {e}")
        return []
