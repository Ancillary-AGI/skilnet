import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';

import 'package:eduverse/main.dart';
import 'package:eduverse/features/auth/providers/auth_provider.dart';
import 'package:eduverse/core/services/api_service.dart';

// Generate mocks
@GenerateMocks([ApiService])
import 'widget_test.mocks.dart';

void main() {
  group('EduVerse App Tests', () {
    late MockApiService mockApiService;

    setUp(() {
      mockApiService = MockApiService();
    });

    testWidgets('App should start with onboarding screen', (WidgetTester tester) async {
      // Build our app and trigger a frame
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(mockApiService),
          ],
          child: const EduVerseApp(),
        ),
      );

      // Verify that onboarding screen is shown
      expect(find.text('Welcome to EduVerse'), findsOneWidget);
    });

    testWidgets('Login screen should validate email format', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: const LoginScreen(),
          ),
        ),
      );

      // Enter invalid email
      await tester.enterText(find.byType(TextFormField).first, 'invalid-email');
      await tester.tap(find.text('Sign In'));
      await tester.pump();

      // Should show validation error
      expect(find.text('Please enter a valid email'), findsOneWidget);
    });

    testWidgets('Course card should display course information', (WidgetTester tester) async {
      final mockCourse = {
        'id': '1',
        'title': 'Test Course',
        'instructor': 'Test Instructor',
        'rating': 4.5,
        'students': 1000,
        'hasVR': true,
        'hasAR': false,
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CourseCard(course: mockCourse),
          ),
        ),
      );

      expect(find.text('Test Course'), findsOneWidget);
      expect(find.text('Test Instructor'), findsOneWidget);
      expect(find.text('4.5'), findsOneWidget);
      expect(find.text('VR'), findsOneWidget);
      expect(find.text('AR'), findsNothing);
    });
  });

  group('VR Classroom Tests', () {
    testWidgets('VR classroom should show connection status', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: VRClassroomScreen(roomId: 'test-room'),
          ),
        ),
      );

      // Should show connecting status initially
      expect(find.text('Connecting...'), findsOneWidget);
    });

    testWidgets('VR controls should be responsive', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: VRClassroomScreen(roomId: 'test-room'),
          ),
        ),
      );

      // Find and tap microphone button
      final micButton = find.byIcon(Icons.mic);
      expect(micButton, findsOneWidget);
      
      await tester.tap(micButton);
      await tester.pump();

      // Should toggle to muted state
      expect(find.byIcon(Icons.mic_off), findsOneWidget);
    });
  });

  group('AI Tutor Tests', () {
    testWidgets('AI tutor should respond to messages', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: AITutorScreen(),
          ),
        ),
      );

      // Enter a question
      await tester.enterText(find.byType(TextField), 'What is machine learning?');
      await tester.tap(find.byIcon(Icons.send));
      await tester.pump();

      // Should show user message
      expect(find.text('What is machine learning?'), findsOneWidget);
    });
  });

  group('Responsive Design Tests', () {
    testWidgets('Should adapt to mobile layout', (WidgetTester tester) async {
      // Set mobile screen size
      tester.binding.window.physicalSizeTestValue = const Size(375, 812);
      tester.binding.window.devicePixelRatioTestValue = 2.0;

      await tester.pumpWidget(
        ProviderScope(
          child: const EduVerseApp(),
        ),
      );

      // Should show bottom navigation on mobile
      expect(find.byType(BottomNavigationBar), findsOneWidget);
      expect(find.byType(NavigationRail), findsNothing);
    });

    testWidgets('Should adapt to tablet layout', (WidgetTester tester) async {
      // Set tablet screen size
      tester.binding.window.physicalSizeTestValue = const Size(768, 1024);
      tester.binding.window.devicePixelRatioTestValue = 2.0;

      await tester.pumpWidget(
        ProviderScope(
          child: const EduVerseApp(),
        ),
      );

      // Should show navigation rail on tablet
      expect(find.byType(NavigationRail), findsOneWidget);
      expect(find.byType(BottomNavigationBar), findsNothing);
    });

    testWidgets('Should adapt to desktop layout', (WidgetTester tester) async {
      // Set desktop screen size
      tester.binding.window.physicalSizeTestValue = const Size(1920, 1080);
      tester.binding.window.devicePixelRatioTestValue = 1.0;

      await tester.pumpWidget(
        ProviderScope(
          child: const EduVerseApp(),
        ),
      );

      // Should show navigation drawer on desktop
      expect(find.byType(Drawer), findsOneWidget);
    });
  });

  group('Accessibility Tests', () {
    testWidgets('Should have proper semantic labels', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: const EduVerseApp(),
        ),
      );

      // Check for semantic labels
      expect(find.bySemanticsLabel('Home'), findsOneWidget);
      expect(find.bySemanticsLabel('Courses'), findsOneWidget);
      expect(find.bySemanticsLabel('Profile'), findsOneWidget);
    });

    testWidgets('Should support screen reader navigation', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: const EduVerseApp(),
        ),
      );

      // Test focus traversal
      await tester.sendKeyEvent(LogicalKeyboardKey.tab);
      await tester.pump();

      // Should move focus to next focusable element
      expect(tester.binding.focusManager.primaryFocus, isNotNull);
    });
  });

  group('Performance Tests', () {
    testWidgets('Should render home screen within performance budget', (WidgetTester tester) async {
      final stopwatch = Stopwatch()..start();

      await tester.pumpWidget(
        ProviderScope(
          child: const EduVerseApp(),
        ),
      );

      await tester.pumpAndSettle();
      stopwatch.stop();

      // Should render within 100ms
      expect(stopwatch.elapsedMilliseconds, lessThan(100));
    });

    testWidgets('Should handle large course lists efficiently', (WidgetTester tester) async {
      // Mock large course list
      final largeCourseList = List.generate(1000, (index) => {
        'id': index.toString(),
        'title': 'Course $index',
        'instructor': 'Instructor $index',
      });

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            featuredCoursesProvider.overrideWith((ref) => Future.value(largeCourseList)),
          ],
          child: MaterialApp(
            home: HomeScreen(),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Should only render visible items (lazy loading)
      expect(find.text('Course 999'), findsNothing);
      expect(find.text('Course 0'), findsOneWidget);
    });
  });

  group('Integration Tests', () {
    testWidgets('Should complete full user journey', (WidgetTester tester) async {
      // Mock successful API responses
      when(mockApiService.login(any, any)).thenAnswer((_) async => {
        'access_token': 'mock_token',
        'user': {'id': '1', 'email': 'test@example.com'}
      });

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiServiceProvider.overrideWithValue(mockApiService),
          ],
          child: const EduVerseApp(),
        ),
      );

      // Start from onboarding
      expect(find.text('Welcome to EduVerse'), findsOneWidget);

      // Navigate to login
      await tester.tap(find.text('Get Started'));
      await tester.pumpAndSettle();

      // Login
      await tester.enterText(find.byType(TextFormField).first, 'test@example.com');
      await tester.enterText(find.byType(TextFormField).last, 'password123');
      await tester.tap(find.text('Sign In'));
      await tester.pumpAndSettle();

      // Should navigate to home screen
      expect(find.text('Good Morning'), findsOneWidget);
    });
  });
}

// Mock classes for testing
class MockCourseCard extends StatelessWidget {
  final Map<String, dynamic> course;

  const MockCourseCard({super.key, required this.course});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Column(
        children: [
          Text(course['title']),
          Text(course['instructor']),
          Text(course['rating'].toString()),
          if (course['hasVR']) const Text('VR'),
          if (course['hasAR']) const Text('AR'),
        ],
      ),
    );
  }
}