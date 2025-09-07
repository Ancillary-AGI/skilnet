import 'dart:async';
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:sensors_plus/sensors_plus.dart';

enum HandGesture {
  none,
  point,
  grab,
  pinch,
  thumbsUp,
  thumbsDown,
  openPalm,
  fist,
  peace,
  ok,
  swipeLeft,
  swipeRight,
  swipeUp,
  swipeDown,
  tap,
  doubleTap,
  longPress,
}

enum HandType {
  left,
  right,
}

class HandPosition {
  final Offset position;
  final double rotation;
  final double confidence;
  final HandType handType;
  final DateTime timestamp;

  HandPosition({
    required this.position,
    required this.rotation,
    required this.confidence,
    required this.handType,
    required this.timestamp,
  });
}

class GestureEvent {
  final HandGesture gesture;
  final HandType handType;
  final Offset position;
  final double confidence;
  final DateTime timestamp;
  final Map<String, dynamic> metadata;

  GestureEvent({
    required this.gesture,
    required this.handType,
    required this.position,
    required this.confidence,
    required this.timestamp,
    this.metadata = const {},
  });
}

class VRHandTracking extends StatefulWidget {
  final Function(GestureEvent)? onGestureDetected;
  final Function(HandPosition, HandPosition?)? onHandPositionChanged;
  final bool showVisualFeedback;
  final bool enableHapticFeedback;
  final double sensitivity;
  final List<HandGesture> enabledGestures;

  const VRHandTracking({
    super.key,
    this.onGestureDetected,
    this.onHandPositionChanged,
    this.showVisualFeedback = true,
    this.enableHapticFeedback = true,
    this.sensitivity = 0.8,
    this.enabledGestures = const [
      HandGesture.point,
      HandGesture.grab,
      HandGesture.pinch,
      HandGesture.tap,
      HandGesture.swipeLeft,
      HandGesture.swipeRight,
    ],
  });

  @override
  State<VRHandTracking> createState() => _VRHandTrackingState();
}

