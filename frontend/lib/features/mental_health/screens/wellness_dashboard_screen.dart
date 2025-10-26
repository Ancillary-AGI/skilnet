import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:material_symbols_icons/symbols.dart';
import 'package:fl_chart/fl_chart.dart';

import '../../../core/theme/app_theme.dart';
import '../../../shared/widgets/adaptive_card.dart';
import '../../../shared/widgets/progress_ring.dart';
import '../providers/wellness_provider.dart';
import '../widgets/breathing_exercise_widget.dart';
import '../widgets/mood_tracker_widget.dart';
import '../widgets/stress_monitor_widget.dart';
import '../widgets/wellness_insights_widget.dart';
import '../widgets/wellness_goals_widget.dart';

class WellnessDashboardScreen extends ConsumerStatefulWidget {
  const WellnessDashboardScreen({super.key});

  @override
  ConsumerState<WellnessDashboardScreen> createState() =>
      _WellnessDashboardScreenState();
}

class _WellnessDashboardScreenState
    extends ConsumerState<WellnessDashboardScreen>
    with TickerProviderStateMixin {
  late AnimationController _fadeController;
  late AnimationController _slideController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  int _selectedTabIndex = 0;

  @override
  void initState() {
    super.initState();

    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _slideController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeOut,
    ));

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.1),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _slideController,
      curve: Curves.easeOutCubic,
    ));

    _fadeController.forward();
    _slideController.forward();
  }

  @override
  void dispose() {
    _fadeController.dispose();
    _slideController.dispose();
    super.dispose();
  }

  // Mock wellness state for development
  dynamic _getMockWellnessState() {
    return {
      'currentMoodScore': 75.0,
      'currentStressLevel': 45.0,
      'currentFocusScore': 80.0,
      'currentEnergyLevel': 70.0,
    };
  }

  @override
  Widget build(BuildContext context) {
    final wellnessState = _getMockWellnessState();

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App bar with wellness greeting
          SliverAppBar(
            expandedHeight: 200,
            floating: false,
            pinned: true,
            backgroundColor: Colors.transparent,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Color(0xFF667eea),
                      Color(0xFF764ba2),
                    ],
                  ),
                ),
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.all(AppTheme.spacing4),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(AppTheme.spacing2),
                              decoration: BoxDecoration(
                                color: Colors.white.withOpacity(0.2),
                                borderRadius:
                                    BorderRadius.circular(AppTheme.radiusSmall),
                              ),
                              child: const Icon(
                                Symbols.psychology,
                                color: Colors.white,
                                size: 24,
                              ),
                            ),
                            const SizedBox(width: AppTheme.spacing3),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Wellness Dashboard',
                                    style: Theme.of(context)
                                        .textTheme
                                        .headlineSmall
                                        ?.copyWith(
                                          color: Colors.white,
                                          fontWeight: FontWeight.bold,
                                        ),
                                  ),
                                  Text(
                                    _getWellnessGreeting(wellnessState),
                                    style: Theme.of(context)
                                        .textTheme
                                        .bodyMedium
                                        ?.copyWith(
                                          color: Colors.white.withOpacity(0.9),
                                        ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            actions: [
              IconButton(
                icon: const Icon(Symbols.emergency, color: Colors.white),
                onPressed: () => _showCrisisSupport(context),
                tooltip: 'Crisis Support',
              ),
              IconButton(
                icon: const Icon(Symbols.settings, color: Colors.white),
                onPressed: () => _showWellnessSettings(context),
                tooltip: 'Wellness Settings',
              ),
            ],
          ),

          // Main content
          SliverPadding(
            padding: const EdgeInsets.all(AppTheme.spacing4),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                // Quick wellness check
                _buildQuickWellnessCheck(context, wellnessState),
                const SizedBox(height: AppTheme.spacing6),

                // Wellness metrics overview
                _buildWellnessMetrics(context, wellnessState),
                const SizedBox(height: AppTheme.spacing6),

                // Mood tracker
                const MoodTrackerWidget(),
                const SizedBox(height: AppTheme.spacing6),

                // Stress monitor
                const StressMonitorWidget(),
                const SizedBox(height: AppTheme.spacing6),

                // Wellness insights
                const WellnessInsightsWidget(),
                const SizedBox(height: AppTheme.spacing6),

                // Wellness goals
                const WellnessGoalsWidget(),
                const SizedBox(height: AppTheme.spacing6),

                // Quick interventions
                _buildQuickInterventions(context),
                const SizedBox(height: AppTheme.spacing6),

                // Learning wellness correlation
                _buildLearningWellnessCorrelation(context, wellnessState),
              ]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickWellnessCheck(BuildContext context, dynamic wellnessState) {
    return AdaptiveCard(
      child: Padding(
        padding: const EdgeInsets.all(AppTheme.spacing4),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Symbols.favorite,
                  color: Colors.red.shade400,
                  size: 24,
                ),
                const SizedBox(width: AppTheme.spacing2),
                Text(
                  'How are you feeling today?',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const SizedBox(height: AppTheme.spacing4),

            // Quick mood selection
            Wrap(
              spacing: AppTheme.spacing2,
              runSpacing: AppTheme.spacing2,
              children: [
                _buildMoodButton('😊', 'Great', Colors.green),
                _buildMoodButton('🙂', 'Good', Colors.blue),
                _buildMoodButton('😐', 'Okay', Colors.orange),
                _buildMoodButton('😔', 'Not Good', Colors.red),
                _buildMoodButton('😰', 'Stressed', Colors.purple),
              ],
            ),

            const SizedBox(height: AppTheme.spacing4),

            // Quick actions
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _startBreathingExercise(context),
                    icon: const Icon(Symbols.air, size: 18),
                    label: const Text('Breathe'),
                  ),
                ),
                const SizedBox(width: AppTheme.spacing2),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _startMindfulnessSession(context),
                    icon: const Icon(Symbols.self_improvement, size: 18),
                    label: const Text('Mindfulness'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    ).animate().fadeIn(delay: 200.ms).slideY(begin: 0.1);
  }

  Widget _buildMoodButton(String emoji, String label, Color color) {
    return InkWell(
      onTap: () => _recordMood(label.toLowerCase()),
      borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: AppTheme.spacing3,
          vertical: AppTheme.spacing2,
        ),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              emoji,
              style: const TextStyle(fontSize: 24),
            ),
            const SizedBox(height: AppTheme.spacing1),
            Text(
              label,
              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                    color: color,
                    fontWeight: FontWeight.w600,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWellnessMetrics(BuildContext context, dynamic wellnessState) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Wellness Overview',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: AppTheme.spacing4),
        GridView.count(
          crossAxisCount: MediaQuery.of(context).size.width < 600 ? 2 : 4,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: AppTheme.spacing3,
          crossAxisSpacing: AppTheme.spacing3,
          childAspectRatio: 1.1,
          children: [
            _buildMetricCard(
              'Mood Score',
              wellnessState.currentMoodScore,
              100,
              Colors.green,
              Symbols.sentiment_satisfied,
            ),
            _buildMetricCard(
              'Stress Level',
              wellnessState.currentStressLevel,
              100,
              Colors.orange,
              Symbols.psychology,
            ),
            _buildMetricCard(
              'Focus Score',
              wellnessState.currentFocusScore,
              100,
              Colors.blue,
              Symbols.center_focus_strong,
            ),
            _buildMetricCard(
              'Energy Level',
              wellnessState.currentEnergyLevel,
              100,
              Colors.purple,
              Symbols.bolt,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildMetricCard(
    String title,
    double value,
    double maxValue,
    Color color,
    IconData icon,
  ) {
    final percentage = (value / maxValue).clamp(0.0, 1.0);

    return AdaptiveCard(
      child: Padding(
        padding: const EdgeInsets.all(AppTheme.spacing4),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ProgressRing(
              progress: percentage,
              size: 60,
              strokeWidth: 6,
              backgroundColor: color.withOpacity(0.2),
              progressColor: color,
              child: Icon(
                icon,
                color: color,
                size: 24,
              ),
            ),
            const SizedBox(height: AppTheme.spacing3),
            Text(
              title,
              style: Theme.of(context).textTheme.labelMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
              textAlign: TextAlign.center,
            ),
            Text(
              '${value.round()}/${maxValue.round()}',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppTheme.textSecondary,
                  ),
            ),
          ],
        ),
      ),
    ).animate().fadeIn(delay: 300.ms).scale(begin: const Offset(0.9, 0.9));
  }

  Widget _buildQuickInterventions(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Quick Wellness Boost',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: AppTheme.spacing4),
        GridView.count(
          crossAxisCount: MediaQuery.of(context).size.width < 600 ? 2 : 3,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: AppTheme.spacing3,
          crossAxisSpacing: AppTheme.spacing3,
          childAspectRatio: 1.3,
          children: [
            _buildInterventionCard(
              'Breathing Exercise',
              '5 min guided breathing',
              Symbols.air,
              const Color(0xFF4FC3F7),
              () => _startBreathingExercise(context),
            ),
            _buildInterventionCard(
              'Mindfulness',
              '10 min meditation',
              Symbols.self_improvement,
              const Color(0xFF81C784),
              () => _startMindfulnessSession(context),
            ),
            _buildInterventionCard(
              'Movement Break',
              '5 min stretching',
              Symbols.directions_walk,
              const Color(0xFFFFB74D),
              () => _startMovementBreak(context),
            ),
            _buildInterventionCard(
              'Gratitude Practice',
              'Quick gratitude log',
              Symbols.favorite,
              const Color(0xFFE57373),
              () => _startGratitudePractice(context),
            ),
            _buildInterventionCard(
              'Social Connection',
              'Connect with peers',
              Symbols.people,
              const Color(0xFFBA68C8),
              () => _openSocialConnection(context),
            ),
            _buildInterventionCard(
              'Learning Break',
              'Pause and reflect',
              Symbols.pause_circle,
              const Color(0xFF64B5F6),
              () => _suggestLearningBreak(context),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildInterventionCard(
    String title,
    String subtitle,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return AdaptiveCard(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.all(AppTheme.spacing4),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(AppTheme.spacing3),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
              ),
              child: Icon(
                icon,
                color: color,
                size: 32,
              ),
            ),
            const SizedBox(height: AppTheme.spacing2),
            Text(
              title,
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
              textAlign: TextAlign.center,
            ),
            Text(
              subtitle,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppTheme.textSecondary,
                  ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    ).animate().fadeIn(delay: 400.ms).scale(begin: const Offset(0.8, 0.8));
  }

  Widget _buildLearningWellnessCorrelation(
      BuildContext context, dynamic wellnessState) {
    return AdaptiveCard(
      child: Padding(
        padding: const EdgeInsets.all(AppTheme.spacing4),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Symbols.analytics,
                  color: AppTheme.primaryColor,
                  size: 24,
                ),
                const SizedBox(width: AppTheme.spacing2),
                Text(
                  'Learning & Wellness Insights',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const SizedBox(height: AppTheme.spacing4),

            // Correlation chart
            SizedBox(
              height: 200,
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(show: true),
                  titlesData: FlTitlesData(
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 40,
                        getTitlesWidget: (value, meta) {
                          return Text(
                            value.toInt().toString(),
                            style: Theme.of(context).textTheme.bodySmall,
                          );
                        },
                      ),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 30,
                        getTitlesWidget: (value, meta) {
                          final days = [
                            'Mon',
                            'Tue',
                            'Wed',
                            'Thu',
                            'Fri',
                            'Sat',
                            'Sun'
                          ];
                          if (value.toInt() < days.length) {
                            return Text(
                              days[value.toInt()],
                              style: Theme.of(context).textTheme.bodySmall,
                            );
                          }
                          return const Text('');
                        },
                      ),
                    ),
                    rightTitles:
                        AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    topTitles:
                        AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  ),
                  borderData: FlBorderData(show: false),
                  lineBarsData: [
                    // Mood line
                    LineChartBarData(
                      spots: _generateMoodSpots(),
                      isCurved: true,
                      color: Colors.green,
                      barWidth: 3,
                      dotData: FlDotData(show: true),
                    ),
                    // Learning performance line
                    LineChartBarData(
                      spots: _generatePerformanceSpots(),
                      isCurved: true,
                      color: AppTheme.primaryColor,
                      barWidth: 3,
                      dotData: FlDotData(show: true),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: AppTheme.spacing4),

            // Legend
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildLegendItem('Mood Score', Colors.green),
                _buildLegendItem('Learning Performance', AppTheme.primaryColor),
              ],
            ),

            const SizedBox(height: AppTheme.spacing4),

            // Insights
            Container(
              padding: const EdgeInsets.all(AppTheme.spacing3),
              decoration: BoxDecoration(
                color: AppTheme.primaryColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(AppTheme.radiusSmall),
              ),
              child: Row(
                children: [
                  Icon(
                    Symbols.lightbulb,
                    color: AppTheme.primaryColor,
                    size: 20,
                  ),
                  const SizedBox(width: AppTheme.spacing2),
                  Expanded(
                    child: Text(
                      'Your learning performance improves by 23% when your mood score is above 70.',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: AppTheme.primaryColor,
                          ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    ).animate().fadeIn(delay: 600.ms).slideY(begin: 0.1);
  }

  Widget _buildLegendItem(String label, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(6),
          ),
        ),
        const SizedBox(width: AppTheme.spacing1),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }

  List<FlSpot> _generateMoodSpots() {
    // Mock data - in production, use actual mood data
    return [
      const FlSpot(0, 75),
      const FlSpot(1, 80),
      const FlSpot(2, 65),
      const FlSpot(3, 85),
      const FlSpot(4, 70),
      const FlSpot(5, 90),
      const FlSpot(6, 85),
    ];
  }

  List<FlSpot> _generatePerformanceSpots() {
    // Mock data - in production, use actual performance data
    return [
      const FlSpot(0, 70),
      const FlSpot(1, 75),
      const FlSpot(2, 60),
      const FlSpot(3, 80),
      const FlSpot(4, 65),
      const FlSpot(5, 85),
      const FlSpot(6, 80),
    ];
  }

  String _getWellnessGreeting(dynamic wellnessState) {
    final hour = DateTime.now().hour;
    final timeGreeting = hour < 12
        ? 'Good morning'
        : hour < 17
            ? 'Good afternoon'
            : 'Good evening';

    if (wellnessState.currentMoodScore > 80) {
      return '$timeGreeting! You\'re doing great today! 🌟';
    } else if (wellnessState.currentMoodScore > 60) {
      return '$timeGreeting! How can we make today even better?';
    } else {
      return '$timeGreeting! Let\'s focus on your wellbeing today. 💙';
    }
  }

  void _recordMood(String mood) {
    // Mock implementation - record mood locally
    debugPrint('Mood recorded: $mood');

    // Show confirmation
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Mood recorded: $mood'),
        backgroundColor: Colors.green,
        duration: const Duration(seconds: 2),
      ),
    );
  }

  void _startBreathingExercise(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => const BreathingExerciseWidget(),
    );
  }

  void _startMindfulnessSession(BuildContext context) {
    // Navigate to mindfulness session
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const MindfulnessSessionScreen(),
      ),
    );
  }

  void _startMovementBreak(BuildContext context) {
    // Start movement break session
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Movement Break'),
        content: const Text(
            'Time for a 5-minute movement break! Stand up, stretch, and move around.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Later'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _startMovementTimer();
            },
            child: const Text('Start Now'),
          ),
        ],
      ),
    );
  }

  void _startGratitudePractice(BuildContext context) {
    // Open gratitude practice dialog
    showDialog(
      context: context,
      builder: (context) => const GratitudePracticeDialog(),
    );
  }

  void _openSocialConnection(BuildContext context) {
    // Navigate to social features
    Navigator.pushNamed(context, '/social/connect');
  }

  void _suggestLearningBreak(BuildContext context) {
    // Suggest taking a break from learning
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Learning Break Suggested'),
        content: const Text(
            'Based on your current wellness state, taking a break might help improve your learning performance. Would you like to pause your current session?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Continue Learning'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _pauseLearningSession();
            },
            child: const Text('Take Break'),
          ),
        ],
      ),
    );
  }

  void _startMovementTimer() {
    // Implementation for movement break timer
  }

  void _pauseLearningSession() {
    // Implementation for pausing learning session
  }

  void _showCrisisSupport(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(
              Symbols.emergency,
              color: Colors.red,
              size: 24,
            ),
            const SizedBox(width: AppTheme.spacing2),
            const Text('Crisis Support'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'If you\'re experiencing a mental health crisis, please reach out for immediate help:',
            ),
            const SizedBox(height: AppTheme.spacing3),

            // Emergency contacts
            _buildEmergencyContact('Crisis Text Line', 'Text HOME to 741741'),
            _buildEmergencyContact(
                'National Suicide Prevention Lifeline', '988'),
            _buildEmergencyContact('Emergency Services', '911'),

            const SizedBox(height: AppTheme.spacing3),
            const Text(
              'You can also connect with our wellness support team 24/7.',
              style: TextStyle(fontWeight: FontWeight.w500),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _connectToWellnessTeam();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green,
            ),
            child: const Text('Connect to Support'),
          ),
        ],
      ),
    );
  }

  Widget _buildEmergencyContact(String name, String contact) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppTheme.spacing1),
      child: Row(
        children: [
          Icon(
            Symbols.phone,
            color: Colors.red,
            size: 16,
          ),
          const SizedBox(width: AppTheme.spacing2),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
                Text(
                  contact,
                  style: TextStyle(
                    color: AppTheme.textSecondary,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showWellnessSettings(BuildContext context) {
    // Navigate to wellness settings
    Navigator.pushNamed(context, '/wellness/settings');
  }

  void _connectToWellnessTeam() {
    // Implementation for connecting to wellness support team
  }
}

// Additional wellness screens
class MindfulnessSessionScreen extends StatelessWidget {
  const MindfulnessSessionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mindfulness Session'),
        backgroundColor: Colors.transparent,
      ),
      body: const Center(
        child: Text('Mindfulness session content would go here'),
      ),
    );
  }
}

