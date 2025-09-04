import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/auth/providers/auth_provider.dart';
import '../../features/auth/screens/login_screen.dart';
import '../../features/auth/screens/register_screen.dart';
import '../../features/auth/screens/forgot_password_screen.dart';
import '../../features/onboarding/screens/onboarding_screen.dart';
import '../../features/home/screens/home_screen.dart';
import '../../features/courses/screens/course_catalog_screen.dart';
import '../../features/courses/screens/course_detail_screen.dart';
import '../../features/courses/screens/lesson_screen.dart';
import '../../features/vr_classroom/screens/vr_classroom_screen.dart';
import '../../features/ar_experience/screens/ar_experience_screen.dart';
import '../../features/ai_tutor/screens/ai_tutor_screen.dart';
import '../../features/live_classes/screens/live_class_screen.dart';
import '../../features/profile/screens/profile_screen.dart';
import '../../features/profile/screens/settings_screen.dart';
import '../../features/dashboard/screens/dashboard_screen.dart';
import '../../features/achievements/screens/achievements_screen.dart';
import '../../features/social/screens/discussion_screen.dart';
import '../../shared/widgets/adaptive_scaffold.dart';
import '../../shared/widgets/error_screen.dart';
import '../../shared/widgets/loading_screen.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);
  
  return GoRouter(
    initialLocation: '/onboarding',
    debugLogDiagnostics: true,
    
    redirect: (context, state) {
      final isLoggedIn = authState.isAuthenticated;
      final isOnboarding = state.location == '/onboarding';
      final isAuth = state.location.startsWith('/auth');
      
      // If not logged in and not on auth/onboarding pages, redirect to onboarding
      if (!isLoggedIn && !isAuth && !isOnboarding) {
        return '/onboarding';
      }
      
      // If logged in and on auth/onboarding pages, redirect to home
      if (isLoggedIn && (isAuth || isOnboarding)) {
        return '/home';
      }
      
      return null;
    },
    
    routes: [
      // Onboarding
      GoRoute(
        path: '/onboarding',
        name: 'onboarding',
        builder: (context, state) => const OnboardingScreen(),
      ),
      
      // Authentication routes
      GoRoute(
        path: '/auth/login',
        name: 'login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/auth/register',
        name: 'register',
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: '/auth/forgot-password',
        name: 'forgot-password',
        builder: (context, state) => const ForgotPasswordScreen(),
      ),
      
      // Main app shell with bottom navigation
      ShellRoute(
        builder: (context, state, child) {
          return AdaptiveScaffold(
            currentLocation: state.location,
            child: child,
          );
        },
        routes: [
          // Home
          GoRoute(
            path: '/home',
            name: 'home',
            builder: (context, state) => const HomeScreen(),
          ),
          
          // Dashboard
          GoRoute(
            path: '/dashboard',
            name: 'dashboard',
            builder: (context, state) => const DashboardScreen(),
          ),
          
          // Course catalog
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
                  return CourseDetailScreen(courseId: courseId);
                },
                routes: [
                  GoRoute(
                    path: '/lesson/:lessonId',
                    name: 'lesson',
                    builder: (context, state) {
                      final courseId = state.pathParameters['courseId']!;
                      final lessonId = state.pathParameters['lessonId']!;
                      return LessonScreen(
                        courseId: courseId,
                        lessonId: lessonId,
                      );
                    },
                  ),
                ],
              ),
            ],
          ),
          
          // Profile
          GoRoute(
            path: '/profile',
            name: 'profile',
            builder: (context, state) => const ProfileScreen(),
            routes: [
              GoRoute(
                path: '/settings',
                name: 'settings',
                builder: (context, state) => const SettingsScreen(),
              ),
              GoRoute(
                path: '/achievements',
                name: 'achievements',
                builder: (context, state) => const AchievementsScreen(),
              ),
            ],
          ),
        ],
      ),
      
      // VR Classroom (full-screen)
      GoRoute(
        path: '/vr-classroom/:roomId',
        name: 'vr-classroom',
        builder: (context, state) {
          final roomId = state.pathParameters['roomId']!;
          return VRClassroomScreen(roomId: roomId);
        },
      ),
      
      // AR Experience (full-screen)
      GoRoute(
        path: '/ar-experience/:experienceId',
        name: 'ar-experience',
        builder: (context, state) {
          final experienceId = state.pathParameters['experienceId']!;
          return ARExperienceScreen(experienceId: experienceId);
        },
      ),
      
      // AI Tutor
      GoRoute(
        path: '/ai-tutor',
        name: 'ai-tutor',
        builder: (context, state) => const AITutorScreen(),
      ),
      
      // Live Classes
      GoRoute(
        path: '/live-class/:classId',
        name: 'live-class',
        builder: (context, state) {
          final classId = state.pathParameters['classId']!;
          return LiveClassScreen(classId: classId);
        },
      ),
      
      // Discussion Forums
      GoRoute(
        path: '/discussions',
        name: 'discussions',
        builder: (context, state) => const DiscussionScreen(),
      ),
    ],
    
    errorBuilder: (context, state) => ErrorScreen(
      error: state.error.toString(),
      onRetry: () => context.go('/home'),
    ),
  );
});

