#!/usr/bin/env dart
/*
Test runner for EduVerse frontend tests
*/

import 'dart:io';

void main(List<String> args) async {
  print('🎓 EduVerse Frontend Test Suite');
  print('=' * 50);

  bool allPassed = true;

  // Run unit tests
  print('🧪 Running unit tests...');
  final unitTestResult = await runTests(['test/simple_test.dart']);
  allPassed &= unitTestResult;

  // Run widget tests
  print('\n🎨 Running widget tests...');
  final widgetTestResult = await runTests(['test/widget_test.dart']);
  allPassed &= widgetTestResult;

  // Run integration tests (optional)
  print('\n🔗 Integration tests available');
  print('Run with: flutter test integration_test/');

  print('\n' + '=' * 50);

  if (allPassed) {
    print('✅ All tests passed!');
    exit(0);
  } else {
    print('❌ Some tests failed!');
    exit(1);
  }
}

Future<bool> runTests(List<String> testFiles) async {
  try {
    for (final testFile in testFiles) {
      print('  Running $testFile...');
      final result = await Process.run('flutter', ['test', testFile]);
      
      if (result.exitCode == 0) {
        print('  ✅ $testFile passed');
      } else {
        print('  ❌ $testFile failed');
        print('  Output: ${result.stdout}');
        print('  Error: ${result.stderr}');
        return false;
      }
    }
    return true;
  } catch (e) {
    print('  ❌ Error running tests: $e');
    return false;
  }
}