class GratitudePracticeDialog extends StatefulWidget {
  const GratitudePracticeDialog({super.key});

  @override
  State<GratitudePracticeDialog> createState() =>
      _GratitudePracticeDialogState();
}

class _GratitudePracticeDialogState extends State<GratitudePracticeDialog> {
  final List<TextEditingController> _controllers = [
    TextEditingController(),
    TextEditingController(),
    TextEditingController(),
  ];

  @override
  void dispose() {
    for (final controller in _controllers) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(
        children: [
          Icon(
            Symbols.favorite,
            color: Colors.red.shade400,
            size: 24,
          ),
          const SizedBox(width: AppTheme.spacing2),
          const Text('Gratitude Practice'),
        ],
      ),
      content: SizedBox(
        width: double.maxFinite,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Take a moment to reflect on three things you\'re grateful for today:',
            ),
            const SizedBox(height: AppTheme.spacing4),
            for (int i = 0; i < 3; i++) ...[
              TextField(
                controller: _controllers[i],
                decoration: InputDecoration(
                  labelText: 'Gratitude ${i + 1}',
                  hintText: 'What are you grateful for?',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(AppTheme.radiusSmall),
                  ),
                ),
                maxLines: 2,
              ),
              if (i < 2) const SizedBox(height: AppTheme.spacing3),
            ],
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () {
            _saveGratitudeEntries();
            Navigator.pop(context);
          },
          child: const Text('Save'),
        ),
      ],
    );
  }

  void _saveGratitudeEntries() {
    final entries = _controllers
        .map((controller) => controller.text.trim())
        .where((text) => text.isNotEmpty)
        .toList();

    if (entries.isNotEmpty) {
      // Save gratitude entries
      // Implementation for saving gratitude entries

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Gratitude entries saved! 🙏'),
          backgroundColor: Colors.green,
        ),
      );
    }
  }
}
