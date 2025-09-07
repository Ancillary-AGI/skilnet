import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter/semantics.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:shared_preferences/shared_preferences.dart';

enum AccessibilityFeature {
  screenReader,
  highContrast,
  largeText,
  voiceControl,
  keyboardNavigation,
  closedCaptions,
  signLanguage,
  audioDescriptions,
  brailleSupport,
  cognitiveAssistance,
  motorAssistance,
  seizureProtection,
}

enum DisabilityType {
  visual,
  hearing,
  motor,
  cognitive,
  speech,
  multiple,
}

class AccessibilityProfile {
  final String userId;
  final List<DisabilityType> disabilityTypes;
  final Map<DisabilityType, String> severityLevels;
  final List<AccessibilityFeature> preferredFeatures;
  final List<String> assistiveTechnologies;
  final Map<String, dynamic> customizations;
  final List<String> languagePreferences;
  final Map<String, dynamic> culturalConsiderations;

  AccessibilityProfile({
    required this.userId,
    required this.disabilityTypes,
    required this.severityLevels,
    required this.preferredFeatures,
    required this.assistiveTechnologies,
    required this.customizations,
    required this.languagePreferences,
    required this.culturalConsiderations,
  });

  Map<String, dynamic> toJson() => {
    'userId': userId,
    'disabilityTypes': disabilityTypes.map((e) => e.toString()).toList(),
    'severityLevels': severityLevels.map((k, v) => MapEntry(k.toString(), v)),
    'preferredFeatures': preferredFeatures.map((e) => e.toString()).toList(),
    'assistiveTechnologies': assistiveTechnologies,
    'customizations': customizations,
    'languagePreferences': languagePreferences,
    'culturalConsiderations': culturalConsiderations,
  };

  factory AccessibilityProfile.fromJson(Map<String, dynamic> json) {
    return AccessibilityProfile(
      userId: json['userId'],
      disabilityTypes: (json['disabilityTypes'] as List)
          .map((e) => DisabilityType.values.firstWhere((type) => type.toString() == e))
          .toList(),
      severityLevels: Map<DisabilityType, String>.fromEntries(
        (json['severityLevels'] as Map<String, dynamic>).entries.map(
          (entry) => MapEntry(
            DisabilityType.values.firstWhere((type) => type.toString() == entry.key),
            entry.value,
          ),
        ),
      ),
      preferredFeatures: (json['preferredFeatures'] as List)
          .map((e) => AccessibilityFeature.values.firstWhere((feature) => feature.toString() == e))
          .toList(),
      assistiveTechnologies: List<String>.from(json['assistiveTechnologies']),
      customizations: json['customizations'],
      languagePreferences: List<String>.from(json['languagePreferences']),
      culturalConsiderations: json['culturalConsiderations'],
    );
  }
}

class AccessibilityService {
  static final AccessibilityService _instance = AccessibilityService._internal();
  factory AccessibilityService() => _instance;
  AccessibilityService._internal();

  late SharedPreferences _prefs;
  late FlutterTts _tts;
  late SpeechToText _speechToText;
  
  AccessibilityProfile? _currentProfile;
  bool _isInitialized = false;
  
  // TTS state
  bool _isSpeaking = false;
  double _speechRate = 0.5;
  double _speechPitch = 1.0;
  double _speechVolume = 1.0;
  String _selectedVoice = '';
  
  // Speech recognition state
  bool _isListening = false;
  String _recognizedText = '';
  
  // Screen reader state
  bool _screenReaderEnabled = false;
  
  // High contrast state
  bool _highContrastEnabled = false;
  
  // Large text state
  double _textScaleFactor = 1.0;
  
  // Voice control state
  bool _voiceControlEnabled = false;
  Map<String, VoidCallback> _voiceCommands = {};
  
  // Keyboard navigation state
  bool _keyboardNavigationEnabled = false;
  
  // Cognitive assistance state
  bool _cognitiveAssistanceEnabled = false;
  bool _simplifiedInterfaceEnabled = false;
  bool _memoryAidsEnabled = false;
  
  // Motor assistance state
  bool _motorAssistanceEnabled = false;
  bool _switchControlEnabled = false;
  double _dwellTime = 1.0;
  
  // Seizure protection state
  bool _seizureProtectionEnabled = false;
  bool _reduceMotionEnabled = false;
  
