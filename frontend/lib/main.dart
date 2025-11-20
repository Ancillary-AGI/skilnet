import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'core/app_config.dart';
import 'core/router/app_router.dart';
import 'core/services/cache_service.dart';
import 'core/services/analytics_service.dart';
import 'core/services/notification_service.dart';
import 'core/services/asset_cache_service.dart';
import 'core/services/asset_service.dart';
import 'core/theme/app_theme.dart';
import 'core/theme/responsive_utils.dart';
import 'core/providers/app_providers.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Hive for local storage
  await Hive.initFlutter();

  // Initialize core services
  await CacheService.initialize();
  await AnalyticsService.initialize();
  await NotificationService.initialize();

  // Initialize new polished services
  await AssetCacheService.instance.initialize();
  await AssetCacheService.instance.preloadCriticalAssets();

  // Initialize asset discovery service
  await AssetService().initialize();
  await AssetService().preloadCriticalAssets();

  // Set preferred orientations for all device types
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
    DeviceOrientation.landscapeLeft,
    DeviceOrientation.landscapeRight,
  ]);

  // Enhanced system UI overlay style with responsive considerations
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
      systemNavigationBarColor: Colors.transparent,
      systemNavigationBarIconBrightness: Brightness.dark,
    ),
  );

  // Enable high refresh rate displays
  await SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);

  // API service is now auto-initialized

  runApp(
    const ProviderScope(
      child: EduVerseApp(),
    ),
  );
}

class EduVerseApp extends ConsumerWidget {
  const EduVerseApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);
    final themeMode = ref.watch(themeProvider);

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
