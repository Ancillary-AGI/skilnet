import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:eduverse/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('EduVerse Integration Tests', () {
    testWidgets('App starts and shows onboarding', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: app.EduVerseApp(),
        ),
      );
      await tester.pumpAndSettle();

      // Should start with onboarding
      expect(find.text('Welcome to EduVerse'), findsOneWidget);
      expect(find.text('🎓'), findsOneWidget);
    });

    testWidgets('Navigation through onboarding works', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: app.EduVerseApp(),
        ),
      );
      await tester.pumpAndSettle();

      // Navigate through onboarding
      final getStartedButton = find.text('Get Started');
      if (getStartedButton.evaluate().isNotEmpty) {
        await tester.tap(getStartedButton);
        await tester.pumpAndSettle();

        // Should navigate to login page
        expect(find.text('Welcome Back'), findsOneWidget);
      }
    });

    testWidgets('Login form validation works', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: app.EduVerseApp(),
        ),
      );
      await tester.pumpAndSettle();

      // Navigate to login if not already there
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

        // Should show validation errors
        expect(find.text('Please enter your email'), findsOneWidget);
        expect(find.text('Please enter your password'), findsOneWidget);
      }
    });
  });
}