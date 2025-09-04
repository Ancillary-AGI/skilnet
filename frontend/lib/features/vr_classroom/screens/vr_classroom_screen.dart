import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:material_symbols_icons/symbols.dart';

import '../../../core/theme/app_theme.dart';
import '../../../shared/widgets/adaptive_card.dart';
import '../../../shared/widgets/immersive_controls.dart';
import '../../../shared/widgets/spatial_audio_controls.dart';
import '../../../shared/widgets/vr_hand_tracking.dart';
import '../providers/vr_classroom_provider.dart';
import '../widgets/vr_environment_selector.dart';
import '../widgets/vr_participant_list.dart';
import '../widgets/vr_whiteboard.dart';
import '../widgets/vr_3d_models.dart';

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
  late AnimationController _immersionController;
  late Animation<double> _immersionAnimation;
  
  bool _isImmersiveMode = false;
  bool _isHandTrackingEnabled = true;
  bool _isSpatialAudioEnabled = true;
  bool _isHapticsEnabled = true;
  
  String _selectedEnvironment = 'modern_classroom';
  double _comfortLevel = 0.8;

  @override
  void initState() {
    super.initState();
    _immersionController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    
    _immersionAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _immersionController,
      curve: Curves.easeInOutCubic,
    ));
    
    // Initialize VR session
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(vrClassroomProvider.notifier).joinRoom(widget.roomId);
    });
  }

  @override
  void dispose() {
    _immersionController.dispose();
    ref.read(vrClassroomProvider.notifier).leaveRoom();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final vrState = ref.watch(vrClassroomProvider);
    
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // Main VR view
          _buildVRView(context, vrState),
          
          // UI overlay
          if (!_isImmersiveMode) _buildUIOverlay(context, vrState),
          
          // Immersive controls (always visible)
          _buildImmersiveControls(context),
          
          // Hand tracking visualization
          if (_isHandTrackingEnabled) _buildHandTrackingOverlay(context),
          
          // Loading overlay
          if (vrState.isLoading) _buildLoadingOverlay(context),
        ],
      ),
    );
  }

  Widget _buildVRView(BuildContext context, VRClassroomState vrState) {
    return Container(
      width: double.infinity,
      height: double.infinity,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            const Color(0xFF1a1a2e),
            const Color(0xFF16213e),
            const Color(0xFF0f3460),
          ],
        ),
      ),
      child: Stack(
        children: [
          // 3D Environment simulation
          _build3DEnvironment(context),
          
          // Participants avatars
          _buildParticipantAvatars(context, vrState.participants),
          
          // Interactive objects
          _buildInteractiveObjects(context),
          
          // Spatial UI elements
          _buildSpatialUI(context),
        ],
      ),
    );
  }

  Widget _build3DEnvironment(BuildContext context) {
    return AnimatedContainer(
      duration: AppTheme.animationMedium,
      width: double.infinity,
      height: double.infinity,
      child: Stack(
        children: [
          // Environment background
          Container(
            decoration: BoxDecoration(
              image: DecorationImage(
                image: NetworkImage(_getEnvironmentImage(_selectedEnvironment)),
                fit: BoxFit.cover,
                colorFilter: ColorFilter.mode(
                  Colors.blue.withOpacity(0.1),
                  BlendMode.overlay,
                ),
              ),
            ),
          ),
          
          // 3D grid overlay for depth perception
          CustomPaint(
            size: Size.infinite,
            painter: VRGridPainter(),
          ),
          
          // Floating particles for immersion
          ...List.generate(20, (index) => _buildFloatingParticle(index)),
        ],
      ),
    );
  }

  Widget _buildFloatingParticle(int index) {
    return Positioned(
      left: (index * 50.0) % MediaQuery.of(context).size.width,
      top: (index * 30.0) % MediaQuery.of(context).size.height,
      child: Container(
        width: 4,
        height: 4,
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.3),
          shape: BoxShape.circle,
        ),
      ).animate(onPlay: (controller) => controller.repeat())
        .fadeIn(duration: 2000.ms)
        .fadeOut(delay: 1000.ms, duration: 1000.ms),
    );
  }

  Widget _buildParticipantAvatars(BuildContext context, List<dynamic> participants) {
    return Stack(
      children: participants.asMap().entries.map((entry) {
        final index = entry.key;
        final participant = entry.value;
        
        // Position avatars in a circle around the room
        final angle = (index * 2 * 3.14159) / participants.length;
        final radius = 150.0;
        final centerX = MediaQuery.of(context).size.width / 2;
        final centerY = MediaQuery.of(context).size.height / 2;
        
        final x = centerX + radius * cos(angle) - 30;
        final y = centerY + radius * sin(angle) - 30;
        
        return Positioned(
          left: x,
          top: y,
          child: _buildParticipantAvatar(participant),
        );
      }).toList(),
    );
  }

  Widget _buildParticipantAvatar(Map<String, dynamic> participant) {
    return Container(
      width: 60,
      height: 60,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(
          color: participant['isActive'] ? AppTheme.successColor : Colors.grey,
          width: 3,
        ),
        boxShadow: [
          BoxShadow(
            color: (participant['isActive'] ? AppTheme.successColor : Colors.grey)
                .withOpacity(0.3),
            blurRadius: 10,
            spreadRadius: 2,
          ),
        ],
      ),
      child: CircleAvatar(
        backgroundImage: participant['avatarUrl'] != null
            ? NetworkImage(participant['avatarUrl'])
            : null,
        child: participant['avatarUrl'] == null
            ? Text(
                participant['name']?.substring(0, 1).toUpperCase() ?? 'U',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              )
            : null,
      ),
    ).animate().scale(delay: 500.ms, curve: Curves.elasticOut);
  }

  Widget _buildInteractiveObjects(BuildContext context) {
    return Stack(
      children: [
        // Virtual whiteboard
        Positioned(
          top: 100,
          left: 50,
          child: VRWhiteboard(
            onContentChanged: (content) {
              ref.read(vrClassroomProvider.notifier).updateWhiteboard(content);
            },
          ),
        ),
        
        // 3D models
        Positioned(
          bottom: 150,
          right: 50,
          child: VR3DModels(
            onModelInteraction: (modelId, interaction) {
              ref.read(vrClassroomProvider.notifier).interactWithModel(modelId, interaction);
            },
          ),
        ),
        
        // Interactive quiz panel
        Positioned(
          top: 200,
          right: 100,
          child: _buildInteractiveQuiz(),
        ),
      ],
    );
  }

  Widget _buildInteractiveQuiz() {
    return Container(
      width: 200,
      padding: const EdgeInsets.all(AppTheme.spacing4),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.9),
        borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
        border: Border.all(color: AppTheme.primaryColor, width: 2),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryColor.withOpacity(0.3),
            blurRadius: 15,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Symbols.quiz,
            color: AppTheme.primaryColor,
            size: 32,
          ),
          const SizedBox(height: AppTheme.spacing2),
          Text(
            'Interactive Quiz',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: AppTheme.spacing2),
          Text(
            'Answer questions by interacting with 3D objects',
            style: Theme.of(context).textTheme.bodySmall,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: AppTheme.spacing3),
          ElevatedButton(
            onPressed: () => _startInteractiveQuiz(),
            style: ElevatedButton.styleFrom(
              minimumSize: const Size(double.infinity, 36),
            ),
            child: const Text('Start Quiz'),
          ),
        ],
      ),
    ).animate().fadeIn(delay: 800.ms).scale(begin: const Offset(0.8, 0.8));
  }

  Widget _buildSpatialUI(BuildContext context) {
    return Stack(
      children: [
        // Floating menu panels
        Positioned(
          top: 150,
          left: 20,
          child: _buildFloatingPanel(
            'Tools',
            [
              _buildToolButton(Symbols.brush, 'Draw', () {}),
              _buildToolButton(Symbols.text_fields, 'Text', () {}),
              _buildToolButton(Symbols.shapes, 'Shapes', () {}),
              _buildToolButton(Symbols.delete, 'Erase', () {}),
            ],
          ),
        ),
        
        // Environment controls
        Positioned(
          bottom: 200,
          left: 20,
          child: _buildFloatingPanel(
            'Environment',
            [
              _buildToolButton(Symbols.wb_sunny, 'Lighting', () {}),
              _buildToolButton(Symbols.palette, 'Theme', () {}),
              _buildToolButton(Symbols.view_in_ar, 'Objects', () {}),
              _buildToolButton(Symbols.settings, 'Settings', () {}),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildFloatingPanel(String title, List<Widget> tools) {
    return Container(
      padding: const EdgeInsets.all(AppTheme.spacing3),
      decoration: AppTheme.glassmorphismDecoration,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.labelMedium?.copyWith(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: AppTheme.spacing2),
          ...tools,
        ],
      ),
    ).animate().fadeIn(delay: 600.ms).slideX(begin: -0.2);
  }

  Widget _buildToolButton(IconData icon, String tooltip, VoidCallback onPressed) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppTheme.spacing1),
      child: IconButton(
        icon: Icon(icon, color: Colors.white),
        onPressed: onPressed,
        tooltip: tooltip,
        style: IconButton.styleFrom(
          backgroundColor: Colors.white.withOpacity(0.1),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppTheme.radiusSmall),
          ),
        ),
      ),
    );
  }

  Widget _buildUIOverlay(BuildContext context, VRClassroomState vrState) {
    return Positioned.fill(
      child: SafeArea(
        child: Column(
          children: [
            // Top bar
            _buildTopBar(context, vrState),
            
            const Spacer(),
            
            // Bottom controls
            _buildBottomControls(context, vrState),
          ],
        ),
      ),
    );
  }

  Widget _buildTopBar(BuildContext context, VRClassroomState vrState) {
    return Container(
      margin: const EdgeInsets.all(AppTheme.spacing4),
      padding: const EdgeInsets.symmetric(
        horizontal: AppTheme.spacing4,
        vertical: AppTheme.spacing3,
      ),
      decoration: AppTheme.glassmorphismDecoration,
      child: Row(
        children: [
          // Back button
          IconButton(
            icon: const Icon(Symbols.arrow_back, color: Colors.white),
            onPressed: () => Navigator.pop(context),
          ),
          
          const SizedBox(width: AppTheme.spacing2),
          
          // Room info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  vrState.roomName ?? 'VR Classroom',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  '${vrState.participants.length} participants',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.white.withOpacity(0.8),
                  ),
                ),
              ],
            ),
          ),
          
          // Connection status
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: AppTheme.spacing3,
              vertical: AppTheme.spacing1,
            ),
            decoration: BoxDecoration(
              color: vrState.isConnected 
                  ? AppTheme.successColor.withOpacity(0.2)
                  : AppTheme.errorColor.withOpacity(0.2),
              borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
              border: Border.all(
                color: vrState.isConnected 
                    ? AppTheme.successColor
                    : AppTheme.errorColor,
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: vrState.isConnected 
                        ? AppTheme.successColor
                        : AppTheme.errorColor,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: AppTheme.spacing2),
                Text(
                  vrState.isConnected ? 'Connected' : 'Connecting...',
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          
          // Settings menu
          IconButton(
            icon: const Icon(Symbols.settings, color: Colors.white),
            onPressed: () => _showVRSettings(context),
          ),
        ],
      ),
    ).animate().slideY(begin: -1.0, delay: 300.ms);
  }

  Widget _buildBottomControls(BuildContext context, VRClassroomState vrState) {
    return Container(
      margin: const EdgeInsets.all(AppTheme.spacing4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          // Microphone control
          _buildControlButton(
            icon: vrState.isMicrophoneOn ? Symbols.mic : Symbols.mic_off,
            label: 'Mic',
            isActive: vrState.isMicrophoneOn,
            onPressed: () => ref.read(vrClassroomProvider.notifier).toggleMicrophone(),
          ),
          
          // Camera control
          _buildControlButton(
            icon: vrState.isCameraOn ? Symbols.videocam : Symbols.videocam_off,
            label: 'Camera',
            isActive: vrState.isCameraOn,
            onPressed: () => ref.read(vrClassroomProvider.notifier).toggleCamera(),
          ),
          
          // Hand tracking
          _buildControlButton(
            icon: Symbols.back_hand,
            label: 'Hands',
            isActive: _isHandTrackingEnabled,
            onPressed: () => setState(() => _isHandTrackingEnabled = !_isHandTrackingEnabled),
          ),
          
          // Spatial audio
          _buildControlButton(
            icon: _isSpatialAudioEnabled ? Symbols.spatial_audio : Symbols.volume_off,
            label: 'Audio',
            isActive: _isSpatialAudioEnabled,
            onPressed: () => setState(() => _isSpatialAudioEnabled = !_isSpatialAudioEnabled),
          ),
          
          // Immersive mode toggle
          _buildControlButton(
            icon: _isImmersiveMode ? Symbols.fullscreen_exit : Symbols.fullscreen,
            label: 'Immersive',
            isActive: _isImmersiveMode,
            onPressed: _toggleImmersiveMode,
          ),
        ],
      ),
    ).animate().slideY(begin: 1.0, delay: 400.ms);
  }

  Widget _buildControlButton({
    required IconData icon,
    required String label,
    required bool isActive,
    required VoidCallback onPressed,
  }) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 56,
          height: 56,
          decoration: BoxDecoration(
            color: isActive 
                ? AppTheme.primaryColor.withOpacity(0.9)
                : Colors.white.withOpacity(0.1),
            borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
            border: Border.all(
              color: isActive 
                  ? AppTheme.primaryColor
                  : Colors.white.withOpacity(0.3),
              width: 2,
            ),
            boxShadow: [
              BoxShadow(
                color: (isActive ? AppTheme.primaryColor : Colors.white)
                    .withOpacity(0.3),
                blurRadius: 10,
                spreadRadius: 1,
              ),
            ],
          ),
          child: IconButton(
            icon: Icon(
              icon,
              color: Colors.white,
              size: 24,
            ),
            onPressed: onPressed,
          ),
        ),
        const SizedBox(height: AppTheme.spacing2),
        Text(
          label,
          style: Theme.of(context).textTheme.labelSmall?.copyWith(
            color: Colors.white.withOpacity(0.9),
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _buildImmersiveControls(BuildContext context) {
    return Positioned(
      right: 20,
      top: MediaQuery.of(context).size.height / 2 - 100,
      child: ImmersiveControls(
        isVisible: _isImmersiveMode,
        onToggleUI: _toggleImmersiveMode,
        onAdjustComfort: (level) => setState(() => _comfortLevel = level),
        onEmergencyExit: () => Navigator.pop(context),
      ),
    );
  }

  Widget _buildHandTrackingOverlay(BuildContext context) {
    if (!_isHandTrackingEnabled) return const SizedBox.shrink();
    
    return Positioned.fill(
      child: VRHandTracking(
        onGestureDetected: (gesture) {
          ref.read(vrClassroomProvider.notifier).handleGesture(gesture);
        },
        onHandPositionChanged: (leftHand, rightHand) {
          ref.read(vrClassroomProvider.notifier).updateHandPositions(leftHand, rightHand);
        },
      ),
    );
  }

  Widget _buildLoadingOverlay(BuildContext context) {
    return Container(
      color: Colors.black.withOpacity(0.8),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(AppTheme.primaryColor),
            ),
            const SizedBox(height: AppTheme.spacing4),
            Text(
              'Initializing VR Environment...',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: Colors.white,
              ),
            ),
            const SizedBox(height: AppTheme.spacing2),
            Text(
              'Please ensure your VR headset is connected',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.white.withOpacity(0.8),
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  void _toggleImmersiveMode() {
    setState(() {
      _isImmersiveMode = !_isImmersiveMode;
    });
    
    if (_isImmersiveMode) {
      _immersionController.forward();
    } else {
      _immersionController.reverse();
    }
  }

  void _showVRSettings(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.8,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(
            top: Radius.circular(AppTheme.radiusLarge),
          ),
        ),
        child: Column(
          children: [
            // Handle
            Container(
              width: 40,
              height: 4,
              margin: const EdgeInsets.symmetric(vertical: AppTheme.spacing2),
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            
            // Header
            Padding(
              padding: const EdgeInsets.all(AppTheme.spacing4),
              child: Row(
                children: [
                  Text(
                    'VR Settings',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Symbols.close),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
            ),
            
            // Settings content
            Expanded(
              child: ListView(
                padding: const EdgeInsets.symmetric(horizontal: AppTheme.spacing4),
                children: [
                  // Environment selector
                  VREnvironmentSelector(
                    selectedEnvironment: _selectedEnvironment,
                    onEnvironmentChanged: (environment) {
                      setState(() => _selectedEnvironment = environment);
                    },
                  ),
                  
                  const SizedBox(height: AppTheme.spacing6),
                  
                  // Comfort settings
                  _buildComfortSettings(),
                  
                  const SizedBox(height: AppTheme.spacing6),
                  
                  // Audio settings
                  SpatialAudioControls(
                    isEnabled: _isSpatialAudioEnabled,
                    onToggle: (enabled) => setState(() => _isSpatialAudioEnabled = enabled),
                  ),
                  
                  const SizedBox(height: AppTheme.spacing6),
                  
                  // Accessibility settings
                  _buildAccessibilitySettings(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildComfortSettings() {
    return AdaptiveCard(
      child: Padding(
        padding: const EdgeInsets.all(AppTheme.spacing4),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Comfort Settings',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: AppTheme.spacing4),
            
            // Comfort level slider
            Text(
              'Comfort Level: ${(_comfortLevel * 100).round()}%',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            Slider(
              value: _comfortLevel,
              onChanged: (value) => setState(() => _comfortLevel = value),
              divisions: 10,
              label: '${(_comfortLevel * 100).round()}%',
            ),
            
            const SizedBox(height: AppTheme.spacing3),
            
            // Motion sickness reduction
            SwitchListTile(
              title: const Text('Motion Sickness Reduction'),
              subtitle: const Text('Reduces camera movement and effects'),
              value: _comfortLevel < 0.5,
              onChanged: (value) {
                setState(() {
                  _comfortLevel = value ? 0.3 : 0.8;
                });
              },
            ),
            
            // Haptic feedback
            SwitchListTile(
              title: const Text('Haptic Feedback'),
              subtitle: const Text('Feel interactions through controller vibration'),
              value: _isHapticsEnabled,
              onChanged: (value) => setState(() => _isHapticsEnabled = value),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAccessibilitySettings() {
    return AdaptiveCard(
      child: Padding(
        padding: const EdgeInsets.all(AppTheme.spacing4),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Accessibility',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: AppTheme.spacing4),
            
            SwitchListTile(
              title: const Text('Voice Commands'),
              subtitle: const Text('Control VR with voice'),
              value: true,
              onChanged: (value) {},
            ),
            
            SwitchListTile(
              title: const Text('High Contrast Mode'),
              subtitle: const Text('Improve visibility for low vision'),
              value: false,
              onChanged: (value) {},
            ),
            
            SwitchListTile(
              title: const Text('Subtitle Display'),
              subtitle: const Text('Show captions for all audio'),
              value: true,
              onChanged: (value) {},
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildToolButton(IconData icon, String tooltip, VoidCallback onPressed) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppTheme.spacing1),
      child: IconButton(
        icon: Icon(icon, color: Colors.white),
        onPressed: onPressed,
        tooltip: tooltip,
        style: IconButton.styleFrom(
          backgroundColor: Colors.white.withOpacity(0.1),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppTheme.radiusSmall),
          ),
        ),
      ),
    );
  }

  void _startInteractiveQuiz() {
    // Start interactive VR quiz
    ref.read(vrClassroomProvider.notifier).startInteractiveQuiz();
  }

  String _getEnvironmentImage(String environment) {
    switch (environment) {
      case 'modern_classroom':
        return 'https://images.pexels.com/photos/5212345/pexels-photo-5212345.jpeg';
      case 'science_lab':
        return 'https://images.pexels.com/photos/2280549/pexels-photo-2280549.jpeg';
      case 'space_station':
        return 'https://images.pexels.com/photos/586063/pexels-photo-586063.jpeg';
      default:
        return 'https://images.pexels.com/photos/5212345/pexels-photo-5212345.jpeg';
    }
  }
}

// Custom painter for VR grid
class VRGridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.1)
      ..strokeWidth = 1;
    
    const gridSize = 50.0;
    
    // Draw vertical lines
    for (double x = 0; x < size.width; x += gridSize) {
      canvas.drawLine(
        Offset(x, 0),
        Offset(x, size.height),
        paint,
      );
    }
    
    // Draw horizontal lines
    for (double y = 0; y < size.height; y += gridSize) {
      canvas.drawLine(
        Offset(0, y),
        Offset(size.width, y),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

// Helper function for cosine calculation
double cos(double radians) {
  return math.cos(radians);
}

// Helper function for sine calculation  
double sin(double radians) {
  return math.sin(radians);
}

// Import math library
import 'dart:math' as math;