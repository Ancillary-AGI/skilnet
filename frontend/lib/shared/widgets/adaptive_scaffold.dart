import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:material_symbols_icons/symbols.dart';

import '../../core/theme/app_theme.dart';
import '../../core/router/app_router.dart';

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
        final route = mainRoutes[index];
        context.go(route.path);
      },
      destinations: mainRoutes.map((route) {
        return NavigationDestination(
          icon: Icon(route.icon),
          selectedIcon: Icon(route.selectedIcon ?? route.icon),
          label: route.label,
        );
      }).toList(),
    );
  }

  Widget _buildNavigationRail(BuildContext context) {
    final currentIndex = _getCurrentIndex(currentLocation);
    
    return NavigationRail(
      selectedIndex: currentIndex,
      onDestinationSelected: (index) {
        final route = mainRoutes[index];
        context.go(route.path);
      },
      labelType: NavigationRailLabelType.all,
      backgroundColor: Theme.of(context).colorScheme.surface,
      destinations: mainRoutes.map((route) {
        return NavigationRailDestination(
          icon: Icon(route.icon),
          selectedIcon: Icon(route.selectedIcon ?? route.icon),
          label: Text(route.label),
        );
      }).toList(),
      trailing: Expanded(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            // Quick action buttons
            IconButton(
              icon: const Icon(Symbols.view_in_ar),
              onPressed: () => _showVRQuickAccess(context),
              tooltip: 'VR Classroom',
            ),
            IconButton(
              icon: const Icon(Symbols.psychology),
              onPressed: () => context.go('/ai-tutor'),
              tooltip: 'AI Tutor',
            ),
            IconButton(
              icon: const Icon(Symbols.settings),
              onPressed: () => context.go('/profile/settings'),
              tooltip: 'Settings',
            ),
            const SizedBox(height: AppTheme.spacing4),
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
            padding: const EdgeInsets.all(AppTheme.spacing4),
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
                    borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
                  ),
                  child: const Icon(
                    Symbols.school,
                    color: Colors.white,
                    size: 24,
                  ),
                ),
                const SizedBox(width: AppTheme.spacing3),
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
              padding: const EdgeInsets.symmetric(vertical: AppTheme.spacing2),
              children: [
                // Main navigation
                ...mainRoutes.map((route) => _buildDrawerItem(
                  context,
                  route.label,
                  route.icon,
                  route.selectedIcon ?? route.icon,
                  route.path,
                  currentLocation == route.path,
                )),
                
                const Divider(height: AppTheme.spacing6),
                
                // Extended navigation
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: AppTheme.spacing4),
                  child: Text(
                    'More',
                    style: Theme.of(context).textTheme.labelMedium?.copyWith(
                      color: AppTheme.textSecondary,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                const SizedBox(height: AppTheme.spacing2),
                
                ...extendedRoutes.map((route) => _buildDrawerItem(
                  context,
                  route.label,
                  route.icon,
                  route.selectedIcon ?? route.icon,
                  route.path,
                  currentLocation == route.path,
                )),
                
                const Divider(height: AppTheme.spacing6),
                
                // Quick actions
                _buildDrawerItem(
                  context,
                  'VR Classroom',
                  Symbols.view_in_ar,
                  Symbols.view_in_ar,
                  '/vr-classroom/quick',
                  false,
                  color: FeatureColors.vrClassroom,
                ),
                _buildDrawerItem(
                  context,
                  'Live Classes',
                  Symbols.video_call,
                  Symbols.video_call,
                  '/live-class/browse',
                  false,
                  color: FeatureColors.liveClass,
                ),
              ],
            ),
          ),
          
          // User section
          Container(
            padding: const EdgeInsets.all(AppTheme.spacing4),
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
                  child: Text(
                    'U',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: AppTheme.spacing3),
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
                  icon: const Icon(Symbols.settings),
                  onPressed: () => context.go('/profile/settings'),
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
    bool isSelected, {
    Color? color,
  }) {
    return Container(
      margin: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacing2,
        vertical: AppTheme.spacing1,
      ),
      child: ListTile(
        leading: Icon(
          isSelected ? selectedIcon : icon,
          color: isSelected 
              ? (color ?? AppTheme.primaryColor)
              : AppTheme.textSecondary,
        ),
        title: Text(
          label,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: isSelected 
                ? (color ?? AppTheme.primaryColor)
                : AppTheme.textPrimary,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
          ),
        ),
        selected: isSelected,
        selectedTileColor: (color ?? AppTheme.primaryColor).withOpacity(0.1),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        ),
        onTap: () => context.go(path),
      ),
    );
  }

  int _getCurrentIndex(String location) {
    for (int i = 0; i < mainRoutes.length; i++) {
      if (location.startsWith(mainRoutes[i].path)) {
        return i;
      }
    }
    return 0;
  }

  void _showVRQuickAccess(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        padding: const EdgeInsets.all(AppTheme.spacing4),
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(
            top: Radius.circular(AppTheme.radiusLarge),
          ),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 40,
              height: 4,
              margin: const EdgeInsets.only(bottom: AppTheme.spacing4),
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            Text(
              'VR Quick Access',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: AppTheme.spacing4),
            
            ListTile(
              leading: const Icon(Symbols.meeting_room, color: FeatureColors.vrClassroom),
              title: const Text('Join Active Classroom'),
              subtitle: const Text('3 active sessions'),
              onTap: () {
                Navigator.pop(context);
                context.go('/vr-classroom/active');
              },
            ),
            
            ListTile(
              leading: const Icon(Symbols.science, color: FeatureColors.arExperience),
              title: const Text('Virtual Lab'),
              subtitle: const Text('Chemistry & Physics'),
              onTap: () {
                Navigator.pop(context);
                context.go('/vr-classroom/lab');
              },
            ),
            
            ListTile(
              leading: const Icon(Symbols.explore, color: AppTheme.accentColor),
              title: const Text('Explore Environments'),
              subtitle: const Text('Browse VR worlds'),
              onTap: () {
                Navigator.pop(context);
                context.go('/vr-classroom/explore');
              },
            ),
            
            const SizedBox(height: AppTheme.spacing4),
          ],
        ),
      ),
    );
  }
}