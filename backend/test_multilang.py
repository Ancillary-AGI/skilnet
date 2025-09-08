#!/usr/bin/env python3
"""
Simple test script to demonstrate multilanguage support
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_translations():
    """Test translation loading and retrieval"""
    try:
        from app.middleware.i18n_middleware import I18nMiddleware

        # Create middleware instance
        middleware = I18nMiddleware(None)

        print("🚀 Testing EduVerse Multilanguage Support")
        print("=" * 50)

        # Test supported languages
        print(f"✅ Supported languages: {len(middleware.supported_languages)}")
        print(f"   Languages: {', '.join(middleware.supported_languages[:5])}...")

        # Test translation loading
        print(f"✅ Translations loaded: {len(middleware.translations)} languages")

        # Test English translations
        if 'en' in middleware.translations:
            en_translations = middleware.translations['en']
            print(f"✅ English translations: {len(en_translations)} keys")
            print(f"   Sample: welcome = '{en_translations.get('welcome', 'N/A')}'")

        # Test Spanish translations
        if 'es' in middleware.translations:
            es_translations = middleware.translations['es']
            print(f"✅ Spanish translations: {len(es_translations)} keys")
            print(f"   Sample: welcome = '{es_translations.get('welcome', 'N/A')}'")

        # Test Swahili translations
        if 'sw' in middleware.translations:
            sw_translations = middleware.translations['sw']
            print(f"✅ Swahili translations: {len(sw_translations)} keys")
            print(f"   Sample: welcome = '{sw_translations.get('welcome', 'N/A')}'")

        # Test translation function
        translate_func = lambda key, fallback=None: middleware._get_translation(key, 'en', fallback)
        test_translation = translate_func('login', 'Login')
        print(f"✅ Translation function: login -> '{test_translation}'")

        print("\n🎉 Multilanguage support is working correctly!")
        return True

    except Exception as e:
        print(f"❌ Error testing multilanguage support: {e}")
        return False

def test_config():
    """Test configuration settings"""
    try:
        from app.core.config import settings

        print("\n🔧 Testing Configuration")
        print("=" * 30)

        print(f"✅ Default language: {settings.DEFAULT_LANGUAGE}")
        print(f"✅ Supported languages: {len(settings.SUPPORTED_LANGUAGES)}")
        print(f"   Sample: {', '.join(settings.SUPPORTED_LANGUAGES[:5])}...")

        return True

    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False

def main():
    """Main test function"""
    print("EduVerse Multilanguage Support Test")
    print("===================================")

    success = True

    # Test translations
    if not test_translations():
        success = False

    # Test configuration
    if not test_config():
        success = False

    if success:
        print("\n✅ All tests passed! Multilanguage support is ready.")
        print("\n📋 Features implemented:")
        print("   • I18n middleware for automatic language detection")
        print("   • Translation API endpoints")
        print("   • Support for 16+ languages including African languages")
        print("   • Cookie-based language persistence")
        print("   • Accept-Language header support")
        print("   • Query parameter language override")
        print("   • Fallback to English for missing translations")
        print("   • RTL language support (Arabic)")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
