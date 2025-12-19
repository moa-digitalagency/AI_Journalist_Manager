import os
import logging
from google import genai

logger = logging.getLogger(__name__)

def clean_html(text: str) -> str:
    """Remove HTML tags and clean text for Telegram."""
    import re
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters that might be HTML-encoded
    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    text = text.replace('<b>', '').replace('</b>', '')
    text = text.replace('<i>', '').replace('</i>', '')
    text = text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
    return text.strip()

class AIService:
    _client = None
    
    @classmethod
    def get_client(cls):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return None
        if cls._client is None:
            cls._client = genai.Client(api_key=api_key)
        return cls._client
    
    @classmethod
    def is_available(cls, provider: str = "gemini"):
        """Check if API is available for the given provider."""
        if provider == "perplexity":
            return os.environ.get("PERPLEXITY_API_KEY") is not None
        return os.environ.get("GEMINI_API_KEY") is not None
    
    @classmethod
    def get_provider_service(cls, provider: str = "gemini"):
        """Get the appropriate service based on provider."""
        if provider == "perplexity":
            from services.perplexity_service import PerplexityService
            return PerplexityService
        elif provider == "openai":
            from services.openai_service import OpenAIService
            return OpenAIService
        elif provider == "openrouter":
            from services.openrouter_service import OpenRouterService
            return OpenRouterService
        return cls
    
    @classmethod
    def generate_summary(cls, articles: list, personality: str, writing_style: str, tone: str, language: str = "fr", provider: str = "gemini", model: str = "auto") -> str:
        if not articles:
            return "Aucune nouvelle actualité à résumer aujourd'hui."
        
        # Use the appropriate provider service
        service = cls.get_provider_service(provider)
        
        # If not Gemini, delegate to the provider service
        if provider != "gemini":
            if provider == "openai":
                return service.generate_summary(articles, personality, writing_style, tone, language, model or "gpt-4o-mini")
            elif provider == "openrouter":
                return service.generate_summary(articles, personality, writing_style, tone, language, model or "openrouter/auto")
            else:
                return service.generate_summary(articles, personality, writing_style, tone, language)
        
        # Gemini implementation
        client = cls.get_client()
        if client is None:
            logger.warning("GEMINI_API_KEY not configured")
            titles = [a.get('title', 'Article') for a in articles[:10]]
            return "Résumé des actualités:\n\n" + "\n".join([f"• {t}" for t in titles])
        
        articles_text = "\n\n".join([
            f"Source: {a.get('source', 'Unknown')}\nTitre: {a.get('title', 'Sans titre')}\nContenu: {a.get('content', '')[:1000]}"
            for a in articles
        ])
        
        prompt = f"""Tu es un journaliste IA avec les caractéristiques suivantes:
- Personnalité: {personality}
- Style d'écriture: {writing_style}
- Ton: {tone}

Génère un résumé d'actualités détaillé et engageant en {language} à partir des articles suivants. 
Le résumé doit:
- Être structuré avec les points clés (5-15 points)
- Mentionner la source directement après chaque point clé entre crochets [Nom Source], sans aucun chiffre
- Utiliser UNIQUEMENT du texte brut, JAMAIS de balises HTML ou Markdown
- Ne pas dépasser 4500 caractères
- NE PAS inclure d'introduction comme "Voici un résumé..."
- NE PAS inclure de notes pratiques ou sections d'explication
- NE PAS utiliser de balises HTML comme <b>, </b>, <i>, </i>, etc
- Aller directement au contenu du résumé

Articles à résumer:
{articles_text}

Résumé:"""

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            summary_text = response.text or "Erreur lors de la génération du résumé."
            return clean_html(summary_text)
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Erreur lors de la génération du résumé: {str(e)}"
    
    @classmethod
    def answer_question(cls, question: str, articles: list, personality: str, writing_style: str, tone: str, language: str = "fr", provider: str = "gemini", model: str = "auto") -> str:
        # Use the appropriate provider service
        service = cls.get_provider_service(provider)
        
        # If not Gemini, delegate to the provider service
        if provider != "gemini":
            if provider == "openai":
                return service.answer_question(question, articles, personality, writing_style, tone, language, model or "gpt-4o-mini")
            elif provider == "openrouter":
                return service.answer_question(question, articles, personality, writing_style, tone, language, model or "openrouter/auto")
            else:
                return service.answer_question(question, articles, personality, writing_style, tone, language)
        
        # Gemini implementation
        client = cls.get_client()
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
    
    @classmethod
    def extract_keywords(cls, text: str, provider: str = "gemini", model: str = "auto") -> list:
        # Use the appropriate provider service
        service = cls.get_provider_service(provider)
        
        # If not Gemini, delegate to the provider service
        if provider != "gemini":
            if provider == "openai":
                return service.extract_keywords(text, model or "gpt-4o-mini")
            elif provider == "openrouter":
                return service.extract_keywords(text, model or "openrouter/auto")
            else:
                return service.extract_keywords(text)
        
        # Gemini implementation
        client = cls.get_client()
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
