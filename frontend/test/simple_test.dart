import 'package:flutter_test/flutter_test.dart';

void main() {
  group('EduVerse Simple Tests', () {
    test('Basic arithmetic test', () {
      expect(2 + 2, equals(4));
    });

    test('String manipulation test', () {
      const appName = 'EduVerse';
      expect(appName.length, equals(8));
      expect(appName.toLowerCase(), equals('eduverse'));
    });

    test('List operations test', () {
      final features = ['VR', 'AR', 'AI', 'Social Learning'];
      expect(features.length, equals(4));
      expect(features.contains('VR'), isTrue);
      expect(features.contains('Blockchain'), isFalse);
    });

    test('Map operations test', () {
      final config = {
        'appName': 'EduVerse',
        'version': '2.0.0',
        'debugMode': true,
      };
      
      expect(config['appName'], equals('EduVerse'));
      expect(config['version'], equals('2.0.0'));
      expect(config['debugMode'], isTrue);
    });
  });
}