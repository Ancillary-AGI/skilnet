import 'package:flutter/material.dart';
import 'package:flutter/gestures.dart';
import '../../core/theme/responsive_utils.dart';

/// Adaptive scaffold that adjusts layout based on device type and screen size
class AdaptiveScaffold extends StatelessWidget {
  final PreferredSizeWidget? appBar;
  final Widget body;
  final Widget? floatingActionButton;
  final FloatingActionButtonLocation? floatingActionButtonLocation;
  final FloatingActionButtonAnimator? floatingActionButtonAnimator;
  final List<Widget>? persistentFooterButtons;
  final Widget? drawer;
  final Widget? endDrawer;
  final Widget? bottomNavigationBar;
  final Widget? bottomSheet;
  final Color? backgroundColor;
  final bool? resizeToAvoidBottomInset;
  final bool primary;
  final DragStartBehavior drawerDragStartBehavior;
  final bool extendBody;
  final bool extendBodyBehindAppBar;
  final Color? drawerScrimColor;
  final double? drawerEdgeDragWidth;
  final bool drawerEnableOpenDragGesture;
  final bool endDrawerEnableOpenDragGesture;
  final String? restorationId;
  final String currentLocation;

  const AdaptiveScaffold({
    super.key,
    this.appBar,
    required this.body,
    this.floatingActionButton,
    this.floatingActionButtonLocation,
    this.floatingActionButtonAnimator,
    this.persistentFooterButtons,
    this.drawer,
    this.endDrawer,
    this.bottomNavigationBar,
    this.bottomSheet,
    this.backgroundColor,
    this.resizeToAvoidBottomInset,
    this.primary = true,
    this.drawerDragStartBehavior = DragStartBehavior.start,
    this.extendBody = false,
    this.extendBodyBehindAppBar = false,
    this.drawerScrimColor,
    this.drawerEdgeDragWidth,
    this.drawerEnableOpenDragGesture = true,
    this.endDrawerEnableOpenDragGesture = true,
    this.restorationId,
    required this.currentLocation,
  });

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final deviceType = ResponsiveUtils.getDeviceType(context);
        final isLandscape =
            MediaQuery.of(context).orientation == Orientation.landscape;
        final screenSize = MediaQuery.of(context).size;

        // Adaptive layout logic
        Widget scaffoldBody = body;

        // For tablets and larger screens in landscape, use master-detail or multi-column layouts
        if ((deviceType == DeviceType.tablet ||
                deviceType == DeviceType.desktop ||
                deviceType == DeviceType.largeDesktop) &&
            isLandscape) {
          scaffoldBody = _buildLandscapeLayout(context, scaffoldBody);
        }

        // For foldables, handle hinge area
        if (ResponsiveUtils.isFoldable(context)) {
          scaffoldBody = _buildFoldableLayout(context, scaffoldBody);
        }

        // For AR/VR supported devices, add XR-specific features
        if (ResponsiveUtils.supportsARVR(context)) {
          scaffoldBody = _buildXRLayout(context, scaffoldBody);
        }

