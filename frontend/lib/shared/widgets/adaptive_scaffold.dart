import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

class AdaptiveScaffold extends StatelessWidget {
  final Widget child;
  final String currentLocation;

  const AdaptiveScaffold({
    super.key,
    required this.child,
    required this.currentLocation,
  });

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;

    // Mobile layout with bottom navigation
    if (screenWidth < 600) {
      return Scaffold(
        body: child,
        bottomNavigationBar: _buildBottomNavigationBar(context),
      );
    }

    // Tablet layout with navigation rail
    if (screenWidth < 1200) {
      return Scaffold(
        body: Row(
          children: [
            _buildNavigationRail(context),
            Expanded(child: child),
          ],
        ),
      );
    }

    // Desktop layout with navigation drawer
    return Scaffold(
      body: Row(
        children: [
          _buildNavigationDrawer(context),
          Expanded(child: child),
        ],
      ),
    );
  }

  Widget _buildBottomNavigationBar(BuildContext context) {
    final currentIndex = _getCurrentIndex(currentLocation);

    return NavigationBar(
      selectedIndex: currentIndex,
      onDestinationSelected: (index) {
        // Simple navigation for demo
        if (index == 0) {
          Navigator.of(context).pushReplacementNamed('/home');
        } else if (index == 1) {
          Navigator.of(context).pushReplacementNamed('/courses');
        } else if (index == 2) {
          Navigator.of(context).pushReplacementNamed('/profile');
        }
      },
      destinations: const [
        NavigationDestination(
          icon: Icon(Icons.home_outlined),
          selectedIcon: Icon(Icons.home),
          label: 'Home',
        ),
        NavigationDestination(
          icon: Icon(Icons.school_outlined),
          selectedIcon: Icon(Icons.school),
          label: 'Courses',
        ),
        NavigationDestination(
          icon: Icon(Icons.person_outline),
          selectedIcon: Icon(Icons.person),
          label: 'Profile',
        ),
      ],
    );
  }

  Widget _buildNavigationRail(BuildContext context) {
    final currentIndex = _getCurrentIndex(currentLocation);

    return NavigationRail(
      selectedIndex: currentIndex,
      onDestinationSelected: (index) {
        // Simple navigation for demo
        if (index == 0) {
          Navigator.of(context).pushReplacementNamed('/home');
        } else if (index == 1) {
          Navigator.of(context).pushReplacementNamed('/courses');
        } else if (index == 2) {
          Navigator.of(context).pushReplacementNamed('/profile');
        }
      },
      labelType: NavigationRailLabelType.all,
      backgroundColor: Theme.of(context).colorScheme.surface,
      destinations: const [
        NavigationRailDestination(
          icon: Icon(Icons.home_outlined),
          selectedIcon: Icon(Icons.home),
          label: Text('Home'),
        ),
        NavigationRailDestination(
          icon: Icon(Icons.school_outlined),
          selectedIcon: Icon(Icons.school),
          label: Text('Courses'),
        ),
        NavigationRailDestination(
          icon: Icon(Icons.person_outline),
          selectedIcon: Icon(Icons.person),
          label: Text('Profile'),
        ),
      ],
      trailing: Expanded(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            IconButton(
              icon: const Icon(Icons.psychology),
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('AI Tutor coming soon!')),
                );
              },
              tooltip: 'AI Tutor',
            ),
            IconButton(
              icon: const Icon(Icons.settings),
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Settings coming soon!')),
                );
              },
              tooltip: 'Settings',
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildNavigationDrawer(BuildContext context) {
    return Container(
      width: 280,
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        border: Border(
          right: BorderSide(
            color: Theme.of(context).dividerColor,
            width: 1,
          ),
        ),
      ),
      child: Column(
        children: [
          // App header
          Container(
            height: 120,
            padding: const EdgeInsets.all(AppTheme.spacing6),
            decoration: BoxDecoration(
              gradient: AppTheme.primaryGradient,
            ),
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.school,
                    color: Colors.white,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'EduVerse',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      Text(
                        'Future of Learning',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Colors.white.withOpacity(0.8),
                            ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Navigation items
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(vertical: 8),
              children: [
                // Main navigation
                _buildDrawerItem(
                  context,
                  'Home',
                  Icons.home_outlined,
                  Icons.home,
                  '/home',
                  currentLocation == '/home',
                ),
                _buildDrawerItem(
                  context,
                  'Courses',
                  Icons.school_outlined,
                  Icons.school,
                  '/courses',
                  currentLocation == '/courses',
                ),
                _buildDrawerItem(
                  context,
                  'AI Tutor',
                  Icons.psychology_outlined,
                  Icons.psychology,
                  '/ai-tutor',
                  currentLocation == '/ai-tutor',
                ),
                _buildDrawerItem(
                  context,
                  'Profile',
                  Icons.person_outline,
                  Icons.person,
                  '/profile',
                  currentLocation == '/profile',
                ),

                const Divider(),

                // Extended navigation
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Text(
                    'More',
                    style: Theme.of(context).textTheme.labelMedium?.copyWith(
                          color: AppTheme.textSecondary,
                          fontWeight: FontWeight.w600,
                        ),
                  ),
                ),
                const SizedBox(height: 8),

                _buildDrawerItem(
                  context,
                  'VR Classroom',
                  Icons.meeting_room,
                  Icons.meeting_room,
                  '/vr-classroom',
                  false,
                ),
                _buildDrawerItem(
                  context,
                  'Live Classes',
                  Icons.video_call,
                  Icons.video_call,
                  '/live-class',
                  false,
                ),
              ],
            ),
          ),

          // User section
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              border: Border(
                top: BorderSide(
                  color: Theme.of(context).dividerColor,
                  width: 1,
                ),
              ),
            ),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 20,
                  backgroundColor: AppTheme.primaryColor,
                  child: const Text(
                    'U',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'User Name',
                        style: Theme.of(context).textTheme.titleSmall,
                      ),
                      Text(
                        'Level 5 • 2,450 XP',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: AppTheme.textSecondary,
                            ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.settings),
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Settings coming soon!')),
                    );
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDrawerItem(
    BuildContext context,
    String label,
    IconData icon,
    IconData selectedIcon,
    String path,
    bool isSelected,
  ) {
    return Container(
      margin: const EdgeInsets.symmetric(
        horizontal: 8,
        vertical: 2,
      ),
      child: ListTile(
        leading: Icon(
          isSelected ? selectedIcon : icon,
          color: isSelected ? AppTheme.primaryColor : AppTheme.textSecondary,
        ),
        title: Text(
          label,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color:
                    isSelected ? AppTheme.primaryColor : AppTheme.textPrimary,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
              ),
        ),
        selected: isSelected,
        selectedTileColor: AppTheme.primaryColor.withOpacity(0.1),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        onTap: () {
          Navigator.of(context).pushReplacementNamed(path);
        },
      ),
    );
  }

  int _getCurrentIndex(String location) {
    if (location.startsWith('/home')) {
      return 0;
    } else if (location.startsWith('/courses')) {
      return 1;
    } else if (location.startsWith('/profile')) {
      return 2;
    }
    return 0;
  }
}
