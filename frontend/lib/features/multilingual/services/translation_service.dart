import 'dart:async';
import 'dart:convert';
import 'dart:ui';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:dio/dio.dart';

/// Comprehensive multilingual and multimodal translation service
class TranslationService {
  static const String _currentLocaleKey = 'current_locale';
  static const String _translationCacheKey = 'translation_cache';
  static const String _offlineTranslationsKey = 'offline_translations';
  
  late SharedPreferences _prefs;
  late Dio _dio;
  
  final Map<String, Map<String, String>> _translationCache = {};
  final Map<String, Map<String, dynamic>> _multimodalCache = {};
  
  Locale _currentLocale = const Locale('en', 'US');
  
  // Supported languages with their configurations
  static const Map<String, LanguageConfig> supportedLanguages = {
    'en': LanguageConfig(
      code: 'en',
      name: 'English',
      nativeName: 'English',
      rtl: false,
      hasVoice: true,
      hasHandwriting: true,
      hasOCR: true,
      culturalAdaptations: true,
    ),
    'es': LanguageConfig(
      code: 'es',
      name: 'Spanish',
      nativeName: 'Español',
      rtl: false,
      hasVoice: true,
      hasHandwriting: true,
      hasOCR: true,
      culturalAdaptations: true,
    ),
    'fr': LanguageConfig(
      code: 'fr',
      name: 'French',
      nativeName: 'Français',
      rtl: false,
      hasVoice: true,
      hasHandwriting: true,
      hasOCR: true,
      culturalAdaptations: true,
    ),
    'de': LanguageConfig(
      code: 'de',
      name: 'German',
      nativeName: 'Deutsch',
      rtl: false,
      hasVoice: true,
      hasHandwriting: true,
      hasOCR: true,
      culturalAdaptations: true,
    ),
    'zh': LanguageConfig(
      code: 'zh',
      name: 'Chinese',
      nativeName: '中文',
      rtl: false,
      hasVoice: true,
      hasHandwriting: true,
      hasOCR: true,
      culturalAdaptations: true,
    ),
    'ja': LanguageConfig(
      code: 'ja',
      name: 'Japanese',
      nativeName: '日本語',
      rtl: false,
      hasVoice: true,
      hasHandwriting: true,
      hasOCR: true,
      culturalAdaptations: true,
    ),
    'ko': LanguageConfig(
      code: 'ko',
      name: 'Korean',
      nativeName: '한국어',
      rtl: false,
      hasVoice: true,
      hasHandwriting: true,
      hasOCR: true,
      culturalAdaptations: true,
    ),
    'ar': LanguageConfig(
      code: 'ar',
      name: 'Arabic',
      nativeName: 'العربية',
      rtl: true,
      hasVoice: true,
      hasHandwriting: true,
      hasOCR: true,
      culturalAdaptations: true,
    ),
    'hi': LanguageConfig(
      code: 'hi',
      name: 'Hindi',
      nativeName: 'हिन्दी',
      rtl: false,
      hasVoice: true,
      hasHandwriting: true,
      hasOCR: true,
      culturalAdaptations: true,
    ),
    'pt': LanguageConfig(
      code: 'pt',
      name: 'Portuguese',
      nativeName: 'Português',
      rtl: false,
      hasVoice: true,
      hasHandwriting: true,
      hasOCR: true,
      culturalAdaptations: true,
    ),
    'ru': LanguageConfig(
      code: 'ru',
      name: 'Russian',
      nativeName: 'Русский',
      rtl: false,
      hasVoice: true,
      hasHandwriting: true,
      hasOCR: true,
      culturalAdaptations: true,
    ),
    'sw': LanguageConfig(
      code: 'sw',
      name: 'Swahili',
      nativeName: 'Kiswahili',
      rtl: false,
      hasVoice: true,
      hasHandwriting: false,
      hasOCR: true,
      culturalAdaptations: true,
    ),
    'am': LanguageConfig(
      code: 'am',
      name: 'Amharic',
      nativeName: 'አማርኛ',
      rtl: false,
      hasVoice: true,
      hasHandwriting: false,
      hasOCR: true,
      culturalAdaptations: true,
    ),
    'yo': LanguageConfig(
      code: 'yo',
      name: 'Yoruba',
      nativeName: 'Yorùbá',
      rtl: false,
      hasVoice: true,
      hasHandwriting: false,
      hasOCR: false,
      culturalAdaptations: true,
    ),
    'ig': LanguageConfig(
      code: 'ig',
      name: 'Igbo',
      nativeName: 'Igbo',
      rtl: false,
      hasVoice: true,
      hasHandwriting: false,
      hasOCR: false,
      culturalAdaptations: true,
    ),
    'ha': LanguageConfig(
      code: 'ha',
      name: 'Hausa',
      nativeName: 'Hausa',
      rtl: false,
      hasVoice: true,
      hasHandwriting: false,
      hasOCR: false,
      culturalAdaptations: true,
    ),
  };
  
