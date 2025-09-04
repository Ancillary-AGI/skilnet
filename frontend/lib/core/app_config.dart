import 'package:flutter/material.dart';

class AppConfig {
  static const String appName = 'EduVerse';
  static const String appVersion = '1.0.0';
  static const String appDescription = 'Advanced E-Learning Platform with VR/AR and AI';
  
  // API Configuration
  static const String baseUrl = 'http://localhost:8000';
  static const String apiVersion = 'v1';
  static const String apiBaseUrl = '$baseUrl/api/$apiVersion';
  
  // WebSocket Configuration
  static const String wsBaseUrl = 'ws://localhost:8000/ws';
  
  // Supported platforms and features
  static const bool isVRSupported = true;
  static const bool isARSupported = true;
  static const bool isAITutoringEnabled = true;
  static const bool isLiveClassesEnabled = true;
  
  // Media Configuration
  static const int maxVideoQuality = 1080;
  static const int defaultVideoQuality = 720;
  static const int maxFileUploadSize = 100 * 1024 * 1024; // 100MB
  
  // VR/AR Configuration
  static const int vrFrameRate = 90;
  static const int arFrameRate = 60;
  static const double vrComfortLevel = 0.8;
  
  // Learning Configuration
  static const int defaultLessonDuration = 15; // minutes
  static const int maxDailyLearningTime = 480; // 8 hours
  static const int streakResetHours = 24;
  
  // Gamification
  static const int baseXPPerLesson = 100;
  static const int bonusXPForStreak = 50;
  static const int levelUpXPMultiplier = 100;
  
  // Supported locales
  static const List<Locale> supportedLocales = [
    Locale('en', 'US'),
    Locale('es', 'ES'),
    Locale('fr', 'FR'),
    Locale('de', 'DE'),
    Locale('ja', 'JP'),
    Locale('ko', 'KR'),
    Locale('zh', 'CN'),
    Locale('hi', 'IN'),
    Locale('ar', 'SA'),
    Locale('pt', 'BR'),
  ];
  
  // Device breakpoints for responsive design
  static const double mobileBreakpoint = 600;
  static const double tabletBreakpoint = 900;
  static const double desktopBreakpoint = 1200;
  static const double largeDesktopBreakpoint = 1600;
  
  // Foldable device configurations
  static const double foldableHingeWidth = 20;
  static const double foldableMinScreenWidth = 300;
  
  // Watch configurations
  static const double watchScreenSize = 200;
  static const int watchMaxNotifications = 5;
  
  // XR Device configurations
  static const Map<String, Map<String, dynamic>> xrDeviceConfigs = {
    'meta_quest': {
      'resolution': [2880, 1700],
      'refresh_rate': 90,
      'fov': 110,
      'tracking': '6dof',
    },
    'apple_vision_pro': {
      'resolution': [3660, 3200],
      'refresh_rate': 96,
      'fov': 120,
      'tracking': '6dof',
      'passthrough': true,
    },
    'hololens': {
      'resolution': [2048, 1080],
      'refresh_rate': 60,
      'fov': 52,
      'tracking': '6dof',
      'passthrough': true,
    },
  };
  
  // Feature flags
  static const Map<String, bool> featureFlags = {
    'ai_video_generation': true,
    'live_ai_classes': true,
    'vr_classrooms': true,
    'ar_overlays': true,
    'peer_learning': true,
    'offline_mode': true,
    'adaptive_learning': true,
    'gamification': true,
    'social_features': true,
    'advanced_analytics': true,
  };
  
  // Performance settings
  static const int maxConcurrentDownloads = 3;
  static const int cacheExpirationDays = 7;
  static const int maxCachedVideos = 10;
  static const int backgroundSyncInterval = 300; // 5 minutes
  
  // Security settings
  static const int sessionTimeoutMinutes = 30;
  static const int maxLoginAttempts = 5;
  static const int lockoutDurationMinutes = 15;
  static const bool biometricAuthRequired = false;
  
  // Accessibility settings
  static const double minFontSize = 12.0;
  static const double maxFontSize = 24.0;
  static const double defaultFontSize = 16.0;
  static const bool highContrastMode = false;
  static const bool screenReaderSupport = true;
  
  // Analytics
  static const bool analyticsEnabled = true;
  static const bool crashReportingEnabled = true;
  static const bool performanceMonitoringEnabled = true;
  
  // Development settings
  static const bool debugMode = true;
  static const bool showPerformanceOverlay = false;
  static const bool enableLogging = true;
  static const String logLevel = 'info'; // debug, info, warning, error
}

class PlatformConfig {
  static bool get isDesktop => 
      TargetPlatform.windows == defaultTargetPlatform ||
      TargetPlatform.macOS == defaultTargetPlatform ||
      TargetPlatform.linux == defaultTargetPlatform;
  
  static bool get isMobile => 
      TargetPlatform.iOS == defaultTargetPlatform ||
      TargetPlatform.android == defaultTargetPlatform;
  
  static bool get isWeb => 
      kIsWeb;
  
  static bool get supportsVR => 
      TargetPlatform.android == defaultTargetPlatform ||
      isDesktop;
  
  static bool get supportsAR => 
      TargetPlatform.iOS == defaultTargetPlatform ||
      TargetPlatform.android == defaultTargetPlatform;
  
  static bool get supportsWebRTC => 
      !isWeb || (isWeb && !isMobile);
}