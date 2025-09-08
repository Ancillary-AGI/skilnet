"""
Translation API endpoints for multilanguage support
"""

from fastapi import APIRouter, Request, HTTPException, Query
from typing import Dict, List, Optional, Any
import json
from pathlib import Path

router = APIRouter()

@router.get("/languages")
async def get_supported_languages(request: Request) -> Dict[str, Any]:
    """Get list of supported languages"""
    supported_languages = getattr(request.state, 'supported_languages', ['en'])

    languages_info = {
        "en": {"name": "English", "native_name": "English", "rtl": False},
        "es": {"name": "Spanish", "native_name": "Español", "rtl": False},
        "fr": {"name": "French", "native_name": "Français", "rtl": False},
        "de": {"name": "German", "native_name": "Deutsch", "rtl": False},
        "zh": {"name": "Chinese", "native_name": "中文", "rtl": False},
        "ja": {"name": "Japanese", "native_name": "日本語", "rtl": False},
        "ko": {"name": "Korean", "native_name": "한국어", "rtl": False},
        "ar": {"name": "Arabic", "native_name": "العربية", "rtl": True},
        "hi": {"name": "Hindi", "native_name": "हिन्दी", "rtl": False},
        "pt": {"name": "Portuguese", "native_name": "Português", "rtl": False},
        "ru": {"name": "Russian", "native_name": "Русский", "rtl": False},
        "sw": {"name": "Swahili", "native_name": "Kiswahili", "rtl": False},
        "am": {"name": "Amharic", "native_name": "አማርኛ", "rtl": False},
        "yo": {"name": "Yoruba", "native_name": "Yorùbá", "rtl": False},
        "ig": {"name": "Igbo", "native_name": "Igbo", "rtl": False},
        "ha": {"name": "Hausa", "native_name": "Hausa", "rtl": False},
    }

    result = []
    for lang_code in supported_languages:
        if lang_code in languages_info:
            result.append({
                "code": lang_code,
                **languages_info[lang_code]
            })

    return {
        "languages": result,
        "default_language": "en",
        "current_language": getattr(request.state, 'language', 'en')
    }

@router.get("/translations/{language}")
async def get_translations(
    language: str,
    request: Request,
    keys: Optional[List[str]] = Query(None)
) -> Dict[str, Any]:
    """Get translations for a specific language"""
    supported_languages = getattr(request.state, 'supported_languages', ['en'])

    if language not in supported_languages:
        raise HTTPException(status_code=400, detail=f"Language '{language}' is not supported")

    # Load translations from file
    translations_dir = Path(__file__).parent.parent.parent / "translations"
    translation_file = translations_dir / f"{language}.json"

    translations = {}

    if translation_file.exists():
        try:
            with open(translation_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load translations: {str(e)}")

    # Filter by keys if provided
    if keys:
        filtered_translations = {}
        for key in keys:
            if key in translations:
                filtered_translations[key] = translations[key]
            else:
                # Try fallback to English
                en_file = translations_dir / "en.json"
                if en_file.exists():
                    try:
                        with open(en_file, 'r', encoding='utf-8') as f:
                            en_translations = json.load(f)
                            if key in en_translations:
                                filtered_translations[key] = en_translations[key]
                            else:
                                filtered_translations[key] = key  # Fallback to key itself
                    except:
                        filtered_translations[key] = key
                else:
                    filtered_translations[key] = key
        translations = filtered_translations

    return {
        "language": language,
        "translations": translations,
        "count": len(translations)
    }

@router.get("/translate")
async def translate_text(
    request: Request,
    text: str = Query(..., description="Text to translate"),
    target_language: str = Query(..., description="Target language code"),
    source_language: Optional[str] = Query(None, description="Source language code (auto-detect if not provided)")
) -> Dict[str, Any]:
    """Translate text to target language"""
    supported_languages = getattr(request.state, 'supported_languages', ['en'])

    if target_language not in supported_languages:
        raise HTTPException(status_code=400, detail=f"Target language '{target_language}' is not supported")

    # For now, return the original text as translation
    # In a real implementation, you would integrate with a translation service
    # like Google Translate, DeepL, or use local translation models

    return {
        "original_text": text,
        "translated_text": text,  # Placeholder - would be actual translation
        "source_language": source_language or "auto",
        "target_language": target_language,
        "confidence": 1.0
    }

@router.post("/batch-translate")
async def batch_translate(
    request: Request,
    translations_request: Dict[str, Any]
) -> Dict[str, Any]:
    """Translate multiple texts at once"""
    texts = translations_request.get("texts", [])
    target_language = translations_request.get("target_language", "en")
    source_language = translations_request.get("source_language")

    supported_languages = getattr(request.state, 'supported_languages', ['en'])

    if target_language not in supported_languages:
        raise HTTPException(status_code=400, detail=f"Target language '{target_language}' is not supported")

    # For now, return original texts as translations
    # In a real implementation, you would use a translation service

    results = []
    for text in texts:
        results.append({
            "original_text": text,
            "translated_text": text,  # Placeholder
            "confidence": 1.0
        })

    return {
        "results": results,
        "target_language": target_language,
        "source_language": source_language or "auto",
        "count": len(results)
    }

@router.get("/detect-language")
async def detect_language(
    request: Request,
    text: str = Query(..., description="Text to detect language for")
) -> Dict[str, Any]:
    """Detect the language of given text"""
    # Simple language detection based on common words
    # In a real implementation, you would use a proper language detection library

    text_lower = text.lower()

    # Simple heuristics for demonstration
    if any(word in text_lower for word in ["el", "la", "los", "las", "es", "son"]):
        detected_lang = "es"
        confidence = 0.8
    elif any(word in text_lower for word in ["le", "la", "les", "et", "est"]):
        detected_lang = "fr"
        confidence = 0.8
    elif any(word in text_lower for word in ["der", "die", "das", "ist", "und"]):
        detected_lang = "de"
        confidence = 0.8
    elif any(word in text_lower for word in ["the", "and", "is", "are", "was"]):
        detected_lang = "en"
        confidence = 0.9
    else:
        detected_lang = "en"
        confidence = 0.5

    return {
        "detected_language": detected_lang,
        "confidence": confidence,
        "text_length": len(text)
    }

@router.get("/current-language")
async def get_current_language(request: Request) -> Dict[str, Any]:
    """Get current language from request context"""
    current_language = getattr(request.state, 'language', 'en')
    supported_languages = getattr(request.state, 'supported_languages', ['en'])

    return {
        "current_language": current_language,
        "supported_languages": supported_languages,
        "is_rtl": current_language in ["ar"]  # Add more RTL languages as needed
    }