        return Scaffold(
          appBar: _buildAdaptiveAppBar(context),
          body: scaffoldBody,
          floatingActionButton: _buildAdaptiveFAB(context),
          floatingActionButtonLocation: floatingActionButtonLocation,
          floatingActionButtonAnimator: floatingActionButtonAnimator,
          persistentFooterButtons: persistentFooterButtons,
          drawer: _buildAdaptiveDrawer(context),
          endDrawer: endDrawer,
          bottomNavigationBar: _buildAdaptiveBottomNav(context),
          bottomSheet: bottomSheet,
          backgroundColor: backgroundColor,
          resizeToAvoidBottomInset: resizeToAvoidBottomInset ?? true,
          primary: primary,
          drawerDragStartBehavior: drawerDragStartBehavior,
          extendBody: extendBody,
          extendBodyBehindAppBar: extendBodyBehindAppBar,
          drawerScrimColor: drawerScrimColor,
          drawerEdgeDragWidth: drawerEdgeDragWidth,
          drawerEnableOpenDragGesture: drawerEnableOpenDragGesture,
          endDrawerEnableOpenDragGesture: endDrawerEnableOpenDragGesture,
          restorationId: restorationId,
        );
      },
    );
  }

  PreferredSizeWidget? _buildAdaptiveAppBar(BuildContext context) {
    if (appBar == null) return null;

    final deviceType = ResponsiveUtils.getDeviceType(context);
    final isLandscape =
        MediaQuery.of(context).orientation == Orientation.landscape;

    // For mobile in portrait, keep standard app bar
    if (deviceType == DeviceType.mobile && !isLandscape) {
      return appBar;
    }

    // For tablets and larger screens, enhance app bar with more actions
    if (deviceType == DeviceType.tablet ||
        deviceType == DeviceType.desktop ||
        deviceType == DeviceType.largeDesktop) {
      return _buildEnhancedAppBar(context);
    }

    return appBar;
  }

  PreferredSizeWidget _buildEnhancedAppBar(BuildContext context) {
    // For enhanced app bar, just return the original for now
    // In a full implementation, we'd create a custom app bar widget
    return appBar!;
  }

  Widget _buildAppBarActions(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Search action for larger screens
        IconButton(
          icon: const Icon(Icons.search),
          onPressed: () {
            // Implement global search
          },
        ),
        // Notifications
        IconButton(
          icon: const Icon(Icons.notifications),
          onPressed: () {
            // Navigate to notifications
          },
        ),
        // Profile menu
        PopupMenuButton<String>(
          onSelected: (value) {
            // Handle menu selection
          },
          itemBuilder: (context) => [
            const PopupMenuItem(value: 'profile', child: Text('Profile')),
            const PopupMenuItem(value: 'settings', child: Text('Settings')),
            const PopupMenuItem(value: 'logout', child: Text('Logout')),
          ],
        ),
      ],
    );
  }

  Widget _buildLandscapeLayout(BuildContext context, Widget child) {
    final deviceType = ResponsiveUtils.getDeviceType(context);

    // For tablets and desktops in landscape, use a two-column layout
    if (deviceType == DeviceType.tablet) {
      return Row(
        children: [
          // Sidebar for navigation or secondary content
          SizedBox(
            width: 280,
            child: _buildSidebar(context),
          ),
          // Main content area
          Expanded(
            child: child,
          ),
        ],
      );
    }

    // For desktops, use a more sophisticated layout
    if (deviceType == DeviceType.desktop ||
        deviceType == DeviceType.largeDesktop) {
      return Row(
        children: [
          // Navigation rail
          SizedBox(
            width: 320,
            child: _buildNavigationRail(context),
          ),
          // Main content
          Expanded(
            child: child,
          ),
          // Optional right sidebar for additional content
          if (deviceType == DeviceType.largeDesktop)
            SizedBox(
              width: 280,
              child: _buildRightSidebar(context),
            ),
        ],
      );
    }

    return child;
  }

  Widget _buildFoldableLayout(BuildContext context, Widget child) {
    // Handle foldable devices with hinge area
    final screenSize = MediaQuery.of(context).size;
    final hingeArea = screenSize.width * 0.1; // Assume 10% hinge area

    return Row(
      children: [
        // Left screen area
        SizedBox(
          width: (screenSize.width - hingeArea) / 2,
          child: child,
        ),
        // Hinge area (visual separator)
        Container(
          width: hingeArea,
          color: Theme.of(context).dividerColor.withOpacity(0.5),
        ),
        // Right screen area
        SizedBox(
          width: (screenSize.width - hingeArea) / 2,
          child: _buildFoldableSecondaryContent(context),
        ),
      ],
    );
  }

  Widget _buildXRLayout(BuildContext context, Widget child) {
    // Add XR-specific UI elements
    return Stack(
      children: [
        child,
        // XR controls overlay
        Positioned(
          top: 16,
          right: 16,
          child: _buildXRControls(context),
        ),
      ],
    );
  }

  Widget _buildSidebar(BuildContext context) {
    // Implement sidebar for tablets
    return Container(
      color: Theme.of(context).colorScheme.surface,
      child: Column(
        children: [
          // Navigation items
          ListTile(
            leading: const Icon(Icons.home),
            title: const Text('Home'),
            selected: currentLocation == '/',
            onTap: () {
              // Navigate to home
            },
          ),
          ListTile(
            leading: const Icon(Icons.book),
            title: const Text('Courses'),
            selected: currentLocation.startsWith('/courses'),
            onTap: () {
              // Navigate to courses
            },
          ),
          // Add more navigation items
        ],
      ),
    );
  }

  Widget _buildNavigationRail(BuildContext context) {
    // Implement navigation rail for desktops
    return NavigationRail(
      selectedIndex: _getSelectedIndex(),
      onDestinationSelected: (index) {
        // Handle navigation
      },
      labelType: NavigationRailLabelType.all,
      destinations: const [
        NavigationRailDestination(
          icon: Icon(Icons.home),
          label: Text('Home'),
        ),
        NavigationRailDestination(
          icon: Icon(Icons.book),
          label: Text('Courses'),
        ),
        NavigationRailDestination(
          icon: Icon(Icons.person),
          label: Text('Profile'),
        ),
        NavigationRailDestination(
          icon: Icon(Icons.settings),
          label: Text('Settings'),
        ),
      ],
    );
  }

  Widget _buildRightSidebar(BuildContext context) {
    // Implement right sidebar for large desktops
    return Container(
      color: Theme.of(context).colorScheme.surface,
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Quick Actions',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 16),
          // Quick action buttons
          ElevatedButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.add),
            label: const Text('New Course'),
          ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.upload),
            label: const Text('Upload Content'),
          ),
        ],
      ),
    );
  }

  Widget _buildFoldableSecondaryContent(BuildContext context) {
    // Content for the second screen on foldables
    return Container(
      color: Theme.of(context).colorScheme.surface,
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Text(
            'Secondary Content',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          // Add secondary content like notifications, quick actions, etc.
        ],
      ),
    );
  }

  Widget _buildXRControls(BuildContext context) {
    // XR-specific controls
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              icon: const Icon(Icons.view_in_ar),
              onPressed: () {
                // Toggle AR mode
              },
            ),
            IconButton(
              icon: const Icon(Icons.vrpano),
              onPressed: () {
                // Toggle VR mode
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget? _buildAdaptiveFAB(BuildContext context) {
    if (floatingActionButton == null) return null;

    final deviceType = ResponsiveUtils.getDeviceType(context);

    // For larger screens, make FAB larger and more prominent
    if (deviceType == DeviceType.desktop ||
        deviceType == DeviceType.largeDesktop) {
      return FloatingActionButton.extended(
        onPressed: () {
          // Handle FAB press - would need to extract from original FAB
        },
        icon: const Icon(Icons.add),
        label: const Text('Create'),
      );
    }

    return floatingActionButton;
  }

  Widget? _buildAdaptiveDrawer(BuildContext context) {
    final deviceType = ResponsiveUtils.getDeviceType(context);

    // For larger screens, don't show drawer as we have navigation rail/sidebar
    if (deviceType == DeviceType.desktop ||
        deviceType == DeviceType.largeDesktop) {
      return null;
    }

    return drawer;
  }

  Widget? _buildAdaptiveBottomNav(BuildContext context) {
    final deviceType = ResponsiveUtils.getDeviceType(context);
    final isLandscape =
        MediaQuery.of(context).orientation == Orientation.landscape;

    // For tablets and desktops in landscape, don't show bottom nav
    if ((deviceType == DeviceType.tablet ||
            deviceType == DeviceType.desktop ||
            deviceType == DeviceType.largeDesktop) &&
        isLandscape) {
      return null;
    }

    return bottomNavigationBar;
  }

  int _getSelectedIndex() {
    // Map current location to navigation index
    if (currentLocation.startsWith('/courses')) return 1;
    if (currentLocation.startsWith('/profile')) return 2;
    if (currentLocation.startsWith('/settings')) return 3;
    return 0; // Home
  }
}
