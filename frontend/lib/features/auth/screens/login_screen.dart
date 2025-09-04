import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:material_symbols_icons/symbols.dart';
import 'package:local_auth/local_auth.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/router/app_router.dart';
import '../../../shared/widgets/adaptive_card.dart';
import '../../../shared/widgets/loading_button.dart';
import '../../../shared/widgets/social_login_button.dart';
import '../providers/auth_provider.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen>
    with TickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;
  
  bool _obscurePassword = true;
  bool _rememberMe = false;
  bool _isLoading = false;
  
  final LocalAuthentication _localAuth = LocalAuthentication();

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: const Interval(0.0, 0.6, curve: Curves.easeOut),
    ));
    
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: const Interval(0.2, 1.0, curve: Curves.easeOutCubic),
    ));
    
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(AppTheme.spacing4),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 400),
              child: FadeTransition(
                opacity: _fadeAnimation,
                child: SlideTransition(
                  position: _slideAnimation,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Logo and welcome
                      _buildHeader(context),
                      const SizedBox(height: AppTheme.spacing8),
                      
                      // Login form
                      _buildLoginForm(context, authState),
                      const SizedBox(height: AppTheme.spacing6),
                      
                      // Biometric login
                      _buildBiometricLogin(context),
                      const SizedBox(height: AppTheme.spacing6),
                      
                      // Social login
                      _buildSocialLogin(context),
                      const SizedBox(height: AppTheme.spacing6),
                      
                      // Register link
                      _buildRegisterLink(context),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Column(
      children: [
        // App logo with gradient background
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            gradient: AppTheme.primaryGradient,
            borderRadius: BorderRadius.circular(AppTheme.radiusLarge),
            boxShadow: [
              BoxShadow(
                color: AppTheme.primaryColor.withOpacity(0.3),
                blurRadius: 20,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: const Icon(
            Symbols.school,
            color: Colors.white,
            size: 40,
          ),
        ).animate().scale(delay: 200.ms, duration: 600.ms, curve: Curves.elasticOut),
        
        const SizedBox(height: AppTheme.spacing4),
        
        Text(
          'Welcome Back',
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: AppTheme.textPrimary,
          ),
        ).animate().fadeIn(delay: 400.ms).slideY(begin: 0.2),
        
        const SizedBox(height: AppTheme.spacing2),
        
        Text(
          'Sign in to continue your learning journey',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: AppTheme.textSecondary,
          ),
          textAlign: TextAlign.center,
        ).animate().fadeIn(delay: 500.ms),
      ],
    );
  }

  Widget _buildLoginForm(BuildContext context, AuthState authState) {
    return AdaptiveCard(
      child: Padding(
        padding: const EdgeInsets.all(AppTheme.spacing6),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Email field
              TextFormField(
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
                textInputAction: TextInputAction.next,
                decoration: InputDecoration(
                  labelText: 'Email',
                  hintText: 'Enter your email address',
                  prefixIcon: const Icon(Symbols.email),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
                  ),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter your email';
                  }
                  if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
                    return 'Please enter a valid email';
                  }
                  return null;
                },
              ).animate().fadeIn(delay: 600.ms).slideX(begin: -0.1),
              
              const SizedBox(height: AppTheme.spacing4),
              
              // Password field
              TextFormField(
                controller: _passwordController,
                obscureText: _obscurePassword,
                textInputAction: TextInputAction.done,
                decoration: InputDecoration(
                  labelText: 'Password',
                  hintText: 'Enter your password',
                  prefixIcon: const Icon(Symbols.lock),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscurePassword ? Symbols.visibility : Symbols.visibility_off,
                    ),
                    onPressed: () {
                      setState(() {
                        _obscurePassword = !_obscurePassword;
                      });
                    },
                  ),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
                  ),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter your password';
                  }
                  return null;
                },
                onFieldSubmitted: (_) => _handleLogin(),
              ).animate().fadeIn(delay: 700.ms).slideX(begin: -0.1),
              
              const SizedBox(height: AppTheme.spacing4),
              
              // Remember me and forgot password
              Row(
                children: [
                  Checkbox(
                    value: _rememberMe,
                    onChanged: (value) {
                      setState(() {
                        _rememberMe = value ?? false;
                      });
                    },
                  ),
                  Text(
                    'Remember me',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const Spacer(),
                  TextButton(
                    onPressed: () => AppNavigation.goToRegister(context),
                    child: const Text('Forgot Password?'),
                  ),
                ],
              ).animate().fadeIn(delay: 800.ms),
              
              const SizedBox(height: AppTheme.spacing6),
              
              // Login button
              LoadingButton(
                onPressed: _handleLogin,
                isLoading: _isLoading || authState.isLoading,
                child: const Text('Sign In'),
              ).animate().fadeIn(delay: 900.ms).slideY(begin: 0.1),
              
              if (authState.error != null) ...[
                const SizedBox(height: AppTheme.spacing4),
                Container(
                  padding: const EdgeInsets.all(AppTheme.spacing3),
                  decoration: BoxDecoration(
                    color: AppTheme.errorColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(AppTheme.radiusSmall),
                    border: Border.all(
                      color: AppTheme.errorColor.withOpacity(0.3),
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Symbols.error,
                        color: AppTheme.errorColor,
                        size: 20,
                      ),
                      const SizedBox(width: AppTheme.spacing2),
                      Expanded(
                        child: Text(
                          authState.error!,
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: AppTheme.errorColor,
                          ),
                        ),
                      ),
                    ],
                  ),
                ).animate().shake(),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBiometricLogin(BuildContext context) {
    return FutureBuilder<bool>(
      future: _localAuth.canCheckBiometrics,
      builder: (context, snapshot) {
        if (snapshot.data != true) return const SizedBox.shrink();
        
        return Column(
          children: [
            Row(
              children: [
                Expanded(child: Divider(color: Colors.grey.shade300)),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: AppTheme.spacing4),
                  child: Text(
                    'or',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppTheme.textSecondary,
                    ),
                  ),
                ),
                Expanded(child: Divider(color: Colors.grey.shade300)),
              ],
            ),
            const SizedBox(height: AppTheme.spacing4),
            
            OutlinedButton.icon(
              onPressed: _handleBiometricLogin,
              icon: const Icon(Symbols.fingerprint),
              label: const Text('Use Biometric Login'),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(
                  horizontal: AppTheme.spacing6,
                  vertical: AppTheme.spacing4,
                ),
              ),
            ).animate().fadeIn(delay: 1000.ms).scale(begin: const Offset(0.9, 0.9)),
          ],
        );
      },
    );
  }

  Widget _buildSocialLogin(BuildContext context) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(child: Divider(color: Colors.grey.shade300)),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: AppTheme.spacing4),
              child: Text(
                'or continue with',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppTheme.textSecondary,
                ),
              ),
            ),
            Expanded(child: Divider(color: Colors.grey.shade300)),
          ],
        ),
        const SizedBox(height: AppTheme.spacing4),
        
        Row(
          children: [
            Expanded(
              child: SocialLoginButton(
                provider: 'Google',
                icon: Symbols.login,
                onPressed: () => _handleSocialLogin('google'),
              ).animate().fadeIn(delay: 1100.ms).slideX(begin: -0.1),
            ),
            const SizedBox(width: AppTheme.spacing3),
            Expanded(
              child: SocialLoginButton(
                provider: 'Microsoft',
                icon: Symbols.business,
                onPressed: () => _handleSocialLogin('microsoft'),
              ).animate().fadeIn(delay: 1200.ms).slideX(begin: 0.1),
            ),
          ],
        ),
        const SizedBox(height: AppTheme.spacing3),
        
        SocialLoginButton(
          provider: 'Apple',
          icon: Symbols.phone_iphone,
          onPressed: () => _handleSocialLogin('apple'),
          isFullWidth: true,
        ).animate().fadeIn(delay: 1300.ms).slideY(begin: 0.1),
      ],
    );
  }

  Widget _buildRegisterLink(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          "Don't have an account? ",
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: AppTheme.textSecondary,
          ),
        ),
        TextButton(
          onPressed: () => AppNavigation.goToRegister(context),
          child: const Text(
            'Sign Up',
            style: TextStyle(fontWeight: FontWeight.w600),
          ),
        ),
      ],
    ).animate().fadeIn(delay: 1400.ms);
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;
    
    setState(() => _isLoading = true);
    
    try {
      await ref.read(authProvider.notifier).login(
        email: _emailController.text.trim(),
        password: _passwordController.text,
        rememberMe: _rememberMe,
      );
      
      if (mounted) {
        AppNavigation.goToHome(context);
      }
    } catch (e) {
      // Error is handled by the provider
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _handleBiometricLogin() async {
    try {
      final bool didAuthenticate = await _localAuth.authenticate(
        localizedReason: 'Please authenticate to sign in to EduVerse',
        options: const AuthenticationOptions(
          biometricOnly: true,
          stickyAuth: true,
        ),
      );
      
      if (didAuthenticate) {
        // In production, use stored credentials or passkey
        await ref.read(authProvider.notifier).loginWithBiometric();
        
        if (mounted) {
          AppNavigation.goToHome(context);
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Biometric authentication failed: $e'),
            backgroundColor: AppTheme.errorColor,
          ),
        );
      }
    }
  }

  Future<void> _handleSocialLogin(String provider) async {
    try {
      await ref.read(authProvider.notifier).loginWithOAuth(provider);
      
      if (mounted) {
        AppNavigation.goToHome(context);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('$provider login failed: $e'),
            backgroundColor: AppTheme.errorColor,
          ),
        );
      }
    }
  }
}