  // Streams for real-time updates
  final StreamController<AccessibilityProfile?> _profileController = 
      StreamController<AccessibilityProfile?>.broadcast();
  final StreamController<String> _speechController = 
      StreamController<String>.broadcast();
  final StreamController<String> _recognitionController = 
      StreamController<String>.broadcast();
  final StreamController<Map<String, dynamic>> _settingsController = 
      StreamController<Map<String, dynamic>>.broadcast();

  // Getters
  AccessibilityProfile? get currentProfile => _currentProfile;
  bool get isInitialized => _isInitialized;
  bool get isSpeaking => _isSpeaking;
  bool get isListening => _isListening;
  bool get screenReaderEnabled => _screenReaderEnabled;
  bool get highContrastEnabled => _highContrastEnabled;
  double get textScaleFactor => _textScaleFactor;
  bool get voiceControlEnabled => _voiceControlEnabled;
  bool get keyboardNavigationEnabled => _keyboardNavigationEnabled;
  bool get cognitiveAssistanceEnabled => _cognitiveAssistanceEnabled;
  bool get motorAssistanceEnabled => _motorAssistanceEnabled;
  bool get seizureProtectionEnabled => _seizureProtectionEnabled;
  
  // Streams
  Stream<AccessibilityProfile?> get profileStream => _profileController.stream;
  Stream<String> get speechStream => _speechController.stream;
  Stream<String> get recognitionStream => _recognitionController.stream;
  Stream<Map<String, dynamic>> get settingsStream => _settingsController.stream;

  Future<void> initialize() async {
    try {
      _prefs = await SharedPreferences.getInstance();
      
      // Initialize TTS
      _tts = FlutterTts();
      await _initializeTts();
      
      // Initialize Speech Recognition
      _speechToText = SpeechToText();
      await _initializeSpeechRecognition();
      
      // Load saved profile
      await _loadAccessibilityProfile();
      
      // Apply saved settings
      await _applyAccessibilitySettings();
      
      _isInitialized = true;
      debugPrint('AccessibilityService initialized successfully');
      
    } catch (e) {
      debugPrint('Failed to initialize AccessibilityService: $e');
    }
  }

  Future<void> _initializeTts() async {
    try {
      // Set up TTS callbacks
      _tts.setStartHandler(() {
        _isSpeaking = true;
        _speechController.add('started');
      });
      
      _tts.setCompletionHandler(() {
        _isSpeaking = false;
        _speechController.add('completed');
      });
      
      _tts.setErrorHandler((message) {
        _isSpeaking = false;
        _speechController.add('error: $message');
      });
      
      // Configure TTS settings
      await _tts.setSpeechRate(_speechRate);
      await _tts.setPitch(_speechPitch);
      await _tts.setVolume(_speechVolume);
      
      // Get available voices
      final voices = await _tts.getVoices;
      if (voices.isNotEmpty && _selectedVoice.isEmpty) {
        _selectedVoice = voices.first['name'];
        await _tts.setVoice({'name': _selectedVoice, 'locale': 'en-US'});
      }
      
    } catch (e) {
      debugPrint('Failed to initialize TTS: $e');
    }
  }

  Future<void> _initializeSpeechRecognition() async {
    try {
      final available = await _speechToText.initialize(
        onStatus: (status) {
          _isListening = status == 'listening';
          _recognitionController.add('status: $status');
        },
        onError: (error) {
          _isListening = false;
          _recognitionController.add('error: ${error.errorMsg}');
        },
      );
      
      if (!available) {
        debugPrint('Speech recognition not available');
      }
      
    } catch (e) {
      debugPrint('Failed to initialize speech recognition: $e');
    }
  }

