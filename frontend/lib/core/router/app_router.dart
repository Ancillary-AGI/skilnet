import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:eduverse/features/auth/screens/login_screen.dart';
import 'package:eduverse/features/auth/screens/register_screen.dart';
import 'package:eduverse/features/home/screens/home_screen.dart';
import 'package:eduverse/features/onboarding/screens/onboarding_screen.dart';
import 'package:eduverse/features/dashboard/screens/dashboard_screen.dart';
import 'package:eduverse/features/courses/screens/course_catalog_screen.dart';
import 'package:eduverse/features/ai_tutor/screens/ai_tutor_screen.dart';
import 'package:eduverse/features/vr_classroom/screens/vr_classroom_screen.dart';
import 'package:eduverse/features/profile/screens/profile_screen.dart';
import 'package:eduverse/features/settings/screens/settings_screen.dart';
import 'package:eduverse/core/services/cache_service.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: _getInitialRoute(),
    routes: [
      GoRoute(
        path: '/onboarding',
        name: 'onboarding',
        builder: (context, state) => const OnboardingScreen(),
      ),
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/register',
        name: 'register',
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: '/home',
        name: 'home',
        builder: (context, state) => const HomeScreen(),
      ),
      GoRoute(
        path: '/dashboard',
        name: 'dashboard',
        builder: (context, state) => const DashboardScreen(),
      ),
      GoRoute(
        path: '/courses',
        name: 'courses',
        builder: (context, state) => const CourseCatalogScreen(),
        routes: [
          GoRoute(
            path: '/:courseId',
            name: 'course-detail',
            builder: (context, state) {
              final courseId = state.pathParameters['courseId']!;
              return CourseDetailPage(courseId: courseId);
            },
          ),
        ],
      ),
      GoRoute(
        path: '/profile',
        name: 'profile',
        builder: (context, state) => const ProfileScreen(),
      ),
      GoRoute(
        path: '/settings',
        name: 'settings',
        builder: (context, state) => const SettingsScreen(),
      ),
      GoRoute(
        path: '/ai-tutor',
        name: 'ai-tutor',
        builder: (context, state) => const AITutorScreen(),
      ),
      GoRoute(
        path: '/vr-classroom',
        name: 'vr-classroom',
        builder: (context, state) =>
            const VRClassroomScreen(roomId: 'default-room'),
      ),
      // Additional routes
      GoRoute(
        path: '/search',
        name: 'search',
        builder: (context, state) => const SearchPage(),
      ),
      GoRoute(
        path: '/notifications',
        name: 'notifications',
        builder: (context, state) => const NotificationsPage(),
      ),
      GoRoute(
        path: '/achievements',
        name: 'achievements',
        builder: (context, state) => const AchievementsPage(),
      ),
    ],
    redirect: (context, state) {
      try {
        final isLoggedIn = CacheService.isLoggedIn;
        final isOnboarding =
            CacheService.getSetting('onboarding_completed') ?? false;

        // If not onboarded, go to onboarding
        if (!isOnboarding && state.matchedLocation != '/onboarding') {
          return '/onboarding';
        }

        // If not logged in and trying to access protected routes
        final protectedRoutes = ['/dashboard', '/profile', '/courses'];
        if (!isLoggedIn &&
            protectedRoutes
                .any((route) => state.matchedLocation.startsWith(route))) {
          return '/login';
        }

        return null; // No redirect needed
      } catch (e) {
        // Fallback for tests or when cache is not initialized
        return null;
      }
    },
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text(
              'Page not found',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              state.error.toString(),
              style: Theme.of(context).textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => context.go('/home'),
              child: const Text('Go Home'),
            ),
          ],
        ),
      ),
    ),
  );
});

String _getInitialRoute() {
  try {
    final isOnboarded =
        CacheService.getSetting('onboarding_completed') ?? false;
    final isLoggedIn = CacheService.isLoggedIn;

    if (!isOnboarded) return '/onboarding';
    if (!isLoggedIn) return '/home';
    return '/dashboard';
  } catch (e) {
    // Fallback for tests or when cache is not initialized
    return '/onboarding';
  }
}

// Placeholder pages for additional routes
class CourseDetailPage extends StatelessWidget {
  final String courseId;

  const CourseDetailPage({super.key, required this.courseId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Course $courseId')),
      body: Center(
        child: Text('Course Detail Page - ID: $courseId'),
      ),
    );
  }
}

class SearchPage extends StatelessWidget {
  const SearchPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Search')),
      body: const Center(
        child: Text('Search Page - Coming Soon'),
      ),
    );
  }
}

class NotificationsPage extends StatelessWidget {
  const NotificationsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Notifications')),
      body: const Center(
        child: Text('Notifications Page - Coming Soon'),
      ),
    );
  }
}

class AchievementsPage extends StatelessWidget {
  const AchievementsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Achievements')),
      body: const Center(
        child: Text('Achievements Page - Coming Soon'),
      ),
    );
  }
}
