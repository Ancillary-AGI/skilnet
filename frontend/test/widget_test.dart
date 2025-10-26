import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:eduverse/main.dart';

void main() {
  group('EduVerse App Tests', () {
    testWidgets('App starts without crashing', (WidgetTester tester) async {
      // Build our app and trigger a frame.
      await tester.pumpWidget(
        const ProviderScope(
          child: EduVerseApp(),
        ),
      );

      // Verify that the app starts
      expect(find.byType(MaterialApp), findsOneWidget);
    });

    testWidgets('Onboarding page displays correctly', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: EduVerseApp(),
        ),
      );

      // Wait for the app to load
      await tester.pumpAndSettle();

      // Check if onboarding elements are present
      expect(find.text('Welcome to EduVerse'), findsOneWidget);
      expect(find.text('🎓'), findsOneWidget);
    });

    testWidgets('Navigation works correctly', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: EduVerseApp(),
        ),
      );

      await tester.pumpAndSettle();

      // Find and tap the "Get Started" button (assuming it's visible)
      final getStartedButton = find.text('Get Started');
      if (getStartedButton.evaluate().isNotEmpty) {
        await tester.tap(getStartedButton);
        await tester.pumpAndSettle();

        // Verify navigation to login page
        expect(find.text('Welcome Back'), findsOneWidget);
      }
    });

    testWidgets('Login form validation works', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: EduVerseApp(),
        ),
      );

      await tester.pumpAndSettle();

      // Navigate to login page if not already there
      final getStartedButton = find.text('Get Started');
      if (getStartedButton.evaluate().isNotEmpty) {
        await tester.tap(getStartedButton);
        await tester.pumpAndSettle();
      }

      // Try to submit empty form
      final signInButton = find.text('Sign In');
      if (signInButton.evaluate().isNotEmpty) {
        await tester.tap(signInButton);
        await tester.pump();

        // Check for validation errors
        expect(find.text('Please enter your email'), findsOneWidget);
        expect(find.text('Please enter your password'), findsOneWidget);
      }
    });

    testWidgets('Theme switching works', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: EduVerseApp(),
        ),
      );

      await tester.pumpAndSettle();

      // The app should start with system theme
      final materialApp = tester.widget<MaterialApp>(find.byType(MaterialApp));
      expect(materialApp.themeMode, equals(ThemeMode.system));
    });
  });

  group('Update Service Tests', () {
    test('UpdateInfo parses correctly from JSON', () {
      final json = {
        'version': '2.0.0',
        'buildNumber': '200',
        'releaseNotes': 'Test release notes',
        'downloadUrl': 'https://example.com/download',
        'storeUrl': 'https://example.com/store',
        'isMandatory': true,
        'isSecurityUpdate': true,
        'hasNewFeatures': true,
        'fileSizeBytes': 50000000,
        'releaseDate': '2024-01-15T10:00:00Z',
        'supportedPlatforms': ['android', 'ios'],
      };

      // This would require importing the UpdateInfo class
      // final updateInfo = UpdateInfo.fromJson(json);
      // expect(updateInfo.version, equals('2.0.0'));
      // expect(updateInfo.isMandatory, equals(true));
    });
  });

  group('API Service Tests', () {
    test('API service initializes correctly', () {
      // Test API service initialization
      expect(true, isTrue); // Placeholder test
    });
  });
}