  Future<void> createAccessibilityProfile(Map<String, dynamic> assessmentData) async {
    try {
      // Analyze assessment data
      final disabilityTypes = _analyzeDisabilityTypes(assessmentData);
      final severityLevels = _determineSeverityLevels(assessmentData);
      final recommendedFeatures = _recommendAccessibilityFeatures(disabilityTypes, severityLevels);
      final assistiveTech = _detectAssistiveTechnologies(assessmentData);
      
      // Create profile
      _currentProfile = AccessibilityProfile(
        userId: assessmentData['userId'] ?? 'anonymous',
        disabilityTypes: disabilityTypes,
        severityLevels: severityLevels,
        preferredFeatures: recommendedFeatures,
        assistiveTechnologies: assistiveTech,
        customizations: _generateDefaultCustomizations(disabilityTypes),
        languagePreferences: List<String>.from(assessmentData['languages'] ?? ['en']),
        culturalConsiderations: assessmentData['culturalFactors'] ?? {},
      );
      
      // Save profile
      await _saveAccessibilityProfile();
      
      // Apply settings
      await _applyAccessibilitySettings();
      
      // Notify listeners
      _profileController.add(_currentProfile);
      
    } catch (e) {
      debugPrint('Failed to create accessibility profile: $e');
    }
  }

  Future<void> updateAccessibilityProfile(AccessibilityProfile profile) async {
    _currentProfile = profile;
    await _saveAccessibilityProfile();
    await _applyAccessibilitySettings();
    _profileController.add(_currentProfile);
  }

  Future<void> _loadAccessibilityProfile() async {
    try {
      final profileJson = _prefs.getString('accessibility_profile');
      if (profileJson != null) {
        final profileData = jsonDecode(profileJson);
        _currentProfile = AccessibilityProfile.fromJson(profileData);
      }
    } catch (e) {
      debugPrint('Failed to load accessibility profile: $e');
    }
  }

  Future<void> _saveAccessibilityProfile() async {
    if (_currentProfile != null) {
      final profileJson = jsonEncode(_currentProfile!.toJson());
      await _prefs.setString('accessibility_profile', profileJson);
    }
  }

  Future<void> _applyAccessibilitySettings() async {
    if (_currentProfile == null) return;
    
    // Apply screen reader settings
    if (_currentProfile!.preferredFeatures.contains(AccessibilityFeature.screenReader)) {
      await enableScreenReader();
    }
    
    // Apply high contrast settings
    if (_currentProfile!.preferredFeatures.contains(AccessibilityFeature.highContrast)) {
      await enableHighContrast();
    }
    
    // Apply large text settings
    if (_currentProfile!.preferredFeatures.contains(AccessibilityFeature.largeText)) {
      final fontSize = _currentProfile!.customizations['font_size'] ?? 1.2;
      await setTextScaleFactor(fontSize);
    }
    
    // Apply voice control settings
    if (_currentProfile!.preferredFeatures.contains(AccessibilityFeature.voiceControl)) {
      await enableVoiceControl();
    }
    
    // Apply keyboard navigation settings
    if (_currentProfile!.preferredFeatures.contains(AccessibilityFeature.keyboardNavigation)) {
      await enableKeyboardNavigation();
    }
    
    // Apply cognitive assistance settings
    if (_currentProfile!.preferredFeatures.contains(AccessibilityFeature.cognitiveAssistance)) {
      await enableCognitiveAssistance();
    }
    
    // Apply motor assistance settings
    if (_currentProfile!.preferredFeatures.contains(AccessibilityFeature.motorAssistance)) {
      await enableMotorAssistance();
    }
    
    // Apply seizure protection settings
    if (_currentProfile!.preferredFeatures.contains(AccessibilityFeature.seizureProtection)) {
      await enableSeizureProtection();
    }
    
    // Notify settings change
    _notifySettingsChange();
  }

  // Screen Reader functionality
  Future<void> enableScreenReader() async {
    _screenReaderEnabled = true;
    await _prefs.setBool('screen_reader_enabled', true);
    
    // Enable semantic announcements
    SemanticsService.announce('Screen reader enabled', TextDirection.ltr);
    
    _notifySettingsChange();
  }

  Future<void> disableScreenReader() async {
    _screenReaderEnabled = false;
    await _prefs.setBool('screen_reader_enabled', false);
    _notifySettingsChange();
  }

  Future<void> speak(String text, {bool interrupt = false}) async {
    if (!_screenReaderEnabled && !_voiceControlEnabled) return;
    
    try {
      if (interrupt && _isSpeaking) {
        await _tts.stop();
      }
      
      await _tts.speak(text);
    } catch (e) {
      debugPrint('Failed to speak text: $e');
    }
  }

  Future<void> stopSpeaking() async {
    await _tts.stop();
  }

  Future<void> pauseSpeaking() async {
    await _tts.pause();
  }

