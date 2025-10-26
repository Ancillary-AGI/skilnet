import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/app_config.dart';
import '../../../shared/widgets/adaptive_scaffold.dart';

// Responsive value extension for BuildContext
extension ResponsiveExtension on BuildContext {
  T responsiveValue<T>({required T mobile, T? tablet, T? desktop}) {
    final width = MediaQuery.of(this).size.width;

    if (width >= AppConfig.desktopBreakpoint) {
      return desktop ?? tablet ?? mobile;
    } else if (width >= AppConfig.tabletBreakpoint) {
      return tablet ?? mobile;
    } else {
      return mobile;
    }
  }
}

class VRClassroomScreen extends ConsumerStatefulWidget {
  final String roomId;

  const VRClassroomScreen({
    super.key,
    required this.roomId,
  });

  @override
  ConsumerState<VRClassroomScreen> createState() => _VRClassroomScreenState();
}

class _VRClassroomScreenState extends ConsumerState<VRClassroomScreen>
    with TickerProviderStateMixin {
  late AnimationController _fadeController;
  late AnimationController _scaleController;
  late Animation<double> _fadeAnimation;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();

    _fadeController = AnimationController(
      duration: AppTheme.normalAnimation,
      vsync: this,
    );

    _scaleController = AnimationController(
      duration: AppTheme.slowAnimation,
      vsync: this,
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _fadeController, curve: AppTheme.defaultCurve),
    );

    _scaleAnimation = Tween<double>(begin: 0.8, end: 1.0).animate(
      CurvedAnimation(parent: _scaleController, curve: AppTheme.bounceCurve),
    );

    // Start animations
    _fadeController.forward();
    _scaleController.forward();
  }

  @override
  void dispose() {
    _fadeController.dispose();
    _scaleController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AdaptiveScaffold(
      currentLocation: '/vr-classroom/${widget.roomId}',
      child: FadeTransition(
        opacity: _fadeAnimation,
        child: ScaleTransition(
          scale: _scaleAnimation,
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(AppTheme.spacing4),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // VR Classroom Header
                _buildVRHeader(),

                const SizedBox(height: AppTheme.spacing6),

                // VR Controls
                _buildVRControls(),

                const SizedBox(height: AppTheme.spacing6),

                // 3D Environment Preview
                _buildEnvironmentPreview(),

                const SizedBox(height: AppTheme.spacing6),

                // Participants Panel
                _buildParticipantsPanel(),

                const SizedBox(height: AppTheme.spacing6),

                // Interactive Objects
                _buildInteractiveObjects(),

                const SizedBox(height: AppTheme.spacing6),

                // VR Settings
                _buildVRSettings(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildVRHeader() {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacing6),
      decoration: BoxDecoration(
        gradient: AppTheme.heroGradient,
        borderRadius: BorderRadius.circular(AppTheme.radiusXxl),
        boxShadow: AppTheme.elevatedShadow,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(AppTheme.spacing3),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
                ),
                child: const Icon(
                  Icons.meeting_room,
                  color: Colors.white,
                  size: 32,
                ),
              ),
              const SizedBox(width: AppTheme.spacing4),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Virtual Reality Classroom',
                      style:
                          Theme.of(context).textTheme.headlineMedium?.copyWith(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                              ),
                    ),
                    const SizedBox(height: AppTheme.spacing1),
                    Text(
                      'Room ID: ${widget.roomId}',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            color: Colors.white.withOpacity(0.8),
                          ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: AppTheme.spacing3,
                  vertical: AppTheme.spacing2,
                ),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 8,
                      height: 8,
                      decoration: const BoxDecoration(
                        color: Colors.green,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: AppTheme.spacing2),
                    Text(
                      'LIVE',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.green,
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: AppTheme.spacing6),

          // VR Stats
          Row(
            children: [
              _buildVRStat('Participants', '12', Icons.people),
              const SizedBox(width: AppTheme.spacing6),
              _buildVRStat('Duration', '45m', Icons.access_time),
              const SizedBox(width: AppTheme.spacing6),
              _buildVRStat('Environment', 'Lab', Icons.science),
            ],
          ),
        ],
      ),
    ).animate().shimmer(duration: 2000.ms);
  }

  Widget _buildVRStat(String label, String value, IconData icon) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(AppTheme.spacing3),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.1),
          borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
        ),
        child: Column(
          children: [
            Icon(icon, color: Colors.white, size: 20),
            const SizedBox(height: AppTheme.spacing2),
            Text(
              value,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
            ),
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.white.withOpacity(0.8),
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVRControls() {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacing5),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(AppTheme.radiusXxl),
        boxShadow: AppTheme.cardShadow,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'VR Controls',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: AppTheme.spacing4),

          // Control Grid
          GridView.count(
            crossAxisCount: context.responsiveValue(
              mobile: 2,
              tablet: 3,
              desktop: 4,
            ),
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisSpacing: AppTheme.spacing4,
            mainAxisSpacing: AppTheme.spacing4,
            children: [
              _buildControlButton(
                'Movement',
                Icons.directions_walk,
                'WASD Keys',
                Colors.blue,
              ),
              _buildControlButton(
                'Interact',
                Icons.touch_app,
                'E Key',
                Colors.green,
              ),
              _buildControlButton(
                'Voice',
                Icons.mic,
                'V Key',
                Colors.purple,
              ),
              _buildControlButton(
                'Menu',
                Icons.menu,
                'Tab Key',
                Colors.orange,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildControlButton(
      String title, IconData icon, String shortcut, Color color) {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacing4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: color, size: 32),
          const SizedBox(height: AppTheme.spacing2),
          Text(
            title,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: color,
                  fontWeight: FontWeight.bold,
                ),
          ),
          Text(
            shortcut,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppTheme.textSecondary,
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildEnvironmentPreview() {
    return Container(
      height: 200,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.blue.shade100, Colors.purple.shade100],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(AppTheme.radiusXxl),
      ),
      child: Stack(
        children: [
          // 3D Grid Background
          Positioned.fill(
            child: CustomPaint(
              painter: VRGridPainter(),
            ),
          ),

          // VR Objects
          Positioned(
            left: 50,
            top: 50,
            child: _buildVRObject('Molecule', Icons.science, Colors.blue),
          ),
          Positioned(
            right: 80,
            top: 80,
            child: _buildVRObject(
                'Atom', Icons.radio_button_unchecked, Colors.green),
          ),
          Positioned(
            bottom: 40,
            left: 100,
            child:
                _buildVRObject('Lab Equipment', Icons.biotech, Colors.purple),
          ),

          // VR Camera Indicator
          Positioned(
            top: 16,
            right: 16,
            child: Container(
              padding: const EdgeInsets.all(AppTheme.spacing2),
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.5),
                borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
              ),
              child: Row(
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      color: Colors.red,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: AppTheme.spacing2),
                  Text(
                    'VR CAM',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVRObject(String name, IconData icon, Color color) {
    return Container(
      width: 60,
      height: 60,
      decoration: BoxDecoration(
        color: color.withOpacity(0.8),
        borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.3),
            blurRadius: 8,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: Colors.white, size: 24),
          const SizedBox(height: 2),
          Text(
            name,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
          ),
        ],
      ),
    ).animate().scale(duration: 2000.ms, curve: Curves.easeInOut);
  }

  Widget _buildParticipantsPanel() {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacing5),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(AppTheme.radiusXxl),
        boxShadow: AppTheme.cardShadow,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Participants (12)',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              ElevatedButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.person_add),
                label: const Text('Invite'),
                style: ElevatedButton.styleFrom(
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: AppTheme.spacing4),

          // Participants Grid
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: context.responsiveValue(
                mobile: 3,
                tablet: 4,
                desktop: 6,
              ),
              crossAxisSpacing: AppTheme.spacing3,
              mainAxisSpacing: AppTheme.spacing3,
            ),
            itemCount: 12,
            itemBuilder: (context, index) {
              return _buildParticipantAvatar(index);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildParticipantAvatar(int index) {
    final isOnline = index < 8;
    final isSpeaking = index == 2; // Simulate current speaker

    return Container(
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(
          color: isSpeaking ? Colors.green : Colors.transparent,
          width: 3,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            spreadRadius: 2,
          ),
        ],
      ),
      child: CircleAvatar(
        radius: 24,
        backgroundColor: isOnline ? Colors.blue : Colors.grey,
        child: Text(
          'U${index + 1}',
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 12,
          ),
        ),
      ),
    );
  }

  Widget _buildInteractiveObjects() {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacing5),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(AppTheme.radiusXxl),
        boxShadow: AppTheme.cardShadow,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Interactive Objects',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: AppTheme.spacing4),
          Wrap(
            spacing: AppTheme.spacing3,
            runSpacing: AppTheme.spacing3,
            children: [
              _buildInteractiveObject(
                  'Periodic Table', Icons.table_chart, Colors.blue),
              _buildInteractiveObject(
                  '3D Models', Icons.view_in_ar, Colors.green),
              _buildInteractiveObject('Whiteboard', Icons.draw, Colors.purple),
              _buildInteractiveObject(
                  'Quiz Station', Icons.quiz, Colors.orange),
              _buildInteractiveObject(
                  'Experiment Lab', Icons.science, Colors.teal),
              _buildInteractiveObject(
                  'Discussion Area', Icons.forum, Colors.pink),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildInteractiveObject(String name, IconData icon, Color color) {
    return Container(
      width: 120,
      padding: const EdgeInsets.all(AppTheme.spacing3),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 32),
          const SizedBox(height: AppTheme.spacing2),
          Text(
            name,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: color,
                  fontWeight: FontWeight.bold,
                ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildVRSettings() {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacing5),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(AppTheme.radiusXxl),
        boxShadow: AppTheme.cardShadow,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'VR Settings',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: AppTheme.spacing4),

          // Settings Options
          _buildSettingOption(
            'Movement Speed',
            'Normal',
            Icons.speed,
            onTap: () {},
          ),
          _buildSettingOption(
            'Audio Quality',
            'High',
            Icons.audio_file,
            onTap: () {},
          ),
          _buildSettingOption(
            'Graphics Quality',
            'Ultra',
            Icons.high_quality,
            onTap: () {},
          ),
          _buildSettingOption(
            'Comfort Mode',
            'Enabled',
            Icons.accessibility,
            onTap: () {},
          ),
        ],
      ),
    );
  }

  Widget _buildSettingOption(String title, String value, IconData icon,
      {VoidCallback? onTap}) {
    return ListTile(
      leading: Icon(icon, color: AppTheme.primaryColor),
      title: Text(title),
      subtitle: Text(value),
      trailing: const Icon(Icons.arrow_forward_ios, size: 16),
      onTap: onTap,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
      ),
    );
  }
}

// VR Grid Background Painter
class VRGridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.1)
      ..strokeWidth = 1;

    const gridSize = 20.0;

    // Draw vertical lines
    for (double x = 0; x <= size.width; x += gridSize) {
      canvas.drawLine(
        Offset(x, 0),
        Offset(x, size.height),
        paint,
      );
    }

    // Draw horizontal lines
    for (double y = 0; y <= size.height; y += gridSize) {
      canvas.drawLine(
        Offset(0, y),
        Offset(size.width, y),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => false;
}

// Feature Colors for different VR features
class FeatureColors {
  static const Color vrClassroom = Color(0xFF6366F1);
  static const Color arExperience = Color(0xFF10B981);
  static const Color liveClass = Color(0xFFF59E0B);
  static const Color aiTutor = Color(0xFF8B5CF6);
  static const Color socialLearning = Color(0xFFEC4899);
  static const Color analytics = Color(0xFF06B6D4);
}
