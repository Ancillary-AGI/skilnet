"""
Internationalization middleware for handling language preferences
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional, Dict, Any
import json
import os
from pathlib import Path
from app.core.config import settings

class I18nMiddleware(BaseHTTPMiddleware):
    """Middleware for handling internationalization and language preferences"""

    def __init__(self, app, default_language: Optional[str] = None):
        super().__init__(app)
        self.default_language = default_language or settings.DEFAULT_LANGUAGE
        self.supported_languages = settings.SUPPORTED_LANGUAGES
        self.translations = {}
        self._load_translations()

    def _load_translations(self):
        """Load translation files from the translations directory"""
        translations_dir = Path(__file__).parent.parent / "translations"

        if not translations_dir.exists():
            translations_dir.mkdir(parents=True, exist_ok=True)
            self._create_default_translations(translations_dir)

        for lang_file in translations_dir.glob("*.json"):
            lang_code = lang_file.stem
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
            except Exception as e:
                print(f"Failed to load translations for {lang_code}: {e}")

    def _create_default_translations(self, translations_dir: Path):
        """Create default translation files"""
        default_translations = {
            "en": {
                "welcome": "Welcome to EduVerse",
                "login": "Login",
                "register": "Register",
                "logout": "Logout",
                "dashboard": "Dashboard",
                "courses": "Courses",
                "profile": "Profile",
                "settings": "Settings",
                "help": "Help",
                "search": "Search",
                "notifications": "Notifications",
                "messages": "Messages",
                "achievements": "Achievements",
                "leaderboard": "Leaderboard",
                "error": "Error",
                "success": "Success",
                "loading": "Loading...",
                "save": "Save",
                "cancel": "Cancel",
                "delete": "Delete",
                "edit": "Edit",
                "view": "View",
                "back": "Back",
                "next": "Next",
                "previous": "Previous",
                "submit": "Submit",
                "reset": "Reset",
                "confirm": "Confirm",
                "yes": "Yes",
                "no": "No",
                "ok": "OK",
                "close": "Close",
                "menu": "Menu",
                "home": "Home",
                "about": "About",
                "contact": "Contact",
                "privacy": "Privacy Policy",
                "terms": "Terms of Service",
                "language": "Language",
                "theme": "Theme",
                "dark_mode": "Dark Mode",
                "light_mode": "Light Mode",
                "accessibility": "Accessibility",
                "feedback": "Feedback",
                "support": "Support",
                "faq": "FAQ",
                "tutorial": "Tutorial",
                "guide": "Guide",
                "documentation": "Documentation",
                "api": "API",
                "admin": "Admin",
                "moderator": "Moderator",
                "student": "Student",
                "instructor": "Instructor",
                "content_creator": "Content Creator",
                "ai_trainer": "AI Trainer"
            }
        }

        for lang_code, translations in default_translations.items():
            with open(translations_dir / f"{lang_code}.json", 'w', encoding='utf-8') as f:
                json.dump(translations, f, indent=2, ensure_ascii=False)

    def _get_language_from_request(self, request: Request) -> str:
        """Extract language preference from request"""
        # Check Accept-Language header
        accept_language = request.headers.get("Accept-Language", "")

        if accept_language:
            # Parse Accept-Language header (e.g., "en-US,en;q=0.9,es;q=0.8")
            languages = []
            for lang in accept_language.split(','):
                lang = lang.strip().split(';')[0]  # Remove quality values
                lang_code = lang.split('-')[0]  # Get primary language code
                if lang_code in self.supported_languages:
                    languages.append(lang_code)

            if languages:
                return languages[0]

        # Check for language in query parameters
        query_lang = request.query_params.get("lang")
        if query_lang and query_lang in self.supported_languages:
            return query_lang

        # Check for language in cookies
        cookie_lang = request.cookies.get("eduverse_language")
        if cookie_lang and cookie_lang in self.supported_languages:
            return cookie_lang

        return self.default_language

    def _get_translation(self, key: str, language: str, fallback: Optional[str] = None) -> str:
        """Get translation for a key in the specified language"""
        if language in self.translations and key in self.translations[language]:
            return self.translations[language][key]

        # Try fallback to English
        if language != "en" and "en" in self.translations and key in self.translations["en"]:
            return self.translations["en"][key]

        # Return fallback or key itself
        return fallback or key

    async def dispatch(self, request: Request, call_next):
        """Process the request and add language context"""
        # Get user's preferred language
        language = self._get_language_from_request(request)

        # Add language to request state
        request.state.language = language

        # Add translation function to request state
        def translate(key: str, fallback: Optional[str] = None) -> str:
            return self._get_translation(key, language, fallback)

        request.state.translate = translate
        request.state.supported_languages = self.supported_languages

        # Process the request
        response = await call_next(request)

        # Add language cookie if not present
        if "eduverse_language" not in request.cookies:
            response.set_cookie(
                key="eduverse_language",
                value=language,
                max_age=365*24*60*60,  # 1 year
                httponly=False,  # Allow JavaScript access
                samesite="lax"
            )

        return response