class _VRHandTrackingState extends State<VRHandTracking>
    with TickerProviderStateMixin {
  
  // Hand tracking state
  HandPosition? _leftHandPosition;
  HandPosition? _rightHandPosition;
  
  // Gesture recognition state
  HandGesture _currentGesture = HandGesture.none;
  HandGesture _previousGesture = HandGesture.none;
  DateTime _lastGestureTime = DateTime.now();
  
  // Animation controllers
  late AnimationController _leftHandController;
  late AnimationController _rightHandController;
  late AnimationController _gestureIndicatorController;
  
  // Animations
  late Animation<double> _leftHandOpacity;
  late Animation<double> _rightHandOpacity;
  late Animation<double> _gestureIndicatorScale;
  
  // Sensor subscriptions
  StreamSubscription<AccelerometerEvent>? _accelerometerSubscription;
  StreamSubscription<GyroscopeEvent>? _gyroscopeSubscription;
  StreamSubscription<MagnetometerEvent>? _magnetometerSubscription;
  
  // Gesture detection
  final List<Offset> _gesturePoints = [];
  Timer? _gestureTimer;
  
  // Calibration
  bool _isCalibrated = false;
  Offset _calibrationOffset = Offset.zero;
  
  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _initializeSensors();
    _startHandTracking();
  }

  void _initializeAnimations() {
    // Left hand animation
    _leftHandController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _leftHandOpacity = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _leftHandController,
      curve: Curves.easeInOut,
    ));

    // Right hand animation
    _rightHandController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _rightHandOpacity = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _rightHandController,
      curve: Curves.easeInOut,
    ));

    // Gesture indicator animation
    _gestureIndicatorController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    _gestureIndicatorScale = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _gestureIndicatorController,
      curve: Curves.elasticOut,
    ));
  }

  void _initializeSensors() {
    // Initialize accelerometer
    _accelerometerSubscription = accelerometerEvents.listen(
      (AccelerometerEvent event) {
        _processAccelerometerData(event);
      },
    );

    // Initialize gyroscope
    _gyroscopeSubscription = gyroscopeEvents.listen(
      (GyroscopeEvent event) {
        _processGyroscopeData(event);
      },
    );

    // Initialize magnetometer
    _magnetometerSubscription = magnetometerEvents.listen(
      (MagnetometerEvent event) {
        _processMagnetometerData(event);
      },
    );
  }

  void _startHandTracking() {
    // Start continuous hand tracking
    Timer.periodic(const Duration(milliseconds: 16), (timer) {
      if (mounted) {
        _updateHandTracking();
      } else {
        timer.cancel();
      }
    });
  }

  void _processAccelerometerData(AccelerometerEvent event) {
    // Process accelerometer data for hand movement detection
    final acceleration = math.sqrt(
      event.x * event.x + event.y * event.y + event.z * event.z
    );
    
    // Detect sudden movements for gesture recognition
    if (acceleration > 15.0) {
      _detectGestureFromMovement(event);
    }
  }

  void _processGyroscopeData(GyroscopeEvent event) {
    // Process gyroscope data for hand rotation
    final rotation = math.atan2(event.y, event.x);
    
    // Update hand rotation if tracking
    if (_rightHandPosition != null) {
      _updateHandRotation(HandType.right, rotation);
    }
  }

  void _processMagnetometerData(MagnetometerEvent event) {
    // Process magnetometer data for orientation
    // This can be used for more accurate hand orientation tracking
  }

  void _updateHandTracking() {
    // Simulate hand tracking using device sensors and touch input
    // In a real VR environment, this would use actual hand tracking hardware
    
    // Update hand positions based on current tracking data
    _updateHandPositions();
    
    // Detect gestures from hand positions
    _detectGesturesFromPositions();
    
    // Update UI
    if (mounted) {
      setState(() {});
    }
  }

  void _updateHandPositions() {
    // Simulate hand position updates
    // In production, this would use actual VR hand tracking data
    
    final now = DateTime.now();
    
    // Mock left hand position
    if (_leftHandPosition == null || 
        now.difference(_leftHandPosition!.timestamp).inMilliseconds > 100) {
      _leftHandPosition = HandPosition(
        position: Offset(
          100 + math.sin(now.millisecondsSinceEpoch / 1000) * 50,
          200 + math.cos(now.millisecondsSinceEpoch / 1000) * 30,
        ),
        rotation: math.sin(now.millisecondsSinceEpoch / 2000) * 0.5,
        confidence: 0.9,
        handType: HandType.left,
        timestamp: now,
      );
      
      _leftHandController.forward();
    }
    
    // Mock right hand position
    if (_rightHandPosition == null || 
        now.difference(_rightHandPosition!.timestamp).inMilliseconds > 100) {
      _rightHandPosition = HandPosition(
        position: Offset(
          300 + math.cos(now.millisecondsSinceEpoch / 1200) * 40,
          180 + math.sin(now.millisecondsSinceEpoch / 1500) * 35,
        ),
        rotation: math.cos(now.millisecondsSinceEpoch / 1800) * 0.3,
        confidence: 0.85,
        handType: HandType.right,
        timestamp: now,
      );
      
      _rightHandController.forward();
    }
    
    // Notify position changes
    if (widget.onHandPositionChanged != null) {
      widget.onHandPositionChanged!(_leftHandPosition!, _rightHandPosition);
    }
  }

  void _detectGesturesFromPositions() {
    if (_leftHandPosition == null || _rightHandPosition == null) return;
    
    // Calculate distance between hands
    final distance = (_leftHandPosition!.position - _rightHandPosition!.position).distance;
    
    // Detect gestures based on hand positions and movements
    HandGesture detectedGesture = HandGesture.none;
    
    // Pinch gesture - hands close together
    if (distance < 50 && widget.enabledGestures.contains(HandGesture.pinch)) {
      detectedGesture = HandGesture.pinch;
    }
    // Grab gesture - hands in grabbing position
    else if (distance > 100 && distance < 200 && 
             widget.enabledGestures.contains(HandGesture.grab)) {
      detectedGesture = HandGesture.grab;
    }
    // Point gesture - one hand extended
    else if (_rightHandPosition!.position.dy < _leftHandPosition!.position.dy - 50 &&
             widget.enabledGestures.contains(HandGesture.point)) {
      detectedGesture = HandGesture.point;
    }
    
    // Update gesture if changed
    if (detectedGesture != _currentGesture) {
      _onGestureChanged(detectedGesture);
    }
  }

  void _detectGestureFromMovement(AccelerometerEvent event) {
    // Detect swipe gestures from accelerometer data
    if (event.x > 8.0 && widget.enabledGestures.contains(HandGesture.swipeRight)) {
      _onGestureDetected(HandGesture.swipeRight, HandType.right);
    } else if (event.x < -8.0 && widget.enabledGestures.contains(HandGesture.swipeLeft)) {
      _onGestureDetected(HandGesture.swipeLeft, HandType.right);
    } else if (event.y > 8.0 && widget.enabledGestures.contains(HandGesture.swipeDown)) {
      _onGestureDetected(HandGesture.swipeDown, HandType.right);
    } else if (event.y < -8.0 && widget.enabledGestures.contains(HandGesture.swipeUp)) {
      _onGestureDetected(HandGesture.swipeUp, HandType.right);
    }
  }

  void _onGestureChanged(HandGesture newGesture) {
    _previousGesture = _currentGesture;
    _currentGesture = newGesture;
    _lastGestureTime = DateTime.now();
    
    if (newGesture != HandGesture.none) {
      _onGestureDetected(newGesture, HandType.right);
    }
  }

  void _onGestureDetected(HandGesture gesture, HandType handType) {
    // Provide haptic feedback
    if (widget.enableHapticFeedback) {
      HapticFeedback.lightImpact();
    }
    
    // Animate gesture indicator
    _gestureIndicatorController.reset();
    _gestureIndicatorController.forward();
    
    // Create gesture event
    final gestureEvent = GestureEvent(
      gesture: gesture,
      handType: handType,
      position: handType == HandType.left 
          ? _leftHandPosition?.position ?? Offset.zero
          : _rightHandPosition?.position ?? Offset.zero,
      confidence: handType == HandType.left 
          ? _leftHandPosition?.confidence ?? 0.0
          : _rightHandPosition?.confidence ?? 0.0,
      timestamp: DateTime.now(),
      metadata: {
        'sensitivity': widget.sensitivity,
        'previous_gesture': _previousGesture.toString(),
      },
    );
    
    // Notify gesture detection
    if (widget.onGestureDetected != null) {
      widget.onGestureDetected!(gestureEvent);
    }
  }

  void _updateHandRotation(HandType handType, double rotation) {
    if (handType == HandType.left && _leftHandPosition != null) {
      _leftHandPosition = HandPosition(
        position: _leftHandPosition!.position,
        rotation: rotation,
        confidence: _leftHandPosition!.confidence,
        handType: _leftHandPosition!.handType,
        timestamp: DateTime.now(),
      );
    } else if (handType == HandType.right && _rightHandPosition != null) {
      _rightHandPosition = HandPosition(
        position: _rightHandPosition!.position,
        rotation: rotation,
        confidence: _rightHandPosition!.confidence,
        handType: _rightHandPosition!.handType,
        timestamp: DateTime.now(),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.showVisualFeedback) {
      return const SizedBox.shrink();
    }

    return Stack(
      children: [
        // Left hand indicator
        if (_leftHandPosition != null)
          AnimatedBuilder(
            animation: _leftHandOpacity,
            builder: (context, child) {
              return Positioned(
                left: _leftHandPosition!.position.dx - 25,
                top: _leftHandPosition!.position.dy - 25,
                child: Opacity(
                  opacity: _leftHandOpacity.value * _leftHandPosition!.confidence,
                  child: Transform.rotate(
                    angle: _leftHandPosition!.rotation,
                    child: _buildHandIndicator(HandType.left),
                  ),
                ),
              );
            },
          ),

        // Right hand indicator
        if (_rightHandPosition != null)
          AnimatedBuilder(
            animation: _rightHandOpacity,
            builder: (context, child) {
              return Positioned(
                left: _rightHandPosition!.position.dx - 25,
                top: _rightHandPosition!.position.dy - 25,
                child: Opacity(
                  opacity: _rightHandOpacity.value * _rightHandPosition!.confidence,
                  child: Transform.rotate(
                    angle: _rightHandPosition!.rotation,
                    child: _buildHandIndicator(HandType.right),
                  ),
                ),
              );
            },
          ),

        // Gesture indicator
        if (_currentGesture != HandGesture.none)
          Center(
            child: AnimatedBuilder(
              animation: _gestureIndicatorScale,
              builder: (context, child) {
                return Transform.scale(
                  scale: _gestureIndicatorScale.value,
                  child: _buildGestureIndicator(_currentGesture),
                );
              },
            ),
          ),

        // Gesture trail
        if (_gesturePoints.isNotEmpty)
          CustomPaint(
            painter: GestureTrailPainter(_gesturePoints),
            size: Size.infinite,
          ),
      ],
    );
  }

  Widget _buildHandIndicator(HandType handType) {
    final color = handType == HandType.left ? Colors.blue : Colors.red;
    
    return Container(
      width: 50,
      height: 50,
      decoration: BoxDecoration(
        color: color.withOpacity(0.3),
        border: Border.all(color: color, width: 2),
        borderRadius: BorderRadius.circular(25),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.5),
            blurRadius: 10,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Icon(
        handType == HandType.left ? Icons.back_hand : Icons.front_hand,
        color: color,
        size: 30,
      ),
    );
  }

  Widget _buildGestureIndicator(HandGesture gesture) {
    IconData icon;
    Color color;
    
    switch (gesture) {
      case HandGesture.point:
        icon = Icons.touch_app;
        color = Colors.yellow;
        break;
      case HandGesture.grab:
        icon = Icons.pan_tool;
        color = Colors.green;
        break;
      case HandGesture.pinch:
        icon = Icons.pinch;
        color = Colors.purple;
        break;
      case HandGesture.thumbsUp:
        icon = Icons.thumb_up;
        color = Colors.green;
        break;
      case HandGesture.thumbsDown:
        icon = Icons.thumb_down;
        color = Colors.red;
        break;
      case HandGesture.swipeLeft:
        icon = Icons.arrow_back;
        color = Colors.blue;
        break;
      case HandGesture.swipeRight:
        icon = Icons.arrow_forward;
        color = Colors.blue;
        break;
      case HandGesture.swipeUp:
        icon = Icons.arrow_upward;
        color = Colors.blue;
        break;
      case HandGesture.swipeDown:
        icon = Icons.arrow_downward;
        color = Colors.blue;
        break;
      default:
        icon = Icons.gesture;
        color = Colors.grey;
    }
    
    return Container(
      width: 80,
      height: 80,
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        border: Border.all(color: color, width: 3),
        borderRadius: BorderRadius.circular(40),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.6),
            blurRadius: 15,
            spreadRadius: 3,
          ),
        ],
      ),
      child: Icon(
        icon,
        color: color,
        size: 40,
      ),
    );
  }

  @override
  void dispose() {
    _leftHandController.dispose();
    _rightHandController.dispose();
    _gestureIndicatorController.dispose();
    _accelerometerSubscription?.cancel();
    _gyroscopeSubscription?.cancel();
    _magnetometerSubscription?.cancel();
    _gestureTimer?.cancel();
    super.dispose();
  }
}

