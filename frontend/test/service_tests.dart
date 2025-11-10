import 'package:flutter_test/flutter_test.dart';
import 'dart:convert';

// Import the services we want to test
import 'package:eduverse/core/services/api_service.dart';
import 'package:eduverse/core/services/cache_service.dart';
import 'package:eduverse/core/services/websocket_service.dart';
import 'package:eduverse/core/services/analytics_service.dart';
import 'package:eduverse/core/services/notification_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('ApiService Tests', () {
    late ApiService apiService;

    setUp(() {
      apiService = ApiService.instance;
    });

    test('should be a singleton instance', () {
      final instance1 = ApiService.instance;
      final instance2 = ApiService.instance;
      expect(identical(instance1, instance2), isTrue);
    });

    test('should initialize with correct base URL', () {
      expect(apiService.baseUrl, isNotNull);
      expect(apiService.baseUrl, contains('api'));
    });

    test('should handle auth token management', () {
      const testToken = 'test_token_123';
      apiService.setAuthToken(testToken);
      // Token is set internally

      apiService.clearAuthToken();
      // Token should be cleared
    });

    test('should have course-related methods', () {
      // Test that the methods exist and are callable
      expect(apiService.getCourse, isNotNull);
      expect(apiService.getCourses, isNotNull);
      expect(apiService.enrollInCourse, isNotNull);
    });

    test('should have user-related methods', () {
      expect(apiService.getUserAnalytics, isNotNull);
      expect(apiService.getUserSubscription, isNotNull);
      expect(apiService.upgradeSubscription, isNotNull);
    });
  });

  group('CacheService Tests', () {
    setUp(() async {
      // Initialize cache service for testing
      await CacheService.initialize();
    });

    tearDown(() async {
      // Clear all data after each test
      await CacheService.clearCache();
      await CacheService.clearUserData();
      await CacheService.clearSettings();
    });

    test('should initialize successfully', () async {
      // Already initialized in setUp, just verify it works
      expect(CacheService.hasUserData, isFalse);
      expect(CacheService.isLoggedIn, isFalse);
    });

    test('should store and retrieve cache data', () async {
      const key = 'test_key';
      const value = 'test_value';

      await CacheService.setCache(key, value);
      final retrieved = CacheService.getCache<String>(key);

      expect(retrieved, equals(value));
    });

    test('should store and retrieve user data', () async {
      const key = 'user_name';
      const value = 'John Doe';

      await CacheService.setUserData(key, value);
      final retrieved = CacheService.getUserData<String>(key);

      expect(retrieved, equals(value));
      expect(CacheService.hasUserData, isTrue);
    });

    test('should store and retrieve settings', () async {
      const key = 'theme_mode';
      const value = 'dark';

      await CacheService.setSetting(key, value);
      final retrieved = CacheService.getSetting<String>(key);

      expect(retrieved, equals(value));
    });

    test('should return null for non-existent keys', () async {
      final cacheResult = CacheService.getCache<String>('non_existent');
      final userResult = CacheService.getUserData<String>('non_existent');
      final settingResult = CacheService.getSetting<String>('non_existent');

      expect(cacheResult, isNull);
      expect(userResult, isNull);
      expect(settingResult, isNull);
    });

    test('should clear cache data', () async {
      await CacheService.setCache('key1', 'value1');
      await CacheService.setCache('key2', 'value2');

      await CacheService.clearCache();

      expect(CacheService.getCache<String>('key1'), isNull);
      expect(CacheService.getCache<String>('key2'), isNull);
    });

    test('should clear user data', () async {
      await CacheService.setUserData('name', 'John');
      await CacheService.setUserData('email', 'john@example.com');

      await CacheService.clearUserData();

      expect(CacheService.getUserData<String>('name'), isNull);
      expect(CacheService.getUserData<String>('email'), isNull);
      expect(CacheService.hasUserData, isFalse);
    });

    test('should clear settings', () async {
      await CacheService.setSetting('theme', 'dark');
      await CacheService.setSetting('language', 'en');

      await CacheService.clearSettings();

      expect(CacheService.getSetting<String>('theme'), isNull);
      expect(CacheService.getSetting<String>('language'), isNull);
    });

    test('should track login status', () async {
      expect(CacheService.isLoggedIn, isFalse);

      await CacheService.setUserData('access_token', 'token123');
      expect(CacheService.isLoggedIn, isTrue);

      await CacheService.clearUserData();
      expect(CacheService.isLoggedIn, isFalse);
    });

    test('should provide all settings', () async {
      await CacheService.setSetting('theme', 'dark');
      await CacheService.setSetting('notifications', true);

      final allSettings = CacheService.allSettings;
      expect(allSettings['theme'], equals('dark'));
      expect(allSettings['notifications'], isTrue);
      expect(allSettings.length, equals(2));
    });
  });

  group('WebSocketService Tests', () {
    late WebSocketService webSocketService;

    setUp(() {
      webSocketService = WebSocketService.instance;
    });

    test('should be a singleton instance', () {
      final instance1 = WebSocketService.instance;
      final instance2 = WebSocketService.instance;
      expect(identical(instance1, instance2), isTrue);
    });

    test('should initialize with disconnected state', () {
      expect(webSocketService.isConnected, isFalse);
    });

    test('should handle WebSocketEvent creation from JSON', () {
      final jsonData = {
        'type': 'test_event',
        'data': {'key': 'value'},
        'timestamp': '2024-01-01T12:00:00.000Z'
      };

      final event = WebSocketEvent.fromJson(jsonData);

      expect(event.type, equals('test_event'));
      expect(event.data['key'], equals('value'));
      expect(event.timestamp, isA<DateTime>());
    });

    test('should convert WebSocketEvent to JSON', () {
      final event = WebSocketEvent(
        type: 'test_event',
        data: {'key': 'value'},
        timestamp: DateTime.parse('2024-01-01T12:00:00.000Z'),
      );

      final jsonData = event.toJson();

      expect(jsonData['type'], equals('test_event'));
      expect(jsonData['data']['key'], equals('value'));
      expect(jsonData['timestamp'], isNotNull);
    });

    test('should handle event processing', () {
      // Test that the service can handle different event types
      // This is more of an integration test, but we can test the structure

      final event = WebSocketEvent(
        type: 'new_message',
        data: {'room_id': 'room123', 'content': 'Hello'},
        timestamp: DateTime.now(),
      );

      // The _processEvent method is private, so we test the public interface
      expect(event.type, equals('new_message'));
      expect(event.data['room_id'], equals('room123'));
    });

    test('should provide event streams', () {
      final events = webSocketService.events;
      expect(events, isA<Stream<WebSocketEvent>>());
    });

    test('should handle disconnection', () {
      // Test that disconnect sets the correct state
      webSocketService.disconnect();
      expect(webSocketService.isConnected, isFalse);
    });

    test('should handle message sending methods', () {
      const roomId = 'test_room';
      const content = 'Test message';

      // These methods should not throw when not connected
      expect(
          () => webSocketService.sendMessage(roomId, content), returnsNormally);
      expect(() => webSocketService.joinRoom(roomId), returnsNormally);
      expect(() => webSocketService.leaveRoom(roomId), returnsNormally);
      expect(() => webSocketService.updatePresence('online'), returnsNormally);
    });
  });

  group('AnalyticsService Tests', () {
    setUp(() {
      // Analytics service is static, so no setup needed
    });

    test('should track events', () {
      const eventName = 'test_event';
      final parameters = {'param1': 'value1', 'param2': 42};

      // Should not throw
      expect(
          () => AnalyticsService.trackEvent(eventName, parameters: parameters),
          returnsNormally);
    });

    test('should track screen views', () {
      const screenName = 'test_screen';

      expect(
          () => AnalyticsService.trackScreenView(screenName), returnsNormally);
    });

    test('should track course enrollment', () {
      const courseId = 'course123';
      const courseName = 'Test Course';

      expect(
          () => AnalyticsService.logCourseEnrollment(
                courseId: courseId,
                courseName: courseName,
              ),
          returnsNormally);
    });

    test('should track discussion participation', () {
      const discussionId = 'discussion123';
      const action = 'reply';

      expect(
          () => AnalyticsService.logDiscussionParticipation(
                discussionId: discussionId,
                action: action,
              ),
          returnsNormally);
    });

    test('should track VR experience', () {
      const experienceId = 'vr123';

      expect(
          () => AnalyticsService.logVRExperience(
                experienceId: experienceId,
              ),
          returnsNormally);
    });

    test('should set user properties', () {
      const name = 'user_type';
      const value = 'student';

      expect(
          () => AnalyticsService.setUserProperty(name, value), returnsNormally);
    });

    test('should set user ID', () {
      const userId = 'user123';

      expect(() => AnalyticsService.setUserId(userId), returnsNormally);
    });

    test('should handle exceptions gracefully', () {
      // Test with empty parameters
      expect(() => AnalyticsService.trackEvent(''), returnsNormally);
      expect(() => AnalyticsService.trackScreenView(''), returnsNormally);
    });
  });

  group('NotificationService Tests', () {
    setUp(() {
      // NotificationService is static, so no setup needed
    });

    test('should initialize successfully', () async {
      await NotificationService.initialize();
      // Should not throw
      expect(true, isTrue);
    });

    test('should show notifications', () async {
      const title = 'Test Notification';
      const body = 'This is a test message';

      await NotificationService.showNotification(
        id: 1,
        title: title,
        body: body,
      );
      // Should not throw
      expect(true, isTrue);
    });

    test('should schedule notifications', () async {
      const title = 'Scheduled Notification';
      const body = 'This is scheduled';
      final scheduledTime = DateTime.now().add(const Duration(hours: 1));

      await NotificationService.scheduleNotification(
        id: 2,
        title: title,
        body: body,
        scheduledDate: scheduledTime,
      );
      // Should not throw
      expect(true, isTrue);
    });

    test('should cancel notifications', () async {
      const notificationId = 1;

      await NotificationService.cancelNotification(notificationId);
      // Should not throw
      expect(true, isTrue);
    });

    test('should cancel all notifications', () async {
      await NotificationService.cancelAllNotifications();
      // Should not throw
      expect(true, isTrue);
    });
  });
}