// Navigation helper
class AppNavigation {
  static void goToHome(BuildContext context) {
    context.go('/home');
  }
  
  static void goToCourse(BuildContext context, String courseId) {
    context.go('/courses/$courseId');
  }
  
  static void goToLesson(BuildContext context, String courseId, String lessonId) {
    context.go('/courses/$courseId/lesson/$lessonId');
  }
  
  static void goToVRClassroom(BuildContext context, String roomId) {
    context.go('/vr-classroom/$roomId');
  }
  
  static void goToARExperience(BuildContext context, String experienceId) {
    context.go('/ar-experience/$experienceId');
  }
  
  static void goToAITutor(BuildContext context) {
    context.go('/ai-tutor');
  }
  
  static void goToLiveClass(BuildContext context, String classId) {
    context.go('/live-class/$classId');
  }
  
  static void goToProfile(BuildContext context) {
    context.go('/profile');
  }
  
  static void goToSettings(BuildContext context) {
    context.go('/profile/settings');
  }
  
  static void goToLogin(BuildContext context) {
    context.go('/auth/login');
  }
  
  static void goToRegister(BuildContext context) {
    context.go('/auth/register');
  }
}

// Route information for adaptive navigation
class RouteInfo {
  final String path;
  final String label;
  final IconData icon;
  final IconData? selectedIcon;
  final bool showInBottomNav;
  final bool showInRail;
  final bool showInDrawer;
  
  const RouteInfo({
    required this.path,
    required this.label,
    required this.icon,
    this.selectedIcon,
    this.showInBottomNav = true,
    this.showInRail = true,
    this.showInDrawer = true,
  });
}

// Main navigation routes
const List<RouteInfo> mainRoutes = [
  RouteInfo(
    path: '/home',
    label: 'Home',
    icon: Icons.home_outlined,
    selectedIcon: Icons.home,
  ),
  RouteInfo(
    path: '/dashboard',
    label: 'Dashboard',
    icon: Icons.dashboard_outlined,
    selectedIcon: Icons.dashboard,
  ),
  RouteInfo(
    path: '/courses',
    label: 'Courses',
    icon: Icons.school_outlined,
    selectedIcon: Icons.school,
  ),
  RouteInfo(
    path: '/ai-tutor',
    label: 'AI Tutor',
    icon: Icons.psychology_outlined,
    selectedIcon: Icons.psychology,
  ),
  RouteInfo(
    path: '/profile',
    label: 'Profile',
    icon: Icons.person_outline,
    selectedIcon: Icons.person,
  ),
];

// Extended navigation routes (for rail and drawer)
const List<RouteInfo> extendedRoutes = [
  RouteInfo(
    path: '/discussions',
    label: 'Discussions',
    icon: Icons.forum_outlined,
    selectedIcon: Icons.forum,
    showInBottomNav: false,
  ),
  RouteInfo(
    path: '/profile/achievements',
    label: 'Achievements',
    icon: Icons.emoji_events_outlined,
    selectedIcon: Icons.emoji_events,
    showInBottomNav: false,
  ),
];