  // Singleton pattern
  static final TranslationService _instance = TranslationService._internal();
  factory TranslationService() => _instance;
  TranslationService._internal();
  
  /// Initialize the translation service
  Future<void> initialize() async {
    try {
      _prefs = await SharedPreferences.getInstance();
      _dio = Dio(BaseOptions(
        baseUrl: 'https://api.eduverse.com/v1/translation',
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 30),
      ));
      
      // Load saved locale
      await _loadSavedLocale();
      
      // Load cached translations
      await _loadCachedTranslations();
      
      // Load offline translations
      await _loadOfflineTranslations();
      
      debugPrint('TranslationService initialized successfully');
    } catch (e) {
      debugPrint('Failed to initialize TranslationService: $e');
      rethrow;
    }
  }
  
  /// Get current locale
  Locale get currentLocale => _currentLocale;
  
  /// Set current locale
  Future<void> setLocale(Locale locale) async {
    if (_currentLocale == locale) return;
    
    _currentLocale = locale;
    await _prefs.setString(_currentLocaleKey, '${locale.languageCode}_${locale.countryCode}');
    
    // Load translations for new locale if not cached
    if (!_translationCache.containsKey(locale.languageCode)) {
      await _loadTranslationsForLocale(locale.languageCode);
    }
    
    debugPrint('Locale changed to: ${locale.languageCode}');
  }
  
  /// Translate text
  Future<String> translate(
    String key, {
    String? fallback,
    Map<String, dynamic>? parameters,
    String? targetLanguage,
  }) async {
    final language = targetLanguage ?? _currentLocale.languageCode;
    
    try {
      // Check cache first
      if (_translationCache.containsKey(language) &&
          _translationCache[language]!.containsKey(key)) {
        String translation = _translationCache[language]![key]!;
        
        // Apply parameters if provided
        if (parameters != null) {
          translation = _applyParameters(translation, parameters);
        }
        
        return translation;
      }
      
      // Try to fetch from server
      final translation = await _fetchTranslationFromServer(key, language);
      if (translation != null) {
        // Cache the translation
        _cacheTranslation(language, key, translation);
        
        // Apply parameters if provided
        if (parameters != null) {
          return _applyParameters(translation, parameters);
        }
        
        return translation;
      }
      
      // Return fallback or key
      return fallback ?? key;
      
    } catch (e) {
      debugPrint('Translation failed for key: $key, error: $e');
      return fallback ?? key;
    }
  }
  
  /// Translate multiple keys at once
  Future<Map<String, String>> translateBatch(
    List<String> keys, {
    String? targetLanguage,
  }) async {
    final language = targetLanguage ?? _currentLocale.languageCode;
    final results = <String, String>{};
    final missingKeys = <String>[];
    
    // Check cache for existing translations
    for (final key in keys) {
      if (_translationCache.containsKey(language) &&
          _translationCache[language]!.containsKey(key)) {
        results[key] = _translationCache[language]![key]!;
      } else {
        missingKeys.add(key);
      }
    }
    
    // Fetch missing translations from server
    if (missingKeys.isNotEmpty) {
      try {
        final response = await _dio.post('/batch', data: {
          'keys': missingKeys,
          'target_language': language,
        });
        
        if (response.statusCode == 200) {
          final translations = Map<String, String>.from(response.data['translations']);
          
          // Cache and add to results
          for (final entry in translations.entries) {
            _cacheTranslation(language, entry.key, entry.value);
            results[entry.key] = entry.value;
          }
        }
      } catch (e) {
        debugPrint('Batch translation failed: $e');
        
        // Add missing keys as fallbacks
        for (final key in missingKeys) {
          results[key] = key;
        }
      }
    }
    
    return results;
  }
  
  /// Translate with voice output
  Future<TranslationResult> translateWithVoice(
    String text, {
    String? targetLanguage,
    String? voiceId,
  }) async {
    final language = targetLanguage ?? _currentLocale.languageCode;
    
    try {
      final response = await _dio.post('/voice', data: {
        'text': text,
        'target_language': language,
        'voice_id': voiceId,
      });
      
      if (response.statusCode == 200) {
        return TranslationResult(
          originalText: text,
          translatedText: response.data['translated_text'],
          targetLanguage: language,
          audioUrl: response.data['audio_url'],
          audioData: response.data['audio_data'],
        );
      }
    } catch (e) {
      debugPrint('Voice translation failed: $e');
    }
    
    // Fallback to text-only translation
    final translatedText = await translate(text, targetLanguage: language);
    return TranslationResult(
      originalText: text,
      translatedText: translatedText,
      targetLanguage: language,
    );
  }
  
  /// Translate image text using OCR
  Future<ImageTranslationResult> translateImage(
    Uint8List imageData, {
    String? targetLanguage,
  }) async {
    final language = targetLanguage ?? _currentLocale.languageCode;
    
    try {
      final formData = FormData.fromMap({
        'image': MultipartFile.fromBytes(imageData, filename: 'image.jpg'),
        'target_language': language,
      });
      
      final response = await _dio.post('/image', data: formData);
      
      if (response.statusCode == 200) {
        return ImageTranslationResult(
          detectedText: response.data['detected_text'],
          translatedText: response.data['translated_text'],
          sourceLanguage: response.data['source_language'],
          targetLanguage: language,
          boundingBoxes: List<Map<String, dynamic>>.from(
            response.data['bounding_boxes'] ?? [],
          ),
          confidence: response.data['confidence']?.toDouble() ?? 0.0,
        );
      }
    } catch (e) {
      debugPrint('Image translation failed: $e');
    }
    
    return ImageTranslationResult(
      detectedText: '',
      translatedText: '',
      sourceLanguage: 'unknown',
      targetLanguage: language,
      boundingBoxes: [],
      confidence: 0.0,
    );
  }
  
  /// Translate handwritten text
  Future<HandwritingTranslationResult> translateHandwriting(
    List<List<Offset>> strokes, {
    String? targetLanguage,
  }) async {
    final language = targetLanguage ?? _currentLocale.languageCode;
    
    try {
      final strokeData = strokes.map((stroke) =>
        stroke.map((point) => {'x': point.dx, 'y': point.dy}).toList()
      ).toList();
      
      final response = await _dio.post('/handwriting', data: {
        'strokes': strokeData,
        'target_language': language,
      });
      
      if (response.statusCode == 200) {
        return HandwritingTranslationResult(
          recognizedText: response.data['recognized_text'],
          translatedText: response.data['translated_text'],
          sourceLanguage: response.data['source_language'],
          targetLanguage: language,
          confidence: response.data['confidence']?.toDouble() ?? 0.0,
          alternatives: List<String>.from(response.data['alternatives'] ?? []),
        );
      }
    } catch (e) {
      debugPrint('Handwriting translation failed: $e');
    }
    
    return HandwritingTranslationResult(
      recognizedText: '',
      translatedText: '',
      sourceLanguage: 'unknown',
      targetLanguage: language,
      confidence: 0.0,
      alternatives: [],
    );
  }
  
  /// Get cultural adaptations for content
  Future<CulturalAdaptation> getCulturalAdaptation(
    String content, {
    String? targetLanguage,
    String? contentType,
  }) async {
    final language = targetLanguage ?? _currentLocale.languageCode;
    
    try {
      final response = await _dio.post('/cultural-adaptation', data: {
        'content': content,
        'target_language': language,
        'content_type': contentType ?? 'general',
      });
      
      if (response.statusCode == 200) {
        return CulturalAdaptation(
          originalContent: content,
          adaptedContent: response.data['adapted_content'],
          targetLanguage: language,
          culturalNotes: List<String>.from(response.data['cultural_notes'] ?? []),
          colorAdaptations: Map<String, String>.from(
            response.data['color_adaptations'] ?? {},
          ),
          imageAdaptations: List<String>.from(
            response.data['image_adaptations'] ?? [],
          ),
          dateTimeFormat: response.data['datetime_format'],
          numberFormat: response.data['number_format'],
          currencyFormat: response.data['currency_format'],
        );
      }
    } catch (e) {
      debugPrint('Cultural adaptation failed: $e');
    }
    
    return CulturalAdaptation(
      originalContent: content,
      adaptedContent: content,
      targetLanguage: language,
      culturalNotes: [],
      colorAdaptations: {},
      imageAdaptations: [],
    );
  }
  
  /// Get language detection from text
  Future<LanguageDetectionResult> detectLanguage(String text) async {
    try {
      final response = await _dio.post('/detect', data: {'text': text});
      
      if (response.statusCode == 200) {
        return LanguageDetectionResult(
          detectedLanguage: response.data['language'],
          confidence: response.data['confidence']?.toDouble() ?? 0.0,
          alternatives: Map<String, double>.from(
            response.data['alternatives'] ?? {},
          ),
        );
      }
    } catch (e) {
      debugPrint('Language detection failed: $e');
    }
    
    return LanguageDetectionResult(
      detectedLanguage: 'unknown',
      confidence: 0.0,
      alternatives: {},
    );
  }
  
  /// Check if language is supported
  bool isLanguageSupported(String languageCode) {
    return supportedLanguages.containsKey(languageCode);
  }
  
  /// Get language configuration
  LanguageConfig? getLanguageConfig(String languageCode) {
    return supportedLanguages[languageCode];
  }
  
  /// Get all supported languages
  List<LanguageConfig> getSupportedLanguages() {
    return supportedLanguages.values.toList();
  }
  
  /// Check if current language is RTL
  bool get isRTL {
    final config = supportedLanguages[_currentLocale.languageCode];
    return config?.rtl ?? false;
  }
  
  /// Download offline translations for a language
  Future<void> downloadOfflineTranslations(String languageCode) async {
    try {
      final response = await _dio.get('/offline/$languageCode');
      
      if (response.statusCode == 200) {
        final translations = Map<String, String>.from(response.data['translations']);
        
        // Save to local storage
        await _prefs.setString(
          '${_offlineTranslationsKey}_$languageCode',
          jsonEncode(translations),
        );
        
        // Update cache
        _translationCache[languageCode] = translations;
        
        debugPrint('Downloaded offline translations for: $languageCode');
      }
    } catch (e) {
      debugPrint('Failed to download offline translations: $e');
      rethrow;
    }
  }
  
  /// Check if offline translations are available
  bool hasOfflineTranslations(String languageCode) {
    return _prefs.containsKey('${_offlineTranslationsKey}_$languageCode');
  }
  
  /// Clear translation cache
  Future<void> clearCache() async {
    _translationCache.clear();
    _multimodalCache.clear();
    
    // Clear from persistent storage
    final keys = _prefs.getKeys().where((key) => 
      key.startsWith(_translationCacheKey) || 
      key.startsWith(_offlineTranslationsKey)
    ).toList();
    
    for (final key in keys) {
      await _prefs.remove(key);
    }
    
    debugPrint('Translation cache cleared');
  }
  
  // Private methods
  
  Future<void> _loadSavedLocale() async {
    final savedLocale = _prefs.getString(_currentLocaleKey);
    if (savedLocale != null) {
      final parts = savedLocale.split('_');
      if (parts.length == 2) {
        _currentLocale = Locale(parts[0], parts[1]);
      } else {
        _currentLocale = Locale(parts[0]);
      }
    } else {
      // Use system locale as default
      _currentLocale = PlatformDispatcher.instance.locale;
    }
  }
  
  Future<void> _loadCachedTranslations()  async {
    for (final languageCode in supportedLanguages.keys) {
      final cacheKey = '${_translationCacheKey}_$languageCode';
      final cachedData = _prefs.getString(cacheKey);
      
      if (cachedData != null) {
        try {
          final translations = Map<String, String>.from(jsonDecode(cachedData));
          _translationCache[languageCode] = translations;
        } catch (e) {
          debugPrint('Failed to load cached translations for $languageCode: $e');
        }
      }
    }
  }
  
  Future<void> _loadOfflineTranslations() async {
    for (final languageCode in supportedLanguages.keys) {
      final offlineKey = '${_offlineTranslationsKey}_$languageCode';
      final offlineData = _prefs.getString(offlineKey);
      
      if (offlineData != null) {
        try {
          final translations = Map<String, String>.from(jsonDecode(offlineData));
          _translationCache[languageCode] = {
            ...(_translationCache[languageCode] ?? {}),
            ...translations,
          };
        } catch (e) {
          debugPrint('Failed to load offline translations for $languageCode: $e');
        }
      }
    }
  }
  
  Future<void> _loadTranslationsForLocale(String languageCode) async {
    try {
      final response = await _dio.get('/language/$languageCode');
      
      if (response.statusCode == 200) {
        final translations = Map<String, String>.from(response.data['translations']);
        _translationCache[languageCode] = translations;
        
        // Cache to persistent storage
        await _prefs.setString(
          '${_translationCacheKey}_$languageCode',
          jsonEncode(translations),
        );
      }
    } catch (e) {
      debugPrint('Failed to load translations for $languageCode: $e');
    }
  }
  
  Future<String?> _fetchTranslationFromServer(String key, String language) async {
    try {
      final response = await _dio.post('/translate', data: {
        'key': key,
        'target_language': language,
      });
      
      if (response.statusCode == 200) {
        return response.data['translation'];
      }
    } catch (e) {
      debugPrint('Failed to fetch translation from server: $e');
    }
    
    return null;
  }
  
  void _cacheTranslation(String language, String key, String translation) {
    if (!_translationCache.containsKey(language)) {
      _translationCache[language] = {};
    }
    
    _translationCache[language]![key] = translation;
    
    // Save to persistent storage (async)
    _saveCacheToStorage(language);
  }
  
  Future<void> _saveCacheToStorage(String language) async {
    try {
      final cacheKey = '${_translationCacheKey}_$language';
      final translations = _translationCache[language] ?? {};
      await _prefs.setString(cacheKey, jsonEncode(translations));
    } catch (e) {
      debugPrint('Failed to save translation cache: $e');
    }
  }
  
  String _applyParameters(String template, Map<String, dynamic> parameters) {
    String result = template;
    
    for (final entry in parameters.entries) {
      final placeholder = '{${entry.key}}';
      result = result.replaceAll(placeholder, entry.value.toString());
    }
    
    return result;
  }
}