  Future<void> resumeSpeaking() async {
    // Note: FlutterTts doesn't have a resume method, so we'll need to track state
  }

  // High Contrast functionality
  Future<void> enableHighContrast() async {
    _highContrastEnabled = true;
    await _prefs.setBool('high_contrast_enabled', true);
    _notifySettingsChange();
  }

  Future<void> disableHighContrast() async {
    _highContrastEnabled = false;
    await _prefs.setBool('high_contrast_enabled', false);
    _notifySettingsChange();
  }

  // Large Text functionality
  Future<void> setTextScaleFactor(double factor) async {
    _textScaleFactor = factor.clamp(0.8, 3.0);
    await _prefs.setDouble('text_scale_factor', _textScaleFactor);
    _notifySettingsChange();
  }

  Future<void> increaseTextSize() async {
    await setTextScaleFactor(_textScaleFactor + 0.1);
  }

  Future<void> decreaseTextSize() async {
    await setTextScaleFactor(_textScaleFactor - 0.1);
  }

  // Voice Control functionality
  Future<void> enableVoiceControl() async {
    _voiceControlEnabled = true;
    await _prefs.setBool('voice_control_enabled', true);
    
    // Set up default voice commands
    _setupDefaultVoiceCommands();
    
    _notifySettingsChange();
  }

  Future<void> disableVoiceControl() async {
    _voiceControlEnabled = false;
    await _prefs.setBool('voice_control_enabled', false);
    
    if (_isListening) {
      await stopListening();
    }
    
    _notifySettingsChange();
  }

  Future<void> startListening() async {
    if (!_voiceControlEnabled || !_speechToText.isAvailable) return;
    
    try {
      await _speechToText.listen(
        onResult: (result) {
          _recognizedText = result.recognizedWords;
          _recognitionController.add(_recognizedText);
          
          if (result.finalResult) {
            _processVoiceCommand(_recognizedText);
          }
        },
        listenFor: const Duration(seconds: 30),
        pauseFor: const Duration(seconds: 3),
      );
    } catch (e) {
      debugPrint('Failed to start listening: $e');
    }
  }

  Future<void> stopListening() async {
    await _speechToText.stop();
  }

  void registerVoiceCommand(String command, VoidCallback callback) {
    _voiceCommands[command.toLowerCase()] = callback;
  }

  void _setupDefaultVoiceCommands() {
    _voiceCommands.clear();
    
    // Navigation commands
    registerVoiceCommand('go home', () => debugPrint('Navigate to home'));
    registerVoiceCommand('go back', () => debugPrint('Navigate back'));
    registerVoiceCommand('open menu', () => debugPrint('Open menu'));
    registerVoiceCommand('close menu', () => debugPrint('Close menu'));
    
    // Accessibility commands
    registerVoiceCommand('read page', () => _readCurrentPage());
    registerVoiceCommand('stop reading', () => stopSpeaking());
    registerVoiceCommand('increase text size', () => increaseTextSize());
    registerVoiceCommand('decrease text size', () => decreaseTextSize());
    registerVoiceCommand('high contrast on', () => enableHighContrast());
    registerVoiceCommand('high contrast off', () => disableHighContrast());
  }

  void _processVoiceCommand(String recognizedText) {
    final command = recognizedText.toLowerCase().trim();
    
    for (final voiceCommand in _voiceCommands.keys) {
      if (command.contains(voiceCommand)) {
        _voiceCommands[voiceCommand]?.call();
        speak('Command executed: $voiceCommand');
        return;
      }
    }
    
    // If no exact match, try fuzzy matching
    final bestMatch = _findBestCommandMatch(command);
    if (bestMatch != null) {
      _voiceCommands[bestMatch]?.call();
      speak('Command executed: $bestMatch');
    } else {
      speak('Command not recognized: $command');
    }
  }

  String? _findBestCommandMatch(String input) {
    // Simple fuzzy matching implementation
    int bestScore = 0;
    String? bestMatch;
    
    for (final command in _voiceCommands.keys) {
      final score = _calculateSimilarity(input, command);
      if (score > bestScore && score > 0.7) {
        bestScore = score;
        bestMatch = command;
      }
    }
    
    return bestMatch;
  }

