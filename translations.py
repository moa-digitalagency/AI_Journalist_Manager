"""
Multilingual translation system for AI Journalist Manager.
Supports French (fr) and English (en).
Loads translations from JSON files in the lang folder.
"""

import json
import os

TRANSLATIONS = {}

def load_translations():
    """Load translations from JSON files in the lang folder."""
    global TRANSLATIONS
    lang_dir = os.path.join(os.path.dirname(__file__), 'lang')
    
    for lang_file in os.listdir(lang_dir):
        if lang_file.endswith('.json'):
            lang_code = lang_file.replace('.json', '')
            file_path = os.path.join(lang_dir, lang_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                TRANSLATIONS[lang_code] = json.load(f)

load_translations()


def get_translation(key, lang='fr'):
    """Get a translation for a given key and language."""
    if not TRANSLATIONS:
        load_translations()
    
    if lang not in TRANSLATIONS:
        lang = 'fr'
    
    # Try to find the key, if not found return the key itself
    val = TRANSLATIONS.get(lang, {}).get(key)
    if val is None:
        # Fallback to English if French key is missing
        val = TRANSLATIONS.get('en', {}).get(key, key)
    return val


def get_all_translations(lang='fr'):
    """Get all translations for a given language."""
    if lang not in TRANSLATIONS:
        lang = 'fr'
    return TRANSLATIONS.get(lang, {})


class TranslationHelper:
    """Helper class for template translations."""
    
    def __init__(self, lang='fr'):
        self.lang = lang
        self.translations = TRANSLATIONS.get(lang, TRANSLATIONS.get('fr', {}))
    
    def __call__(self, key):
        return self.translations.get(key, key)
    
    def get(self, key, default=None):
        return self.translations.get(key, default if default else key)
