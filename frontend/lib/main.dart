import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'core/app_config.dart';
import 'core/router/app_router.dart';
import 'core/services/cache_service.dart';
import 'core/services/analytics_service.dart';
import 'core/services/notification_service.dart';
import 'core/services/asset_service.dart';
import 'core/theme/app_theme.dart';
import 'core/theme/responsive_utils.dart';
import 'core/providers/app_providers.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  try {
    // Initialize Hive for local storage
    await Hive.initFlutter();

    // Initialize core services with error handling
    await _initializeServices();

    // Configure system UI
    await _configureSystemUI();

    // Run the app
    runApp(
      const ProviderScope(
        child: EduVerseApp(),
      ),
    );
  } catch (error, stackTrace) {
    // Log critical startup errors
    debugPrint('Error Critical startup error: $error');
    debugPrint('Stack trace: $stackTrace');

    // Run app with error screen for debugging
    runApp(
      MaterialApp(
        home: Scaffold(
          body: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.error, size: 64, color: Colors.red),
                const SizedBox(height: 16),
                const Text(
                  'Failed to start EduVerse',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                Text(
                  'Error: $error',
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.grey),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

Future<void> _initializeServices() async {
  try {
    // Initialize core services
    await CacheService.initialize();
    await AnalyticsService.initialize();
    await NotificationService.initialize();

    // Initialize asset services (avoiding duplication)
    final assetService = AssetService();
    await assetService.initialize();
    await assetService.preloadCriticalAssets();

    debugPrint('✅ All services initialized successfully');
  } catch (e) {
    debugPrint('❌ Service initialization failed: $e');
    rethrow;
  }
}

Future<void> _configureSystemUI() async {
  try {
    // Set preferred orientations for all device types
    await SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
      DeviceOrientation.portraitDown,
      DeviceOrientation.landscapeLeft,
      DeviceOrientation.landscapeRight,
    ]);

    // Enable high refresh rate displays
    await SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);

    // Set initial system UI overlay style based on system theme
    // This will be overridden when the app builds with the actual theme
    final brightness =
        WidgetsBinding.instance.platformDispatcher.platformBrightness;
    SystemChrome.setSystemUIOverlayStyle(_getSystemUiOverlayStyle(brightness));
  } catch (e) {
    debugPrint('⚠️  System UI configuration failed: $e');
    // Continue anyway as this is not critical
  }
}

/// Returns the appropriate system UI overlay style based on theme brightness
SystemUiOverlayStyle _getSystemUiOverlayStyle(Brightness brightness) {
  return SystemUiOverlayStyle(
    // Status bar styling
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: brightness == Brightness.light
        ? Brightness.dark // Dark icons on light background
        : Brightness.light, // Light icons on dark background

    // Navigation bar styling
    systemNavigationBarColor: Colors.transparent,
    systemNavigationBarIconBrightness: brightness == Brightness.light
        ? Brightness.dark // Dark icons on light background
        : Brightness.light, // Light icons on dark background

    // Additional properties for better integration
    systemNavigationBarDividerColor: Colors.transparent,
  );
}

/// Updates system UI overlay style based on current theme
void _updateSystemUiOverlayStyle(BuildContext context) {
  final brightness = Theme.of(context).brightness;
  SystemChrome.setSystemUIOverlayStyle(_getSystemUiOverlayStyle(brightness));
}

class EduVerseApp extends ConsumerStatefulWidget {
  const EduVerseApp({super.key});

  @override
  ConsumerState<EduVerseApp> createState() => _EduVerseAppState();
}

class _EduVerseAppState extends ConsumerState<EduVerseApp>
    with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    // Cleanup services on app disposal
    _cleanupServices();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    super.didChangeAppLifecycleState(state);

    switch (state) {
      case AppLifecycleState.paused:
        // App is in background
        debugPrint('App paused - saving state');
        break;
      case AppLifecycleState.resumed:
        // App is in foreground
        debugPrint('App resumed');
        break;
      case AppLifecycleState.inactive:
        // App is inactive
        debugPrint('App inactive');
        break;
      case AppLifecycleState.detached:
        // App is terminating
        debugPrint('App detached - final cleanup');
        _cleanupServices();
        break;
      case AppLifecycleState.hidden:
        // App is hidden (iOS specific)
        debugPrint('App hidden');
        break;
    }
  }

  Future<void> _cleanupServices() async {
    try {
      // Dispose cache service
      await CacheService.dispose();

      // Dispose other services if they have dispose methods
      debugPrint('✅ Services cleaned up');
    } catch (e) {
      debugPrint('⚠️  Error during service cleanup: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final router = ref.watch(appRouterProvider);
    final themeMode = ref.watch(themeProvider);

    // Update system UI overlay style based on current theme
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _updateSystemUiOverlayStyle(context);
    });

    return MaterialApp.router(
      title: AppConfig.appName,
      debugShowCheckedModeBanner: AppConfig.debugMode,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeMode,

      // Router configuration
      routerConfig: router,

      // Localization
      supportedLocales: AppConfig.supportedLocales,
      locale: ref.watch(localeProvider),

      // Enhanced builder for responsive design, accessibility, and performance
      builder: (context, child) {
        final mediaQuery = MediaQuery.of(context);

        // Enhanced text scaling with better accessibility
        final textScaler = mediaQuery.textScaler.clamp(
          minScaleFactor: 0.8,
          maxScaleFactor: 1.4, // Increased for better accessibility
        );

        // Apply responsive padding and safe areas
        final safeAreaInsets = ResponsiveUtils.getSafeAreaInsets(context);

        final enhancedChild = MediaQuery(
          data: mediaQuery.copyWith(
            textScaler: textScaler,
            padding: mediaQuery.padding.copyWith(
              left: mediaQuery.padding.left + safeAreaInsets.left,
              top: mediaQuery.padding.top + safeAreaInsets.top,
              right: mediaQuery.padding.right + safeAreaInsets.right,
              bottom: mediaQuery.padding.bottom + safeAreaInsets.bottom,
            ),
          ),
          child: child ?? const SizedBox.shrink(),
        );

        // Add performance optimizations
        return DefaultTextHeightBehavior(
          textHeightBehavior: const TextHeightBehavior(
            leadingDistribution: TextLeadingDistribution.even,
          ),
          child: enhancedChild,
        );
      },
    );
  }
}