class GestureTrailPainter extends CustomPainter {
  final List<Offset> points;

  GestureTrailPainter(this.points);

  @override
  void paint(Canvas canvas, Size size) {
    if (points.length < 2) return;

    final paint = Paint()
      ..color = Colors.white.withOpacity(0.6)
      ..strokeWidth = 3.0
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;

    final path = Path();
    path.moveTo(points.first.dx, points.first.dy);

    for (int i = 1; i < points.length; i++) {
      path.lineTo(points[i].dx, points[i].dy);
    }

    canvas.drawPath(path, paint);

    // Draw points
    final pointPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;

    for (final point in points) {
      canvas.drawCircle(point, 2, pointPaint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return true;
  }
}

// Extension methods for gesture utilities
extension HandGestureExtension on HandGesture {
  String get displayName {
    switch (this) {
      case HandGesture.point:
        return 'Point';
      case HandGesture.grab:
        return 'Grab';
      case HandGesture.pinch:
        return 'Pinch';
      case HandGesture.thumbsUp:
        return 'Thumbs Up';
      case HandGesture.thumbsDown:
        return 'Thumbs Down';
      case HandGesture.openPalm:
        return 'Open Palm';
      case HandGesture.fist:
        return 'Fist';
      case HandGesture.peace:
        return 'Peace';
      case HandGesture.ok:
        return 'OK';
      case HandGesture.swipeLeft:
        return 'Swipe Left';
      case HandGesture.swipeRight:
        return 'Swipe Right';
      case HandGesture.swipeUp:
        return 'Swipe Up';
      case HandGesture.swipeDown:
        return 'Swipe Down';
      case HandGesture.tap:
        return 'Tap';
      case HandGesture.doubleTap:
        return 'Double Tap';
      case HandGesture.longPress:
        return 'Long Press';
      default:
        return 'None';
    }
  }

  bool get isSwipeGesture {
    return [
      HandGesture.swipeLeft,
      HandGesture.swipeRight,
      HandGesture.swipeUp,
      HandGesture.swipeDown,
    ].contains(this);
  }

  bool get isTapGesture {
    return [
      HandGesture.tap,
      HandGesture.doubleTap,
      HandGesture.longPress,
    ].contains(this);
  }
}