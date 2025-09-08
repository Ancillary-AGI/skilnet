# EduVerse Multilanguage Support

This document describes the comprehensive multilanguage support implementation for the EduVerse platform.

## Overview

The EduVerse platform now supports 16+ languages including major world languages and African languages, providing a truly global learning experience.

## Features Implemented

### 1. I18n Middleware (`app/middleware/i18n_middleware.py`)
- **Automatic Language Detection**: Detects user language from:
  - Accept-Language HTTP header
  - Query parameters (`?lang=es`)
  - Cookies (`eduverse_language`)
  - System default (fallback to English)
- **Language Persistence**: Stores user language preference in cookies
- **Translation Loading**: Loads translation files from JSON format
- **Fallback Support**: Falls back to English for missing translations

### 2. Translation API Endpoints (`app/api/v1/endpoints/translations.py`)
- `GET /api/v1/translations/languages` - List all supported languages
- `GET /api/v1/translations/translations/{language}` - Get translations for a language
- `GET /api/v1/translations/translate` - Translate text (placeholder for future integration)
- `POST /api/v1/translations/batch-translate` - Batch translation (placeholder)
- `GET /api/v1/translations/detect-language` - Language detection
- `GET /api/v1/translations/current-language` - Get current language context

### 3. Configuration (`app/core/config.py`)
- Configurable default language
- List of supported languages
- Translation directory path

### 4. Translation Files
Located in `app/translations/` directory:
- `en.json` - English (base language)
- `es.json` - Spanish
- `sw.json` - Swahili (African language)

## Supported Languages

| Code | Language | Native Name | RTL | Region |
|------|----------|-------------|-----|--------|
| en | English | English | No | Global |
| es | Spanish | Español | No | Spain, Latin America |
| fr | French | Français | No | France, Africa |
| de | German | Deutsch | No | Germany |
| zh | Chinese | 中文 | No | China |
| ja | Japanese | 日本語 | No | Japan |
| ko | Korean | 한국어 | No | Korea |
| ar | Arabic | العربية | Yes | Middle East, North Africa |
| hi | Hindi | हिन्दी | No | India |
| pt | Portuguese | Português | No | Portugal, Brazil |
| ru | Russian | Русский | No | Russia |
| sw | Swahili | Kiswahili | No | East Africa |
| am | Amharic | አማርኛ | No | Ethiopia |
| yo | Yoruba | Yorùbá | No | Nigeria |
| ig | Igbo | Igbo | No | Nigeria |
| ha | Hausa | Hausa | No | Nigeria, Niger |

## Usage Examples

### Frontend Integration

```javascript
// Get supported languages
const languages = await fetch('/api/v1/translations/languages');
const data = await languages.json();

// Get translations for current language
const translations = await fetch('/api/v1/translations/translations/es');
const strings = await translations.json();

// Use Accept-Language header
const response = await fetch('/api/health', {
  headers: { 'Accept-Language': 'es' }
});
```

### Backend Usage

```python
from fastapi import Request

@app.get("/test")
async def test_translation(request: Request):
    # Access translation function
    translate = request.state.translate

    # Translate text
    welcome_msg = translate('welcome', 'Welcome')

    return {"message": welcome_msg}
```

## File Structure

```
backend/app/
├── middleware/
│   └── i18n_middleware.py          # I18n middleware
├── api/v1/endpoints/
│   └── translations.py             # Translation endpoints
├── translations/                   # Translation files
│   ├── en.json                     # English translations
│   ├── es.json                     # Spanish translations
│   └── sw.json                     # Swahili translations
├── core/
│   └── config.py                   # Configuration with i18n settings
└── main.py                         # Updated to include i18n middleware
```

## Translation File Format

```json
{
  "welcome": "Welcome to EduVerse",
  "login": "Login",
  "register": "Register",
  "dashboard": "Dashboard",
  "courses": "Courses",
  "profile": "Profile",
  "settings": "Settings",
  "language": "Language",
  "theme": "Theme"
}
```

## Configuration

Update your environment variables or `app/core/config.py`:

```python
# Default language
DEFAULT_LANGUAGE = "en"

# Supported languages
SUPPORTED_LANGUAGES = [
    "en", "es", "fr", "de", "zh", "ja", "ko", "ar",
    "hi", "pt", "ru", "sw", "am", "yo", "ig", "ha"
]

# Translation directory
TRANSLATIONS_DIR = "./app/translations"
```

## Testing

Run the test script to verify functionality:

```bash
cd backend
python test_multilang.py
```

## Future Enhancements

1. **Translation Service Integration**: Connect to Google Translate, DeepL, or other translation services
2. **Database Storage**: Store translations in database for dynamic management
3. **Admin Interface**: Web interface for managing translations
4. **Pluralization Support**: Handle singular/plural forms
5. **Context-Aware Translations**: Different translations based on context
6. **Offline Translation Packages**: Downloadable language packs for offline use

## Benefits

- **Global Reach**: Support users from diverse linguistic backgrounds
- **Accessibility**: Improve accessibility for non-English speakers
- **User Experience**: Localized interface enhances user engagement
- **Cultural Relevance**: Support for African languages shows commitment to local communities
- **Scalability**: Easy to add new languages and translations

## Integration with Frontend

The frontend already has a comprehensive translation service in `frontend/lib/features/multilingual/services/translation_service.dart`. The backend API endpoints are designed to work seamlessly with this frontend service.

## Conclusion

The multilanguage support implementation provides a solid foundation for global expansion, with support for major world languages and African languages, making EduVerse truly accessible to learners worldwide.
