import os
import logging
import requests

logger = logging.getLogger(__name__)

class OpenRouterService:
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    @classmethod
    def get_api_key(cls):
        return os.environ.get("OPENROUTER_API_KEY")
    
    @classmethod
    def is_available(cls):
        return cls.get_api_key() is not None
    
    @classmethod
    def _call_api(cls, prompt: str, model: str = "openrouter/auto") -> str:
        """Make a call to OpenRouter API."""
        api_key = cls.get_api_key()
        if not api_key:
            return None
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://replit.com",
            "X-Title": "AI Journalist Manager"
        }
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(cls.API_URL, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return None
    
    @classmethod
    def generate_summary(cls, articles: list, personality: str, writing_style: str, tone: str, language: str = "fr", model: str = "openrouter/auto") -> str:
        if not articles:
            return "Aucune nouvelle actualité à résumer aujourd'hui."
        
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
        
        result = cls._call_api(prompt, model)
        if result:
            return result
        else:
            logger.warning("OPENROUTER_API_KEY not configured or API error")
            titles = [a.get('title', 'Article') for a in articles[:10]]
            return "Résumé des actualités:\n\n" + "\n".join([f"• {t}" for t in titles])
    
    @classmethod
    def answer_question(cls, question: str, articles: list, personality: str, writing_style: str, tone: str, language: str = "fr", model: str = "openrouter/auto") -> str:
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
        
        result = cls._call_api(prompt, model)
        return result or "Je n'ai pas pu trouver d'information pertinente."
    
    @classmethod
    def extract_keywords(cls, text: str, model: str = "openrouter/auto") -> list:
        prompt = f"""Extrais les mots-clés principaux du texte suivant.
Retourne uniquement une liste de mots-clés séparés par des virgules.

Texte: {text[:2000]}

Mots-clés:"""
        
        result = cls._call_api(prompt, model)
        if result:
            return [kw.strip() for kw in result.split(",") if kw.strip()]
        return []
