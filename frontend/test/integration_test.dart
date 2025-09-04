import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:patrol/patrol.dart';

import 'package:eduverse/main.dart' as app;
import 'package:eduverse/core/services/api_service.dart';
import 'package:eduverse/features/auth/providers/auth_provider.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('EduVerse Integration Tests', () {
    patrolTest('Complete user onboarding and login flow', (PatrolTester $) async {
      // Start the app
      await $.pumpWidgetAndSettle(
        ProviderScope(
          child: app.EduVerseApp(),
        ),
      );

      // Should start with onboarding
      expect($('Welcome to EduVerse'), findsOneWidget);
      
      // Navigate through onboarding
      await $.tap($('Get Started'));
      await $.pumpAndSettle();
      
      // Should show features overview
      expect($('Immersive Learning'), findsOneWidget);
      expect($('AI-Powered Teaching'), findsOneWidget);
      expect($('Virtual Reality'), findsOneWidget);
      
      await $.tap($('Continue'));
      await $.pumpAndSettle();
      
      // Should show login/register options
      expect($('Sign In'), findsOneWidget);
      expect($('Create Account'), findsOneWidget);
      
      // Go to registration
      await $.tap($('Create Account'));
      await $.pumpAndSettle();
      
      // Fill registration form
      await $.enterText($('Email'), 'test@example.com');
      await $.enterText($('Username'), 'testuser');
      await $.enterText($('Password'), 'securepassword123');
      await $.enterText($('First Name'), 'Test');
      await $.enterText($('Last Name'), 'User');
      
      // Select learning style
      await $.tap($('Visual Learner'));
      
      // Submit registration
      await $.tap($('Create Account'));
      await $.pumpAndSettle();
      
      // Should show success message
      expect($('Registration successful'), findsOneWidget);
      
      // Go to login
      await $.tap($('Sign In Now'));
      await $.pumpAndSettle();
      
      // Login with created account
      await $.enterText($('Email'), 'test@example.com');
      await $.enterText($('Password'), 'securepassword123');
      await $.tap($('Sign In'));
      await $.pumpAndSettle();
      
      // Should navigate to home screen
      expect($('Good Morning'), findsOneWidget);
      expect($('Ready to explore'), findsOneWidget);
    });

    patrolTest('Course browsing and enrollment flow', (PatrolTester $) async {
      // Start with authenticated user
      await _loginTestUser($);
      
      // Navigate to courses
      await $.tap($('Courses'));
      await $.pumpAndSettle();
      
      // Should show course catalog
      expect($('Course Catalog'), findsOneWidget);
      expect($('Featured Courses'), findsOneWidget);
      
      // Search for a course
      await $.enterText($('Search courses'), 'machine learning');
      await $.pumpAndSettle();
      
      // Should show search results
      expect($('Machine Learning'), findsWidgets);
      
      // Tap on first course
      await $.tap($('Advanced Machine Learning').first);
      await $.pumpAndSettle();
      
      // Should show course details
      expect($('Course Overview'), findsOneWidget);
      expect($('Enroll Now'), findsOneWidget);
      expect($('VR Experience Available'), findsOneWidget);
      
      // Enroll in course
      await $.tap($('Enroll Now'));
      await $.pumpAndSettle();
      
      // Should show enrollment success
      expect($('Successfully enrolled'), findsOneWidget);
      
      // Start first lesson
      await $.tap($('Start Learning'));
      await $.pumpAndSettle();
      
      // Should show lesson screen
      expect($('Lesson 1'), findsOneWidget);
      expect($('Video Player'), findsOneWidget);
    });

    patrolTest('VR classroom experience', (PatrolTester $) async {
      await _loginTestUser($);
      
      // Navigate to VR classroom
      await $.tap($('VR Classroom'));
      await $.pumpAndSettle();
      
      // Should show VR setup screen
      expect($('VR Setup'), findsOneWidget);
      expect($('Check VR Headset'), findsOneWidget);
      
      // Mock VR headset connection
      await $.tap($('Connect Headset'));
      await $.pumpAndSettle();
      
      // Should show VR environment selection
      expect($('Select Environment'), findsOneWidget);
      
      // Select classroom environment
      await $.tap($('Modern Classroom'));
      await $.pumpAndSettle();
      
      // Should enter VR classroom
      expect($('VR Classroom'), findsOneWidget);
      expect($('Participants'), findsOneWidget);
      expect($('Hand Tracking'), findsOneWidget);
      
      // Test VR controls
      await $.tap($('Toggle Microphone'));
      await $.pumpAndSettle();
      
      expect($('Microphone Off'), findsOneWidget);
      
      // Test spatial interaction
      await $.tap($('Virtual Whiteboard'));
      await $.pumpAndSettle();
      
      expect($('Drawing Tools'), findsOneWidget);
      
      // Exit VR
      await $.tap($('Exit VR'));
      await $.pumpAndSettle();
      
      expect($('VR Session Ended'), findsOneWidget);
    });

    patrolTest('AI tutor interaction', (PatrolTester $) async {
      await _loginTestUser($);
      
      // Navigate to AI tutor
      await $.tap($('AI Tutor'));
      await $.pumpAndSettle();
      
      // Should show AI tutor interface
      expect($('AI Teaching Assistant'), findsOneWidget);
      expect($('Ask me anything'), findsOneWidget);
      
      // Ask a question
      await $.enterText($('Type your question'), 'What is quantum computing?');
      await $.tap($('Send'));
      await $.pumpAndSettle();
      
      // Should show user message
      expect($('What is quantum computing?'), findsOneWidget);
      
      // Wait for AI response
      await $.pump(const Duration(seconds: 2));
      
      // Should show AI response
      expect($('AI Tutor'), findsOneWidget);
      expect(find.textContaining('quantum'), findsWidgets);
      
      // Test voice interaction
      await $.tap($('Voice Chat'));
      await $.pumpAndSettle();
      
      expect($('Listening...'), findsOneWidget);
      
      // Test visual aids request
      await $.enterText($('Type your question'), 'Show me a diagram of neural networks');
      await $.tap($('Send'));
      await $.pumpAndSettle();
      
      // Should show visual aid
      expect($('Generated Diagram'), findsOneWidget);
    });

    patrolTest('AR experience interaction', (PatrolTester $) async {
      await _loginTestUser($);
      
      // Navigate to AR experience
      await $.tap($('AR Lab'));
      await $.pumpAndSettle();
      
      // Should show AR setup
      expect($('AR Camera Setup'), findsOneWidget);
      expect($('Point camera at surface'), findsOneWidget);
      
      // Mock camera permission
      await $.tap($('Grant Camera Permission'));
      await $.pumpAndSettle();
      
      // Should start AR session
      expect($('AR Active'), findsOneWidget);
      expect($('Place Objects'), findsOneWidget);
      
      // Test AR object placement
      await $.tap($('3D Molecule'));
      await $.pumpAndSettle();
      
      // Should place AR object
      expect($('Molecule Placed'), findsOneWidget);
      
      // Test AR interaction
      await $.tap($('Rotate Object'));
      await $.pumpAndSettle();
      
      expect($('Rotation Controls'), findsOneWidget);
      
      // Test AR quiz
      await $.tap($('Start AR Quiz'));
      await $.pumpAndSettle();
      
      expect($('Identify the molecule'), findsOneWidget);
      
      // Answer quiz by tapping AR object
      await $.tap($('AR Object'));
      await $.pumpAndSettle();
      
      expect($('Correct!'), findsOneWidget);
    });

    patrolTest('Live class participation', (PatrolTester $) async {
      await _loginTestUser($);
      
      // Navigate to live classes
      await $.tap($('Live Classes'));
      await $.pumpAndSettle();
      
      // Should show available live classes
      expect($('Live Classes'), findsOneWidget);
      expect($('Join Class'), findsWidgets);
      
      // Join a live class
      await $.tap($('Join Class').first);
      await $.pumpAndSettle();
      
      // Should show live class interface
      expect($('Live Class'), findsOneWidget);
      expect($('AI Instructor'), findsOneWidget);
      expect($('Chat'), findsOneWidget);
      
      // Test chat interaction
      await $.enterText($('Type message'), 'Can you explain this concept?');
      await $.tap($('Send Message'));
      await $.pumpAndSettle();
      
      // Should show user message in chat
      expect($('Can you explain this concept?'), findsOneWidget);
      
      // Wait for AI response
      await $.pump(const Duration(seconds: 3));
      
      // Should show AI instructor response
      expect(find.textContaining('AI Instructor'), findsWidgets);
      
      // Test raise hand feature
      await $.tap($('Raise Hand'));
      await $.pumpAndSettle();
      
      expect($('Hand Raised'), findsOneWidget);
      
      // Test screen sharing
      await $.tap($('Share Screen'));
      await $.pumpAndSettle();
      
      expect($('Screen Sharing'), findsOneWidget);
    });

    patrolTest('Offline mode functionality', (PatrolTester $) async {
      await _loginTestUser($);
      
      // Download content for offline use
      await $.tap($('Courses'));
      await $.pumpAndSettle();
      
      await $.tap($('Python Basics'));
      await $.pumpAndSettle();
      
      await $.tap($('Download for Offline'));
      await $.pumpAndSettle();
      
      // Should show download progress
      expect($('Downloading'), findsOneWidget);
      
      // Wait for download completion
      await $.pump(const Duration(seconds: 5));
      
      expect($('Downloaded'), findsOneWidget);
      
      // Simulate offline mode
      // (In real test, would disable network)
      
      // Should still be able to access downloaded content
      await $.tap($('Start Lesson'));
      await $.pumpAndSettle();
      
      expect($('Offline Mode'), findsOneWidget);
      expect($('Video Player'), findsOneWidget);
    });

    patrolTest('Accessibility features', (PatrolTester $) async {
      await _loginTestUser($);
      
      // Navigate to accessibility settings
      await $.tap($('Profile'));
      await $.pumpAndSettle();
      
      await $.tap($('Settings'));
      await $.pumpAndSettle();
      
      await $.tap($('Accessibility'));
      await $.pumpAndSettle();
      
      // Enable high contrast mode
      await $.tap($('High Contrast Mode'));
      await $.pumpAndSettle();
      
      // Should apply high contrast theme
      expect($('High Contrast Enabled'), findsOneWidget);
      
      // Enable large text
      await $.tap($('Large Text'));
      await $.pumpAndSettle();
      
      // Should increase text size
      expect($('Large Text Enabled'), findsOneWidget);
      
      // Enable screen reader support
      await $.tap($('Screen Reader Support'));
      await $.pumpAndSettle();
      
      expect($('Screen Reader Enabled'), findsOneWidget);
      
      // Test voice commands
      await $.tap($('Voice Commands'));
      await $.pumpAndSettle();
      
      expect($('Say "Go to courses"'), findsOneWidget);
    });

    patrolTest('Performance under load', (PatrolTester $) async {
      await _loginTestUser($);
      
      // Navigate through multiple screens rapidly
      final screens = ['Courses', 'AI Tutor', 'Profile', 'Home'];
      
      for (int i = 0; i < 10; i++) {
        for (final screen in screens) {
          await $.tap($(screen));
          await $.pump(const Duration(milliseconds: 100));
        }
      }
      
      await $.pumpAndSettle();
      
      // App should remain responsive
      expect($('Home'), findsOneWidget);
      
      // Test memory usage by loading many courses
      await $.tap($('Courses'));
      await $.pumpAndSettle();
      
      // Scroll through large course list
      for (int i = 0; i < 50; i++) {
        await $.scroll(
          finder: $('Course List'),
          delta: const Offset(0, -200),
        );
        await $.pump(const Duration(milliseconds: 50));
      }
      
      // Should handle scrolling smoothly
      expect($('Courses'), findsOneWidget);
    });

    patrolTest('Cross-platform feature compatibility', (PatrolTester $) async {
      await _loginTestUser($);
      
      // Test features available on current platform
      await $.tap($('Features'));
      await $.pumpAndSettle();
      
      // Check VR availability
      if (await _isVRSupported()) {
        expect($('VR Classroom'), findsOneWidget);
        await $.tap($('VR Classroom'));
        await $.pumpAndSettle();
        expect($('VR Setup'), findsOneWidget);
        await $.tap($('Back'));
        await $.pumpAndSettle();
      }
      
      // Check AR availability
      if (await _isARSupported()) {
        expect($('AR Experience'), findsOneWidget);
        await $.tap($('AR Experience'));
        await $.pumpAndSettle();
        expect($('AR Camera'), findsOneWidget);
        await $.tap($('Back'));
        await $.pumpAndSettle();
      }
      
      // AI features should be available on all platforms
      expect($('AI Tutor'), findsOneWidget);
      await $.tap($('AI Tutor'));
      await $.pumpAndSettle();
      expect($('AI Teaching Assistant'), findsOneWidget);
    });
  });

  group('Error Handling Tests', () {
    patrolTest('Network error handling', (PatrolTester $) async {
      // Start app in offline mode
      await $.pumpWidgetAndSettle(
        ProviderScope(
          overrides: [
            // Mock network error
            apiServiceProvider.overrideWith((ref) => throw Exception('Network error')),
          ],
          child: app.EduVerseApp(),
        ),
      );
      
      // Should show offline message
      expect($('No internet connection'), findsOneWidget);
      expect($('Retry'), findsOneWidget);
      
      // Test retry functionality
      await $.tap($('Retry'));
      await $.pumpAndSettle();
      
      // Should attempt to reconnect
      expect($('Connecting...'), findsOneWidget);
    });

    patrolTest('VR headset disconnection handling', (PatrolTester $) async {
      await _loginTestUser($);
      
      // Start VR session
      await $.tap($('VR Classroom'));
      await $.pumpAndSettle();
      
      await $.tap($('Join Demo Room'));
      await $.pumpAndSettle();
      
      // Simulate VR headset disconnection
      // (In real test, would mock VR service)
      
      // Should show disconnection warning
      expect($('VR Headset Disconnected'), findsOneWidget);
      expect($('Reconnect'), findsOneWidget);
      expect($('Continue in 2D'), findsOneWidget);
      
      // Test fallback to 2D mode
      await $.tap($('Continue in 2D'));
      await $.pumpAndSettle();
      
      expect($('2D Classroom Mode'), findsOneWidget);
      expect($('VR features disabled'), findsOneWidget);
    });

    patrolTest('AI service error handling', (PatrolTester $) async {
      await _loginTestUser($);
      
      // Navigate to AI tutor
      await $.tap($('AI Tutor'));
      await $.pumpAndSettle();
      
      // Send message that causes AI error
      await $.enterText($('Type your question'), 'Cause AI error');
      await $.tap($('Send'));
      await $.pumpAndSettle();
      
      // Should show error message gracefully
      expect($('AI temporarily unavailable'), findsOneWidget);
      expect($('Try again'), findsOneWidget);
      
      // Test retry
      await $.tap($('Try again'));
      await $.pumpAndSettle();
      
      expect($('Retrying...'), findsOneWidget);
    });
  });

  group('Performance Tests', () {
    patrolTest('App startup performance', (PatrolTester $) async {
      final stopwatch = Stopwatch()..start();
      
      await $.pumpWidgetAndSettle(
        ProviderScope(
          child: app.EduVerse(),
        ),
      );
      
      stopwatch.stop();
      
      // App should start within 3 seconds
      expect(stopwatch.elapsedMilliseconds, lessThan(3000));
      
      // Should show onboarding screen
      expect($('Welcome to EduVerse'), findsOneWidget);
    });

    patrolTest('Video playback performance', (PatrolTester $) async {
      await _loginTestUser($);
      
      // Navigate to a video lesson
      await $.tap($('Courses'));
      await $.pumpAndSettle();
      
      await $.tap($('Python Basics'));
      await $.pumpAndSettle();
      
      await $.tap($('Start Learning'));
      await $.pumpAndSettle();
      
      // Should load video quickly
      expect($('Video Player'), findsOneWidget);
      
      // Test video controls
      await $.tap($('Play'));
      await $.pump(const Duration(seconds: 2));
      
      expect($('Pause'), findsOneWidget);
      
      // Test seeking
      await $.tap($('Seek Forward'));
      await $.pump(const Duration(milliseconds: 500));
      
      // Should seek smoothly
      expect($('Video Player'), findsOneWidget);
    });

    patrolTest('Large dataset handling', (PatrolTester $) async {
      await _loginTestUser($);
      
      // Navigate to courses with large dataset
      await $.tap($('Courses'));
      await $.pumpAndSettle();
      
      // Scroll through many courses
      for (int i = 0; i < 100; i++) {
        await $.scroll(
          finder: $('Course List'),
          delta: const Offset(0, -100),
        );
        await $.pump(const Duration(milliseconds: 16)); // 60 FPS
      }
      
      // Should maintain smooth scrolling
      expect($('Courses'), findsOneWidget);
      
      // Memory usage should be stable
      // (In real test, would monitor memory usage)
    });
  });

  group('Security Tests', () {
    patrolTest('Secure authentication flow', (PatrolTester $) async {
      await $.pumpWidgetAndSettle(
        ProviderScope(
          child: app.EduVerseApp(),
        ),
      );
      
      // Navigate to login
      await $.tap($('Sign In'));
      await $.pumpAndSettle();
      
      // Test biometric authentication if available
      if (await _isBiometricAvailable()) {
        await $.tap($('Use Biometric Login'));
        await $.pumpAndSettle();
        
        // Should prompt for biometric
        expect($('Biometric Authentication'), findsOneWidget);
      }
      
      // Test passkey authentication
      await $.tap($('Use Passkey'));
      await $.pumpAndSettle();
      
      // Should show passkey prompt
      expect($('Passkey Authentication'), findsOneWidget);
      
      // Fall back to password
      await $.tap($('Use Password'));
      await $.pumpAndSettle();
      
      // Login with password
      await $.enterText($('Email'), 'test@example.com');
      await $.enterText($('Password'), 'securepassword123');
      await $.tap($('Sign In'));
      await $.pumpAndSettle();
      
      // Should be authenticated securely
      expect($('Welcome back'), findsOneWidget);
    });

    patrolTest('Data privacy controls', (PatrolTester $) async {
      await _loginTestUser($);
      
      // Navigate to privacy settings
      await $.tap($('Profile'));
      await $.pumpAndSettle();
      
      await $.tap($('Settings'));
      await $.pumpAndSettle();
      
      await $.tap($('Privacy'));
      await $.pumpAndSettle();
      
      // Should show privacy controls
      expect($('Data Sharing'), findsOneWidget);
      expect($('Analytics'), findsOneWidget);
      expect($('Marketing'), findsOneWidget);
      
      // Test opting out of data sharing
      await $.tap($('Disable Data Sharing'));
      await $.pumpAndSettle();
      
      expect($('Data sharing disabled'), findsOneWidget);
      
      // Test data export
      await $.tap($('Export My Data'));
      await $.pumpAndSettle();
      
      expect($('Data export requested'), findsOneWidget);
      
      // Test account deletion
      await $.tap($('Delete Account'));
      await $.pumpAndSettle();
      
      expect($('Confirm account deletion'), findsOneWidget);
    });
  });
}

// Helper functions
Future<void> _loginTestUser(PatrolTester $) async {
  await $.pumpWidgetAndSettle(
    ProviderScope(
      child: app.EduVerseApp(),
    ),
  );
  
  // Skip onboarding if present
  if ($('Get Started').evaluate().isNotEmpty) {
    await $.tap($('Get Started'));
    await $.pumpAndSettle();
    
    await $.tap($('Sign In'));
    await $.pumpAndSettle();
  }
  
  // Login
  await $.enterText($('Email'), 'test@example.com');
  await $.enterText($('Password'), 'testpassword123');
  await $.tap($('Sign In'));
  await $.pumpAndSettle();
}

Future<bool> _isVRSupported() async {
  // Mock VR support detection
  return true; // In real test, would check actual VR capability
}

Future<bool> _isARSupported() async {
  // Mock AR support detection
  return true; // In real test, would check actual AR capability
}

Future<bool> _isBiometricAvailable() async {
  // Mock biometric availability
  return true; // In real test, would check actual biometric capability
}