/// Language configuration
class LanguageConfig {
  final String code;
  final String name;
  final String nativeName;
  final bool rtl;
  final bool hasVoice;
  final bool hasHandwriting;
  final bool hasOCR;
  final bool culturalAdaptations;
  
  const LanguageConfig({
    required this.code,
    required this.name,
    required this.nativeName,
    required this.rtl,
    required this.hasVoice,
    required this.hasHandwriting,
    required this.hasOCR,
    required this.culturalAdaptations,
  });
}

/// Translation result with voice
class TranslationResult {
  final String originalText;
  final String translatedText;
  final String targetLanguage;
  final String? audioUrl;
  final String? audioData;
  
  const TranslationResult({
    required this.originalText,
    required this.translatedText,
    required this.targetLanguage,
    this.audioUrl,
    this.audioData,
  });
}

/// Image translation result
class ImageTranslationResult {
  final String detectedText;
  final String translatedText;
  final String sourceLanguage;
  final String targetLanguage;
  final List<Map<String, dynamic>> boundingBoxes;
  final double confidence;
  
  const ImageTranslationResult({
    required this.detectedText,
    required this.translatedText,
    required this.sourceLanguage,
    required this.targetLanguage,
    required this.boundingBoxes,
    required this.confidence,
  });
}

/// Handwriting translation result
class HandwritingTranslationResult {
  final String recognizedText;
  final String translatedText;
  final String sourceLanguage;
  final String targetLanguage;
  final double confidence;
  final List<String> alternatives;
  
  const HandwritingTranslationResult({
    required this.recognizedText,
    required this.translatedText,
    required this.sourceLanguage,
    required this.targetLanguage,
    required this.confidence,
    required this.alternatives,
  });
}

/// Cultural adaptation result
class CulturalAdaptation {
  final String originalContent;
  final String adaptedContent;
  final String targetLanguage;
  final List<String> culturalNotes;
  final Map<String, String> colorAdaptations;
  final List<String> imageAdaptations;
  final String? dateTimeFormat;
  final String? numberFormat;
  final String? currencyFormat;
  
  const CulturalAdaptation({
    required this.originalContent,
    required this.adaptedContent,
    required this.targetLanguage,
    required this.culturalNotes,
    required this.colorAdaptations,
    required this.imageAdaptations,
    this.dateTimeFormat,
    this.numberFormat,
    this.currencyFormat,
  });
}

/// Language detection result
class LanguageDetectionResult {
  final String detectedLanguage;
  final double confidence;
  final Map<String, double> alternatives;
  
  const LanguageDetectionResult({
    required this.detectedLanguage,
    required this.confidence,
    required this.alternatives,
  });
}