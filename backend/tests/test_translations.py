"""
Tests for multilanguage support
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_supported_languages():
    """Test getting list of supported languages"""
    response = client.get("/api/v1/translations/languages")
    assert response.status_code == 200
    data = response.json()
    assert "languages" in data
    assert "default_language" in data
    assert "current_language" in data
    assert len(data["languages"]) > 0

def test_get_translations_english():
    """Test getting English translations"""
    response = client.get("/api/v1/translations/translations/en")
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "en"
    assert "translations" in data
    assert "welcome" in data["translations"]
    assert data["translations"]["welcome"] == "Welcome to EduVerse"

def test_get_translations_spanish():
    """Test getting Spanish translations"""
    response = client.get("/api/v1/translations/translations/es")
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "es"
    assert "translations" in data
    assert "welcome" in data["translations"]
    assert data["translations"]["welcome"] == "Bienvenido a EduVerse"

def test_get_translations_swahili():
    """Test getting Swahili translations"""
    response = client.get("/api/v1/translations/translations/sw")
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "sw"
    assert "translations" in data
    assert "welcome" in data["translations"]
    assert data["translations"]["welcome"] == "Karibu EduVerse"

def test_get_translations_unsupported_language():
    """Test getting translations for unsupported language"""
    response = client.get("/api/v1/translations/translations/xx")
    assert response.status_code == 400
    assert "not supported" in response.json()["detail"]

def test_translate_text():
    """Test text translation endpoint"""
    response = client.get("/api/v1/translations/translate?text=Hello&target_language=es")
    assert response.status_code == 200
    data = response.json()
    assert "original_text" in data
    assert "translated_text" in data
    assert "target_language" in data
    assert data["target_language"] == "es"

def test_translate_text_unsupported_language():
    """Test text translation with unsupported language"""
    response = client.get("/api/v1/translations/translate?text=Hello&target_language=xx")
    assert response.status_code == 400
    assert "not supported" in response.json()["detail"]

def test_detect_language():
    """Test language detection"""
    response = client.get("/api/v1/translations/detect-language?text=Hello world")
    assert response.status_code == 200
    data = response.json()
    assert "detected_language" in data
    assert "confidence" in data
    assert "text_length" in data

def test_get_current_language():
    """Test getting current language"""
    response = client.get("/api/v1/translations/current-language")
    assert response.status_code == 200
    data = response.json()
    assert "current_language" in data
    assert "supported_languages" in data
    assert "is_rtl" in data

def test_i18n_middleware_default_language():
    """Test that middleware sets default language"""
    response = client.get("/health")
    assert response.status_code == 200
    # The middleware should have set a language cookie
    assert "eduverse_language" in response.cookies

def test_i18n_middleware_accept_language_header():
    """Test that middleware respects Accept-Language header"""
    headers = {"Accept-Language": "es"}
    response = client.get("/api/v1/translations/current-language", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["current_language"] == "es"

def test_i18n_middleware_query_parameter():
    """Test that middleware respects lang query parameter"""
    response = client.get("/api/v1/translations/current-language?lang=sw")
    assert response.status_code == 200
    data = response.json()
    assert data["current_language"] == "sw"