  double _calculateSimilarity(String a, String b) {
    // Simple Levenshtein distance-based similarity
    final matrix = List.generate(
      a.length + 1,
      (i) => List.generate(b.length + 1, (j) => 0),
    );
    
    for (int i = 0; i <= a.length; i++) {
      matrix[i][0] = i;
    }
    
    for (int j = 0; j <= b.length; j++) {
      matrix[0][j] = j;
    }
    
    for (int i = 1; i <= a.length; i++) {
      for (int j = 1; j <= b.length; j++) {
        final cost = a[i - 1] == b[j - 1] ? 0 : 1;
        matrix[i][j] = [
          matrix[i - 1][j] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j - 1] + cost,
        ].reduce((a, b) => a < b ? a : b);
      }
    }
    
    final maxLength = a.length > b.length ? a.length : b.length;
    return 1.0 - (matrix[a.length][b.length] / maxLength);
  }

  // Keyboard Navigation functionality
  Future<void> enableKeyboardNavigation() async {
    _keyboardNavigationEnabled = true;
    await _prefs.setBool('keyboard_navigation_enabled', true);
    _notifySettingsChange();
  }

  Future<void> disableKeyboardNavigation() async {
    _keyboardNavigationEnabled = false;
    await _prefs.setBool('keyboard_navigation_enabled', false);
    _notifySettingsChange();
  }

  // Cognitive Assistance functionality
  Future<void> enableCognitiveAssistance() async {
    _cognitiveAssistanceEnabled = true;
    await _prefs.setBool('cognitive_assistance_enabled', true);
    
    // Enable related features
    _simplifiedInterfaceEnabled = true;
    _memoryAidsEnabled = true;
    
    _notifySettingsChange();
  }

  Future<void> disableCognitiveAssistance() async {
    _cognitiveAssistanceEnabled = false;
    await _prefs.setBool('cognitive_assistance_enabled', false);
    
    _simplifiedInterfaceEnabled = false;
    _memoryAidsEnabled = false;
    
    _notifySettingsChange();
  }

  // Motor Assistance functionality
  Future<void> enableMotorAssistance() async {
    _motorAssistanceEnabled = true;
    await _prefs.setBool('motor_assistance_enabled', true);
    
    // Configure dwell time
    _dwellTime = _currentProfile?.customizations['dwell_time'] ?? 1.0;
    
    _notifySettingsChange();
  }

  Future<void> disableMotorAssistance() async {
    _motorAssistanceEnabled = false;
    await _prefs.setBool('motor_assistance_enabled', false);
    _notifySettingsChange();
  }

  Future<void> setDwellTime(double seconds) async {
    _dwellTime = seconds.clamp(0.5, 5.0);
    await _prefs.setDouble('dwell_time', _dwellTime);
    _notifySettingsChange();
  }

  // Seizure Protection functionality
  Future<void> enableSeizureProtection() async {
    _seizureProtectionEnabled = true;
    _reduceMotionEnabled = true;
    
    await _prefs.setBool('seizure_protection_enabled', true);
    await _prefs.setBool('reduce_motion_enabled', true);
    
    _notifySettingsChange();
  }

  Future<void> disableSeizureProtection() async {
    _seizureProtectionEnabled = false;
    _reduceMotionEnabled = false;
    
    await _prefs.setBool('seizure_protection_enabled', false);
    await _prefs.setBool('reduce_motion_enabled', false);
    
    _notifySettingsChange();
  }

  // Content reading functionality
  Future<void> _readCurrentPage() async {
    // This would need to be implemented with the current page context
    await speak('Reading current page content');
  }

  Future<void> readText(String text) async {
    await speak(text);
  }

  Future<void> describeImage(String description) async {
    await speak('Image description: $description');
  }

  Future<void> announceNavigation(String destination) async {
    await speak('Navigating to $destination');
  }

  // Settings management
  Future<void> resetToDefaults() async {
    _screenReaderEnabled = false;
    _highContrastEnabled = false;
    _textScaleFactor = 1.0;
    _voiceControlEnabled = false;
    _keyboardNavigationEnabled = false;
    _cognitiveAssistanceEnabled = false;
    _motorAssistanceEnabled = false;
    _seizureProtectionEnabled = false;
    
    await _prefs.clear();
    _currentProfile = null;
    
    _notifySettingsChange();
    _profileController.add(null);
  }

  Map<String, dynamic> getCurrentSettings() {
    return {
      'screen_reader_enabled': _screenReaderEnabled,
      'high_contrast_enabled': _highContrastEnabled,
      'text_scale_factor': _textScaleFactor,
      'voice_control_enabled': _voiceControlEnabled,
      'keyboard_navigation_enabled': _keyboardNavigationEnabled,
      'cognitive_assistance_enabled': _cognitiveAssistanceEnabled,
      'motor_assistance_enabled': _motorAssistanceEnabled,
      'seizure_protection_enabled': _seizureProtectionEnabled,
      'speech_rate': _speechRate,
      'speech_pitch': _speechPitch,
      'speech_volume': _speechVolume,
      'dwell_time': _dwellTime,
    };
  }

  void _notifySettingsChange() {
    _settingsController.add(getCurrentSettings());
  }

  // Helper methods for profile creation
  List<DisabilityType> _analyzeDisabilityTypes(Map<String, dynamic> data) {
    final types = <DisabilityType>[];
    
    if (data['visual_impairment'] == true) types.add(DisabilityType.visual);
    if (data['hearing_impairment'] == true) types.add(DisabilityType.hearing);
    if (data['motor_impairment'] == true) types.add(DisabilityType.motor);
    if (data['cognitive_impairment'] == true) types.add(DisabilityType.cognitive);
    if (data['speech_impairment'] == true) types.add(DisabilityType.speech);
    
    if (types.length > 1) types.add(DisabilityType.multiple);
    
    return types;
  }

  Map<DisabilityType, String> _determineSeverityLevels(Map<String, dynamic> data) {
    final levels = <DisabilityType, String>{};
    
    for (final type in DisabilityType.values) {
      final key = '${type.toString().split('.').last}_severity';
      levels[type] = data[key] ?? 'mild';
    }
    
    return levels;
  }

  List<AccessibilityFeature> _recommendAccessibilityFeatures(
    List<DisabilityType> types,
    Map<DisabilityType, String> severities,
  ) {
    final features = <AccessibilityFeature>[];
    
    for (final type in types) {
      switch (type) {
        case DisabilityType.visual:
          features.addAll([
            AccessibilityFeature.screenReader,
            AccessibilityFeature.highContrast,
            AccessibilityFeature.largeText,
            AccessibilityFeature.audioDescriptions,
          ]);
          break;
        case DisabilityType.hearing:
          features.addAll([
            AccessibilityFeature.closedCaptions,
            AccessibilityFeature.signLanguage,
          ]);
          break;
        case DisabilityType.motor:
          features.addAll([
            AccessibilityFeature.voiceControl,
            AccessibilityFeature.keyboardNavigation,
            AccessibilityFeature.motorAssistance,
          ]);
          break;
        case DisabilityType.cognitive:
          features.addAll([
            AccessibilityFeature.cognitiveAssistance,
            AccessibilityFeature.largeText,
          ]);
          break;
        case DisabilityType.speech:
          features.add(AccessibilityFeature.voiceControl);
          break;
        default:
          break;
      }
    }
    
    return features.toSet().toList();
  }

  List<String> _detectAssistiveTechnologies(Map<String, dynamic> data) {
    final technologies = <String>[];
    
    if (data['screen_reader'] == true) technologies.add('screen_reader');
    if (data['switch_control'] == true) technologies.add('switch_control');
    if (data['eye_tracking'] == true) technologies.add('eye_tracking');
    if (data['voice_control'] == true) technologies.add('voice_control');
    
    return technologies;
  }

  Map<String, dynamic> _generateDefaultCustomizations(List<DisabilityType> types) {
    final customizations = <String, dynamic>{};
    
    if (types.contains(DisabilityType.visual)) {
      customizations['font_size'] = 1.2;
      customizations['color_scheme'] = 'high_contrast';
      customizations['speech_rate'] = 0.5;
    }
    
    if (types.contains(DisabilityType.motor)) {
      customizations['dwell_time'] = 1.0;
      customizations['switch_scan_speed'] = 'medium';
    }
    
    if (types.contains(DisabilityType.cognitive)) {
      customizations['simplified_interface'] = true;
      customizations['memory_aids'] = true;
    }
    
    return customizations;
  }

  void dispose() {
    _profileController.close();
    _speechController.close();
    _recognitionController.close();
    _settingsController.close();
    _tts.stop();
    _speechToText.stop();
  }
}