import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:material_symbols_icons/symbols.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/router/app_router.dart';
import '../../../shared/widgets/adaptive_card.dart';
import '../../../shared/widgets/feature_card.dart';
import '../../../shared/widgets/progress_ring.dart';
import '../../../shared/widgets/shimmer_loading.dart';
import '../../auth/providers/auth_provider.dart';
import '../../courses/providers/course_provider.dart';
import '../../dashboard/widgets/learning_stats_widget.dart';
import '../../dashboard/widgets/recent_activity_widget.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: AppTheme.animationMedium,
      vsync: this,
    );
    
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: AppCurves.easeOutQuart,
    ));
    
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.1),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: AppCurves.easeOutQuart,
    ));
    
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(authProvider).user;
    final featuredCourses = ref.watch(featuredCoursesProvider);
    final continueLearning = ref.watch(continuelearningProvider);
    
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App bar with user greeting
          SliverAppBar(
            expandedHeight: 200,
            floating: false,
            pinned: true,
            backgroundColor: Colors.transparent,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: const BoxDecoration(
                  gradient: AppTheme.primaryGradient,
                ),
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.all(AppTheme.spacing4),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        FadeTransition(
                          opacity: _fadeAnimation,
                          child: SlideTransition(
                            position: _slideAnimation,
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  _getGreeting(),
                                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                    color: Colors.white.withOpacity(0.9),
                                  ),
                                ),
                                const SizedBox(height: AppTheme.spacing1),
                                Text(
                                  user?.fullName ?? 'Welcome to EduVerse',
                                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const SizedBox(height: AppTheme.spacing2),
                                Text(
                                  'Ready to explore new worlds of knowledge?',
                                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                    color: Colors.white.withOpacity(0.8),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            actions: [
              IconButton(
                icon: const Icon(Symbols.notifications, color: Colors.white),
                onPressed: () => _showNotifications(context),
              ),
              IconButton(
                icon: CircleAvatar(
                  radius: 16,
                  backgroundImage: user?.avatarUrl != null
                      ? CachedNetworkImageProvider(user!.avatarUrl!)
                      : null,
                  child: user?.avatarUrl == null
                      ? Text(
                          user?.fullName?.substring(0, 1).toUpperCase() ?? 'U',
                          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
                        )
                      : null,
                ),
                onPressed: () => AppNavigation.goToProfile(context),
              ),
              const SizedBox(width: AppTheme.spacing2),
            ],
          ),
          
          // Main content
          SliverPadding(
            padding: const EdgeInsets.all(AppTheme.spacing4),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                // Quick actions
                _buildQuickActions(context),
                const SizedBox(height: AppTheme.spacing6),
                
                // Continue learning section
                _buildContinueLearning(context, continueLearning),
                const SizedBox(height: AppTheme.spacing6),
                
                // Learning stats
                const LearningStatsWidget(),
                const SizedBox(height: AppTheme.spacing6),
                
                // Featured experiences
                _buildFeaturedExperiences(context),
                const SizedBox(height: AppTheme.spacing6),
                
                // Featured courses
                _buildFeaturedCourses(context, featuredCourses),
                const SizedBox(height: AppTheme.spacing6),
                
                // Recent activity
                const RecentActivityWidget(),
                const SizedBox(height: AppTheme.spacing6),
                
                // AI recommendations
                _buildAIRecommendations(context),
              ]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Quick Actions',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: AppTheme.spacing4),
        GridView.count(
          crossAxisCount: AppTheme.isMobile(context) ? 2 : 4,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: AppTheme.spacing3,
          crossAxisSpacing: AppTheme.spacing3,
          childAspectRatio: 1.2,
          children: [
            FeatureCard(
              title: 'VR Classroom',
              subtitle: 'Immersive Learning',
              icon: Symbols.view_in_ar,
              color: FeatureColors.vrClassroom,
              onTap: () => _joinVRClassroom(context),
            ).animate().fadeIn(delay: 100.ms).slideX(begin: -0.1),
            
            FeatureCard(
              title: 'AI Tutor',
              subtitle: '24/7 Assistant',
              icon: Symbols.psychology,
              color: FeatureColors.aiTutor,
              onTap: () => AppNavigation.goToAITutor(context),
            ).animate().fadeIn(delay: 200.ms).slideX(begin: -0.1),
            
            FeatureCard(
              title: 'Live Classes',
              subtitle: 'Join Now',
              icon: Symbols.video_call,
              color: FeatureColors.liveClass,
              onTap: () => _joinLiveClass(context),
            ).animate().fadeIn(delay: 300.ms).slideX(begin: -0.1),
            
            FeatureCard(
              title: 'AR Lab',
              subtitle: 'Hands-on Practice',
              icon: Symbols.science,
              color: FeatureColors.arExperience,
              onTap: () => _startARExperience(context),
            ).animate().fadeIn(delay: 400.ms).slideX(begin: -0.1),
          ],
        ),
      ],
    );
  }

  Widget _buildContinueLearning(BuildContext context, AsyncValue<List<dynamic>> continueLearning) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Continue Learning',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            TextButton(
              onPressed: () => AppNavigation.goToCourse(context, 'all'),
              child: const Text('View All'),
            ),
          ],
        ),
        const SizedBox(height: AppTheme.spacing4),
        
        continueLearning.when(
          data: (courses) => SizedBox(
            height: 200,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: courses.length,
              itemBuilder: (context, index) {
                final course = courses[index];
                return Container(
                  width: 300,
                  margin: const EdgeInsets.only(right: AppTheme.spacing4),
                  child: AdaptiveCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        ClipRRect(
                          borderRadius: const BorderRadius.vertical(
                            top: Radius.circular(AppTheme.radiusMedium),
                          ),
                          child: AspectRatio(
                            aspectRatio: 16 / 9,
                            child: CachedNetworkImage(
                              imageUrl: course['thumbnail'] ?? 'https://images.pexels.com/photos/5212345/pexels-photo-5212345.jpeg',
                              fit: BoxFit.cover,
                              placeholder: (context, url) => const ShimmerLoading(),
                              errorWidget: (context, url, error) => Container(
                                color: Colors.grey.shade200,
                                child: const Icon(Icons.image_not_supported),
                              ),
                            ),
                          ),
                        ),
                        Expanded(
                          child: Padding(
                            padding: const EdgeInsets.all(AppTheme.spacing4),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  course['title'] ?? 'Course Title',
                                  style: Theme.of(context).textTheme.titleMedium,
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                const SizedBox(height: AppTheme.spacing2),
                                Row(
                                  children: [
                                    Expanded(
                                      child: ProgressRing(
                                        progress: (course['progress'] ?? 0.0) / 100.0,
                                        size: 40,
                                        strokeWidth: 4,
                                        backgroundColor: Colors.grey.shade200,
                                        progressColor: AppTheme.primaryColor,
                                        child: Text(
                                          '${course['progress'] ?? 0}%',
                                          style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ),
                                    ),
                                    const SizedBox(width: AppTheme.spacing3),
                                    Expanded(
                                      flex: 2,
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            'Next: ${course['nextLesson'] ?? 'Complete'}',
                                            style: Theme.of(context).textTheme.bodySmall,
                                            maxLines: 1,
                                            overflow: TextOverflow.ellipsis,
                                          ),
                                          Text(
                                            '${course['timeLeft'] ?? 0} min left',
                                            style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                              color: AppTheme.textSecondary,
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
                      ],
                    ),
                  ),
                ).animate().fadeIn(delay: (index * 100).ms).slideX(begin: 0.1);
              },
            ),
          ),
          loading: () => const ShimmerLoading(height: 200),
          error: (error, stack) => Center(
            child: Text('Error loading courses: $error'),
          ),
        ),
      ],
    );
  }

  Widget _buildFeaturedExperiences(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Immersive Experiences',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: AppTheme.spacing4),
        
        SizedBox(
          height: 160,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: [
              _buildExperienceCard(
                context,
                'Virtual Chemistry Lab',
                'Conduct experiments safely in VR',
                Symbols.science,
                FeatureColors.vrClassroom,
                'https://images.pexels.com/photos/2280549/pexels-photo-2280549.jpeg',
                () => _startARExperience(context),
              ),
              _buildExperienceCard(
                context,
                'AR Anatomy Explorer',
                'Explore human body in 3D',
                Symbols.medical_services,
                FeatureColors.arExperience,
                'https://images.pexels.com/photos/5726794/pexels-photo-5726794.jpeg',
                () => _startARExperience(context),
              ),
              _buildExperienceCard(
                context,
                'AI Physics Tutor',
                'Interactive problem solving',
                Symbols.calculate,
                FeatureColors.aiTutor,
                'https://images.pexels.com/photos/8197543/pexels-photo-8197543.jpeg',
                () => AppNavigation.goToAITutor(context),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildExperienceCard(
    BuildContext context,
    String title,
    String subtitle,
    IconData icon,
    Color color,
    String imageUrl,
    VoidCallback onTap,
  ) {
    return Container(
      width: 280,
      margin: const EdgeInsets.only(right: AppTheme.spacing4),
      child: AdaptiveCard(
        onTap: onTap,
        child: Stack(
          children: [
            // Background image
            ClipRRect(
              borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
              child: CachedNetworkImage(
                imageUrl: imageUrl,
                height: 160,
                width: 280,
                fit: BoxFit.cover,
                placeholder: (context, url) => const ShimmerLoading(),
              ),
            ),
            
            // Gradient overlay
            Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.transparent,
                    Colors.black.withOpacity(0.7),
                  ],
                ),
              ),
            ),
            
            // Content
            Positioned(
              bottom: AppTheme.spacing4,
              left: AppTheme.spacing4,
              right: AppTheme.spacing4,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.all(AppTheme.spacing2),
                    decoration: BoxDecoration(
                      color: color.withOpacity(0.9),
                      borderRadius: BorderRadius.circular(AppTheme.radiusSmall),
                    ),
                    child: Icon(
                      icon,
                      color: Colors.white,
                      size: 20,
                    ),
                  ),
                  const SizedBox(height: AppTheme.spacing2),
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    subtitle,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.white.withOpacity(0.9),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    ).animate().fadeIn(delay: 300.ms).scale(begin: const Offset(0.9, 0.9));
  }

  Widget _buildFeaturedCourses(BuildContext context, AsyncValue<List<dynamic>> featuredCourses) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Featured Courses',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            TextButton(
              onPressed: () => AppNavigation.goToCourse(context, 'featured'),
              child: const Text('View All'),
            ),
          ],
        ),
        const SizedBox(height: AppTheme.spacing4),
        
        featuredCourses.when(
          data: (courses) => GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: AppTheme.isMobile(context) ? 1 : 2,
              childAspectRatio: AppTheme.isMobile(context) ? 2.5 : 2.0,
              mainAxisSpacing: AppTheme.spacing4,
              crossAxisSpacing: AppTheme.spacing4,
            ),
            itemCount: courses.length.clamp(0, 4),
            itemBuilder: (context, index) {
              final course = courses[index];
              return _buildCourseCard(context, course, index);
            },
          ),
          loading: () => GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: AppTheme.isMobile(context) ? 1 : 2,
              childAspectRatio: AppTheme.isMobile(context) ? 2.5 : 2.0,
              mainAxisSpacing: AppTheme.spacing4,
              crossAxisSpacing: AppTheme.spacing4,
            ),
            itemCount: 4,
            itemBuilder: (context, index) => const ShimmerLoading(),
          ),
          error: (error, stack) => Center(
            child: Text('Error loading featured courses: $error'),
          ),
        ),
      ],
    );
  }

  Widget _buildCourseCard(BuildContext context, Map<String, dynamic> course, int index) {
    return AdaptiveCard(
      onTap: () => AppNavigation.goToCourse(context, course['id'] ?? ''),
      child: Row(
        children: [
          // Course thumbnail
          ClipRRect(
            borderRadius: BorderRadius.circular(AppTheme.radiusSmall),
            child: AspectRatio(
              aspectRatio: 16 / 9,
              child: CachedNetworkImage(
                imageUrl: course['thumbnail'] ?? 'https://images.pexels.com/photos/5212345/pexels-photo-5212345.jpeg',
                fit: BoxFit.cover,
                placeholder: (context, url) => const ShimmerLoading(),
              ),
            ),
          ),
          
          const SizedBox(width: AppTheme.spacing4),
          
          // Course info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  course['title'] ?? 'Course Title',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: AppTheme.spacing1),
                Text(
                  course['instructor'] ?? 'Instructor Name',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppTheme.textSecondary,
                  ),
                ),
                const SizedBox(height: AppTheme.spacing2),
                Row(
                  children: [
                    Icon(
                      Symbols.star,
                      size: 16,
                      color: AppTheme.warningColor,
                    ),
                    const SizedBox(width: AppTheme.spacing1),
                    Text(
                      '${course['rating'] ?? 4.5}',
                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(width: AppTheme.spacing2),
                    Icon(
                      Symbols.people,
                      size: 16,
                      color: AppTheme.textSecondary,
                    ),
                    const SizedBox(width: AppTheme.spacing1),
                    Text(
                      '${course['students'] ?? 1234}',
                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                        color: AppTheme.textSecondary,
                      ),
                    ),
                  ],
                ),
                if (course['hasVR'] == true || course['hasAR'] == true) ...[
                  const SizedBox(height: AppTheme.spacing2),
                  Row(
                    children: [
                      if (course['hasVR'] == true)
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: AppTheme.spacing2,
                            vertical: AppTheme.spacing1,
                          ),
                          decoration: BoxDecoration(
                            color: FeatureColors.vrClassroom.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(AppTheme.radiusSmall),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                Symbols.view_in_ar,
                                size: 12,
                                color: FeatureColors.vrClassroom,
                              ),
                              const SizedBox(width: AppTheme.spacing1),
                              Text(
                                'VR',
                                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                  color: FeatureColors.vrClassroom,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                        ),
                      if (course['hasAR'] == true) ...[
                        if (course['hasVR'] == true) const SizedBox(width: AppTheme.spacing2),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: AppTheme.spacing2,
                            vertical: AppTheme.spacing1,
                          ),
                          decoration: BoxDecoration(
                            color: FeatureColors.arExperience.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(AppTheme.radiusSmall),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                Symbols.camera,
                                size: 12,
                                color: FeatureColors.arExperience,
                              ),
                              const SizedBox(width: AppTheme.spacing1),
                              Text(
                                'AR',
                                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                  color: FeatureColors.arExperience,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ],
                  ),
                ],
              ],
            ),
          ),
        ),
      ],
    ),
    ).animate().fadeIn(delay: (index * 100 + 500).ms).slideY(begin: 0.1);
  }

  Widget _buildAIRecommendations(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(
              Symbols.psychology,
              color: FeatureColors.aiTutor,
              size: 24,
            ),
            const SizedBox(width: AppTheme.spacing2),
            Text(
              'AI Recommendations',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: AppTheme.spacing4),
        
        AdaptiveCard(
          child: Padding(
            padding: const EdgeInsets.all(AppTheme.spacing4),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(AppTheme.spacing2),
                      decoration: BoxDecoration(
                        color: FeatureColors.aiTutor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(AppTheme.radiusSmall),
                      ),
                      child: Icon(
                        Symbols.auto_awesome,
                        color: FeatureColors.aiTutor,
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: AppTheme.spacing3),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Personalized Learning Path',
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          Text(
                            'Based on your learning style and progress',
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: AppTheme.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: AppTheme.spacing4),
                Text(
                  'Our AI has analyzed your learning patterns and recommends focusing on interactive content with VR experiences. You learn best with visual and hands-on approaches.',
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                const SizedBox(height: AppTheme.spacing4),
                ElevatedButton.icon(
                  onPressed: () => AppNavigation.goToAITutor(context),
                  icon: const Icon(Symbols.psychology, size: 18),
                  label: const Text('Chat with AI Tutor'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: FeatureColors.aiTutor,
                  ),
                ),
              ],
            ),
          ),
        ).animate().fadeIn(delay: 600.ms).slideY(begin: 0.1),
      ],
    );
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  }

  void _showNotifications(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.7,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(
            top: Radius.circular(AppTheme.radiusLarge),
          ),
        ),
        child: Column(
          children: [
            Container(
              width: 40,
              height: 4,
              margin: const EdgeInsets.symmetric(vertical: AppTheme.spacing2),
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(AppTheme.spacing4),
              child: Row(
                children: [
                  Text(
                    'Notifications',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const Spacer(),
                  TextButton(
                    onPressed: () {},
                    child: const Text('Mark all read'),
                  ),
                ],
              ),
            ),
            const Expanded(
              child: Center(
                child: Text('No new notifications'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _joinVRClassroom(BuildContext context) {
    // Show VR classroom selection dialog
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Join VR Classroom'),
        content: const Text('Select a VR classroom to join:'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              AppNavigation.goToVRClassroom(context, 'demo-room');
            },
            child: const Text('Join Demo Room'),
          ),
        ],
      ),
    );
  }

  void _joinLiveClass(BuildContext context) {
    // Show live classes
    AppNavigation.goToLiveClass(context, 'live-demo');
  }

  void _startARExperience(BuildContext context) {
    // Start AR experience
    AppNavigation.goToARExperience(context, 'chemistry-lab');
  }
}

// Providers for home screen data
final featuredCoursesProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  // Mock data - in production, fetch from API
  await Future.delayed(const Duration(seconds: 1));
  
  return [
    {
      'id': '1',
      'title': 'Advanced Machine Learning with VR Visualization',
      'instructor': 'Dr. Sarah Chen',
      'thumbnail': 'https://images.pexels.com/photos/8386440/pexels-photo-8386440.jpeg',
      'rating': 4.8,
      'students': 15420,
      'hasVR': true,
      'hasAR': false,
    },
    {
      'id': '2',
      'title': 'Interactive Chemistry Lab in AR',
      'instructor': 'Prof. Michael Rodriguez',
      'thumbnail': 'https://images.pexels.com/photos/2280549/pexels-photo-2280549.jpeg',
      'rating': 4.9,
      'students': 8930,
      'hasVR': false,
      'hasAR': true,
    },
    {
      'id': '3',
      'title': 'AI-Powered Data Science Bootcamp',
      'instructor': 'AI Tutor Emma',
      'thumbnail': 'https://images.pexels.com/photos/8386440/pexels-photo-8386440.jpeg',
      'rating': 4.7,
      'students': 23450,
      'hasVR': true,
      'hasAR': true,
    },
    {
      'id': '4',
      'title': 'Virtual Physics Laboratory',
      'instructor': 'Dr. James Wilson',
      'thumbnail': 'https://images.pexels.com/photos/8197543/pexels-photo-8197543.jpeg',
      'rating': 4.6,
      'students': 12100,
      'hasVR': true,
      'hasAR': false,
    },
  ];
});

final continuelearningProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  // Mock data - in production, fetch from API
  await Future.delayed(const Duration(milliseconds: 800));
  
  return [
    {
      'id': '1',
      'title': 'Python for Data Science',
      'thumbnail': 'https://images.pexels.com/photos/1181671/pexels-photo-1181671.jpeg',
      'progress': 65,
      'nextLesson': 'Pandas DataFrames',
      'timeLeft': 25,
    },
    {
      'id': '2',
      'title': 'VR Game Development',
      'thumbnail': 'https://images.pexels.com/photos/7915437/pexels-photo-7915437.jpeg',
      'progress': 30,
      'nextLesson': 'Unity VR Setup',
      'timeLeft': 45,
    },
    {
      'id': '3',
      'title': 'AI Ethics and Society',
      'thumbnail': 'https://images.pexels.com/photos/8386440/pexels-photo-8386440.jpeg',
      'progress': 80,
      'nextLesson': 'Final Project',
      'timeLeft': 15,
    },
  ];
});