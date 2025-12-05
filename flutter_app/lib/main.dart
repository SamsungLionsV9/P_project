import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:responsive_framework/responsive_framework.dart';
import 'car_info_input_page.dart';
import 'mypage.dart';
import 'settings_page.dart';
import 'recommendation_page.dart';
import 'comparison_page.dart';
import 'oauth_webview_page.dart';
import 'signup_page.dart';
import 'forgot_password_page.dart';
import 'services/auth_service.dart';
import 'services/api_service.dart';
import 'theme/theme_provider.dart';
import 'providers/comparison_provider.dart';
import 'providers/recent_views_provider.dart';
import 'providers/popular_cars_provider.dart';
import 'widgets/deal_analysis_modal.dart';
import 'widgets/model_deals_modal.dart';
import 'widgets/common/bottom_nav_bar.dart';
import 'widgets/market_trend_card.dart';
import 'widgets/ai_pick_card.dart';
import 'widgets/professional_timing_card.dart';
import 'utils/car_image_mapper.dart';
import 'package:percent_indicator/circular_percent_indicator.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // 저장된 토큰 로드
  final authService = AuthService();
  await authService.loadSavedToken();
  
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
        ChangeNotifierProvider(create: (_) => ComparisonProvider()),
        ChangeNotifierProvider(create: (_) {
          final provider = RecentViewsProvider();
          provider.loadRecentViews();
          return provider;
        }),
        ChangeNotifierProvider(create: (_) {
          final provider = PopularCarsProvider();
          provider.loadData();
          return provider;
        }),
      ],
      child: const CarPriceApp(),
    ),
  );
}

class CarPriceApp extends StatelessWidget {
  const CarPriceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ScreenUtilInit(
      // 디자인 기준 사이즈 (일반적인 모바일 기준)
      designSize: const Size(390, 844),
      minTextAdapt: true,
      splitScreenMode: true,
      builder: (context, child) {
        return Consumer<ThemeProvider>(
          builder: (context, themeProvider, child) {
            return MaterialApp(
              title: '언제 살까?',  // 차별화: 시세가 아닌 타이밍
              debugShowCheckedModeBanner: false,
              themeMode: themeProvider.themeMode,
              // 반응형 브레이크포인트 설정
              builder: (context, child) => ResponsiveBreakpoints.builder(
                child: child!,
                breakpoints: [
                  const Breakpoint(start: 0, end: 450, name: MOBILE),
                  const Breakpoint(start: 451, end: 800, name: TABLET),
                  const Breakpoint(start: 801, end: 1920, name: DESKTOP),
                  const Breakpoint(start: 1921, end: double.infinity, name: '4K'),
                ],
              ),
              // 라이트 테마 정의
              theme: ThemeData(
                brightness: Brightness.light,
                primaryColor: const Color(0xFF0066FF),
                scaffoldBackgroundColor: const Color(0xFFF5F7FA),
                fontFamily: 'Pretendard',
                useMaterial3: true,
                appBarTheme: const AppBarTheme(
                  backgroundColor: Color(0xFFF5F7FA),
                  foregroundColor: Colors.black,
                ),
              ),
              // 다크 테마 정의
              darkTheme: ThemeData(
                brightness: Brightness.dark,
                primaryColor: const Color(0xFF0066FF),
                scaffoldBackgroundColor: const Color(0xFF121212),
                fontFamily: 'Pretendard',
                useMaterial3: true,
                appBarTheme: const AppBarTheme(
                  backgroundColor: Color(0xFF121212),
                  foregroundColor: Colors.white,
                ),
              ),
              home: const MainScreen(),
            );
          },
        );
      },
    );
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;
  final GlobalKey _myPageKey = GlobalKey();

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }
  
  // 로그인 상태 변경 시 MyPage 업데이트
  void _refreshMyPage() {
    setState(() {
      // IndexedStack을 재빌드하여 MyPage도 재빌드되도록 함
    });
  }

  @override
  Widget build(BuildContext context) {
    final themeProvider = Provider.of<ThemeProvider>(context);
    final isDark = themeProvider.isDarkMode;
    final navBgColor = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final unselectedItemColor = isDark ? Colors.grey[600] : Colors.grey[400];

    // 페이지 리스트 (빌드 시점에 생성)
    final pages = [
      HomePageContent(
        onNavigateToSearch: () => _onItemTapped(1),
        onLoginSuccess: _refreshMyPage,
      ),
      const CarInfoInputPage(),
      const RecommendationPage(),
      MyPage(key: _myPageKey),
      const SettingsPage(),
    ];

    // MainScreenNavigator로 감싸서 하위 화면에서도 탭 전환 가능
    return MainScreenNavigator(
      switchTab: _onItemTapped,
      child: Scaffold(
        body: IndexedStack(
          index: _selectedIndex,
          children: pages,
        ),
        bottomNavigationBar: Container(
          decoration: BoxDecoration(
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.05),
                blurRadius: 10,
                offset: const Offset(0, -5),
              ),
            ],
          ),
          child: BottomNavigationBar(
            backgroundColor: navBgColor,
            type: BottomNavigationBarType.fixed,
            currentIndex: _selectedIndex,
            selectedItemColor: const Color(0xFF0066FF),
            unselectedItemColor: unselectedItemColor,
            selectedFontSize: 12,
            unselectedFontSize: 12,
            onTap: _onItemTapped,
            elevation: 0,
            items: const [
              BottomNavigationBarItem(
                icon: Icon(Icons.home_outlined),
                activeIcon: Icon(Icons.home),
                label: '홈',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.search),
                activeIcon: Icon(Icons.search),
                label: '내 차 찾기',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.recommend_outlined),
                activeIcon: Icon(Icons.recommend),
                label: '추천',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.person_outline),
                activeIcon: Icon(Icons.person),
                label: '마이',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.settings_outlined),
                activeIcon: Icon(Icons.settings),
                label: '설정',
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class HomePageContent extends StatefulWidget {
  final VoidCallback? onNavigateToSearch;
  final VoidCallback? onLoginSuccess;

  const HomePageContent({super.key, this.onNavigateToSearch, this.onLoginSuccess});

  @override
  State<HomePageContent> createState() => _HomePageContentState();
}

class _HomePageContentState extends State<HomePageContent> {
  final AuthService _authService = AuthService();
  final ApiService _apiService = ApiService();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  bool _isLoading = false;
  bool _isLoggedIn = false;
  
  // 차별화: 시장 타이밍 상태
  MarketTimingResult? _marketTiming;
  bool _isLoadingTiming = true;

  @override
  void initState() {
    super.initState();
    _isLoggedIn = _authService.isLoggedIn;
    _loadMarketTiming();
  }

  /// 시장 타이밍 데이터 로드 (차별화 포인트)
  Future<void> _loadMarketTiming() async {
    try {
      final timing = await _apiService.getMarketTiming();
      if (mounted) {
        setState(() {
          _marketTiming = timing;
          _isLoadingTiming = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _marketTiming = MarketTimingResult.defaultValue();
          _isLoadingTiming = false;
        });
      }
    }
  }

  /// 로그인 상태 확인
  Future<void> _checkLoginStatus() async {
    final isLoggedIn = _authService.isLoggedIn;
    if (mounted) {
      setState(() {
        _isLoggedIn = isLoggedIn;
      });
    }
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  /// 이메일/비밀번호 로그인
  Future<void> _login() async {
    if (_emailController.text.isEmpty || _passwordController.text.isEmpty) {
      _showMessage('이메일과 비밀번호를 입력하세요', isError: true);
      return;
    }

    setState(() => _isLoading = true);

    final result = await _authService.login(
      _emailController.text.trim(),
      _passwordController.text,
    );

    setState(() => _isLoading = false);

    if (result['success'] == true) {
      setState(() => _isLoggedIn = true);
      _emailController.clear();
      _passwordController.clear();
      // 로그인 성공 시 모달 닫기
      if (mounted) {
        Navigator.pop(context);
        _showMessage('로그인 성공!');
      }
      // MyPage 업데이트
      widget.onLoginSuccess?.call();
    } else {
      _showMessage(result['message'] ?? '로그인 실패', isError: true);
    }
  }

  /// 소셜 로그인
  Future<void> _socialLogin(String provider) async {
    // 네이버는 WebView를 차단하므로 외부 브라우저 사용
    if (provider == 'naver') {
      final url = _authService.getSocialLoginUrl(provider);
      _showMessage('네이버 로그인은 외부 브라우저에서 진행됩니다.\n(에뮬레이터에서는 제한될 수 있습니다)');
      
      try {
        final uri = Uri.parse(url);
        if (await canLaunchUrl(uri)) {
          await launchUrl(uri, mode: LaunchMode.externalApplication);
        } else {
          _showMessage('브라우저를 열 수 없습니다', isError: true);
        }
      } catch (e) {
        _showMessage('네이버 로그인 오류: $e', isError: true);
      }
      return;
    }
    
    // 카카오, 구글은 WebView 사용
    final result = await Navigator.push<Map<String, dynamic>>(
      context,
      MaterialPageRoute(
        builder: (context) => OAuthWebViewPage(provider: provider),
      ),
    );

    if (result != null && result['success'] == true) {
      setState(() => _isLoggedIn = true);
      // 로그인 성공 시 모달 닫기
      if (mounted) {
        Navigator.pop(context);
        _showMessage('${_getProviderName(provider)} 로그인 성공!');
      }
      // MyPage 업데이트
      widget.onLoginSuccess?.call();
    }
  }

  String _getProviderName(String provider) {
    switch (provider) {
      case 'naver': return '네이버';
      case 'kakao': return '카카오';
      case 'google': return 'Google';
      default: return provider;
    }
  }

  /// 회원가입 페이지로 이동

  /// 로그인 바텀시트 표시
  void _showLoginBottomSheet() {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor = isDark ? Colors.white : Colors.black87;
    
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.85,
        decoration: BoxDecoration(
          color: isDark ? const Color(0xFF1E1E1E) : Colors.white,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  margin: const EdgeInsets.only(bottom: 20),
                  decoration: BoxDecoration(
                    color: Colors.grey[400],
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              _buildLoginForm(isDark, textColor),
            ],
          ),
        ),
      ),
    );
  }

  void _navigateToSignup() async {
    final result = await Navigator.push<bool>(
      context,
      MaterialPageRoute(builder: (context) => const SignupPage()),
    );
    
    if (result == true) {
      _showMessage('회원가입이 완료되었습니다. 로그인하세요!');
    }
  }

  /// 로그아웃
  Future<void> _logout() async {
    await _authService.logout();
    
    // 로컬 상태 초기화
    try {
      // 최근 조회 목록 초기화
      if (mounted) {
        context.read<RecentViewsProvider>().clearAll();
      }
    } catch (e) {
      debugPrint('최근 조회 목록 초기화 실패: $e');
    }
    
    setState(() => _isLoggedIn = false);
    _showMessage('로그아웃되었습니다');
  }

  void _showMessage(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red : Colors.green,
      ),
    );
  }

  /// AI 추천 픽 상세 모달 표시
  void _showAiPickDetails() {
    final recentViewsProvider = context.read<RecentViewsProvider>();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => ModelDealsModal(
        brand: "현대",
        model: "그랜저",
        avgPrice: 2450,
        medianPrice: 2380,
        listings: 1240,
        onCarViewed: (viewedCar) {
          recentViewsProvider.addRecentCar(viewedCar);
        },
      ),
    );
  }

  /// Hero Section (GitHub 스타일 - 언제 살까? 테마)
  Widget _buildHeroSection(bool isDark) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(24, 40, 24, 40),
      decoration: const BoxDecoration(
        color: Color(0xFF001F3F), // 딥 블루 배경
        borderRadius: BorderRadius.only(
          bottomLeft: Radius.circular(32),
          bottomRight: Radius.circular(32),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "AI 기반 중고차 구매 타이밍 분석",
            style: TextStyle(
              color: Color(0xFF4DA8DA),
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.0,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            "언제 살까?\n지금이 적기인지 확인하세요",
            style: TextStyle(
              color: Colors.white,
              fontSize: 26,
              fontWeight: FontWeight.bold,
              height: 1.3,
            ),
          ),
          const SizedBox(height: 32),

          // 시세 조회 버튼
          SizedBox(
            width: double.infinity,
            height: 56,
            child: ElevatedButton(
              onPressed: () => widget.onNavigateToSearch?.call(),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0066FF),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                elevation: 8,
                shadowColor: const Color(0xFF0066FF).withOpacity(0.5),
              ),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    "구매 타이밍 분석하기",
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(width: 8),
                  Icon(Icons.arrow_forward_rounded),
                ],
              ),
            ),
          ),

          const SizedBox(height: 32),

          // 로그인 상태에 따른 UI
          if (!_isLoggedIn)
            Center(
              child: Column(
                children: [
                  Text(
                    "로그인하고 맞춤 알림을 받아보세요!",
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.7),
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 8),
                  OutlinedButton(
                    onPressed: _showLoginBottomSheet,
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.white,
                      side: const BorderSide(color: Colors.white, width: 1),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(30),
                      ),
                      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                    ),
                    child: const Text(
                      "로그인 / 회원가입",
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                    ),
                  ),
                ],
              ),
            )
          else
            Center(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    "${_authService.userEmail ?? '사용자'}님",
                    style: const TextStyle(color: Colors.white, fontSize: 14),
                  ),
                  const SizedBox(width: 8),
                  TextButton(
                    onPressed: _logout,
                    style: TextButton.styleFrom(foregroundColor: Colors.white70),
                    child: const Text('로그아웃', style: TextStyle(fontSize: 12)),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardColor = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final textColor = isDark ? Colors.white : Colors.black87;

    return SafeArea(
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1. Hero Section (GitHub 스타일 - 언제 살까? 테마)
            _buildHeroSection(isDark),

            const SizedBox(height: 24),

            // 2.  차별화: 오늘의 구매 타이밍 (핵심 강조)
            // ★ 전문적인 타이밍 카드 (고도화)
            ProfessionalTimingCard(
              timing: _marketTiming ?? MarketTimingResult.defaultValue(),
              isLoading: _isLoadingTiming,
              onTap: () => widget.onNavigateToSearch?.call(),
            ),

            const SizedBox(height: 32),

            // 3. 최근 조회 차량 섹션 (Provider 연동)
            _buildSectionTitle("최근 조회 차량", textColor),
            const SizedBox(height: 12),
            _buildRecentViewsList(isDark: isDark),

            const SizedBox(height: 32),

            // 4. 인기 모델 추천 섹션 (Provider 연동)
            _buildSectionTitle("인기 모델 추천", textColor),
            const SizedBox(height: 12),
            _buildPopularCarsList(isDark: isDark),

            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  /// 로그인된 상태 뷰
  Widget _buildLoggedInView(Color textColor) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            CircleAvatar(
              radius: 30,
              backgroundColor: const Color(0xFF0066FF).withOpacity(0.1),
              child: const Icon(Icons.person, size: 30, color: Color(0xFF0066FF)),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '환영합니다!',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: textColor),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _authService.userEmail ?? '사용자',
                    style: TextStyle(fontSize: 14, color: Colors.grey[500]),
                  ),
                  Text(
                    _authService.provider != null ? '(${_getProviderName(_authService.provider!)} 로그인)' : '',
                    style: TextStyle(fontSize: 12, color: Colors.grey[400]),
                  ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 20),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton(
            onPressed: _logout,
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.red,
              side: const BorderSide(color: Colors.red),
            ),
            child: const Text('로그아웃'),
          ),
        ),
      ],
    );
  }

  /// 로그인 폼
  Widget _buildLoginForm(bool isDark, Color textColor) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 브랜드 강조: 차별화된 가치 제안
        Text(
          "언제 살까?",
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: const Color(0xFF0066FF),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          "경제지표 기반 구매 타이밍 어드바이저",
          style: TextStyle(
            fontSize: 13,
            color: Colors.grey[500],
          ),
        ),
        const SizedBox(height: 20),
        
        // 이메일 입력
        _buildTextField(
          controller: _emailController,
          hintText: "이메일",
          isDark: isDark,
        ),
        const SizedBox(height: 12),
        
        // 비밀번호 입력
        _buildTextField(
          controller: _passwordController,
          hintText: "비밀번호",
          obscureText: true,
          isDark: isDark,
        ),
        const SizedBox(height: 8),
        
        // 비밀번호 재설정 링크
        Align(
          alignment: Alignment.centerRight,
          child: TextButton(
            onPressed: () async {
              final result = await Navigator.push<bool>(
                context,
                MaterialPageRoute(builder: (context) => const ForgotPasswordPage()),
              );
              if (result == true) {
                _showMessage('비밀번호가 재설정되었습니다. 새 비밀번호로 로그인하세요.');
              }
            },
            style: TextButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              minimumSize: Size.zero,
              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
            ),
            child: const Text(
              "비밀번호 재설정",
              style: TextStyle(
                color: Color(0xFF0066FF),
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ),
        const SizedBox(height: 20),

        // 로그인 버튼
        SizedBox(
          width: double.infinity,
          height: 52,
          child: ElevatedButton(
            onPressed: _isLoading ? null : _login,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0066FF),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              elevation: 0,
            ),
            child: _isLoading
              ? const SizedBox(
                  width: 24, height: 24,
                  child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                )
              : const Text(
                  "로그인",
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                ),
          ),
        ),
        const SizedBox(height: 20),

        // 소셜 로그인 버튼들
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _buildSocialButton("N", const Color(0xFF03C75A), Colors.white, provider: 'naver'),
            const SizedBox(width: 16),
            _buildSocialButton("K", const Color(0xFFFEE500), const Color(0xFF3C1E1E), provider: 'kakao'),
            const SizedBox(width: 16),
            _buildSocialButton("G", Colors.white, Colors.grey, isBorder: true, provider: 'google'),
          ],
        ),
        const SizedBox(height: 20),

        // 회원가입 링크
        Center(
          child: GestureDetector(
            onTap: _navigateToSignup,
            child: const Text(
              "회원가입",
              style: TextStyle(
                color: Color(0xFF0066FF),
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ),
      ],
    );
  }

  // Helper Widget: 텍스트 필드
  Widget _buildTextField({
    required String hintText,
    bool obscureText = false,
    required bool isDark,
    TextEditingController? controller,
  }) {
    return Container(
      height: 50,
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF2C2C2C) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: isDark ? Colors.grey[700]! : Colors.grey[300]!),
      ),
      child: TextField(
        controller: controller,
        obscureText: obscureText,
        style: TextStyle(color: isDark ? Colors.white : Colors.black),
        decoration: InputDecoration(
          hintText: hintText,
          hintStyle: TextStyle(color: Colors.grey[400], fontSize: 14),
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(horizontal: 16),
        ),
      ),
    );
  }

  // Helper Widget: 소셜 로그인 버튼
  Widget _buildSocialButton(String text, Color bgColor, Color textColor, {bool isBorder = false, String? provider}) {
    return GestureDetector(
      onTap: provider != null ? () => _socialLogin(provider) : null,
      child: Container(
        width: 48,
        height: 48,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: bgColor,
          border: isBorder ? Border.all(color: Colors.grey[300]!) : null,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Center(
          child: Text(
            text,
            style: TextStyle(
              color: textColor,
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),
        ),
      ),
    );
  }

  // ★ 차별화 위젯: 오늘의 구매 타이밍 카드
  Widget _buildMarketTimingCard(bool isDark, Color cardColor, Color textColor) {
    if (_isLoadingTiming) {
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        child: Container(
          width: double.infinity,
          height: 140,
          decoration: BoxDecoration(
            color: cardColor,
            borderRadius: BorderRadius.circular(20),
          ),
          child: const Center(child: CircularProgressIndicator()),
        ),
      );
    }

    final timing = _marketTiming ?? MarketTimingResult.defaultValue();
    final scoreColor = timing.getScoreColor();

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.white,
              scoreColor.withOpacity(0.08),
            ],
          ),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: scoreColor.withOpacity(0.2), width: 1.5),
          boxShadow: [
            BoxShadow(
              color: scoreColor.withOpacity(0.15),
              blurRadius: 20,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 헤더
            Row(
              children: [
                Icon(Icons.access_time_filled, color: scoreColor, size: 20),
                const SizedBox(width: 8),
                Text(
                  "오늘의 구매 타이밍",
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: textColor.withOpacity(0.7),
                  ),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: scoreColor.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    timing.label,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: scoreColor,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            // 점수 표시
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  "${timing.score.toInt()}",
                  style: TextStyle(
                    fontSize: 48,
                    fontWeight: FontWeight.bold,
                    color: scoreColor,
                    height: 1,
                  ),
                ),
                const SizedBox(width: 4),
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Text(
                    "/ 100",
                    style: TextStyle(
                      fontSize: 16,
                      color: textColor.withOpacity(0.5),
                    ),
                  ),
                ),
                const Spacer(),
                // 경제지표 요약
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: timing.indicators.take(3).map((indicator) {
                    final status = indicator['status'] as String;
                    final icon = status == 'positive' 
                        ? Icons.arrow_upward 
                        : status == 'negative' 
                            ? Icons.arrow_downward 
                            : Icons.remove;
                    final color = status == 'positive' 
                        ? Colors.green 
                        : status == 'negative' 
                            ? Colors.red 
                            : Colors.grey;
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 2),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            indicator['name'] as String,
                            style: TextStyle(
                              fontSize: 11,
                              color: textColor.withOpacity(0.6),
                            ),
                          ),
                          const SizedBox(width: 4),
                          Icon(icon, size: 12, color: color),
                        ],
                      ),
                    );
                  }).toList(),
                ),
              ],
            ),
            const SizedBox(height: 12),
            // 한 줄 요약
            Text(
              timing.action,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: textColor,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // Helper Widget: 섹션 타이틀
  Widget _buildSectionTitle(String title, Color textColor) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: textColor,
            ),
          ),
          const Icon(Icons.arrow_forward, size: 20, color: Colors.grey),
        ],
      ),
    );
  }

  // 최근 조회 차량 리스트 (Provider 연동)
  Widget _buildRecentViewsList({required bool isDark}) {
    return Consumer<RecentViewsProvider>(
      builder: (context, provider, child) {
        if (provider.isLoading && provider.recentViewedCars.isEmpty) {
          return const SizedBox(
            height: 190,
            child: Center(child: CircularProgressIndicator()),
          );
        }
        
        if (provider.recentViewedCars.isEmpty) {
          return SizedBox(
            height: 190,
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.history, size: 48, color: Colors.grey[400]),
                  const SizedBox(height: 8),
                  Text(
                    '최근 조회한 차량이 없습니다',
                    style: TextStyle(color: Colors.grey[500], fontSize: 14),
                  ),
                ],
              ),
            ),
          );
        }
        
        return SizedBox(
          height: 190,
          child: ListView.separated(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            scrollDirection: Axis.horizontal,
            itemCount: provider.recentViewedCars.length,
            separatorBuilder: (context, index) => const SizedBox(width: 12),
            itemBuilder: (context, index) {
              final car = provider.recentViewedCars[index];
              // RecommendedCar 모델에서 CarCard 형식으로 변환
              final displayColor = car.isGoodDeal ? Colors.green : Colors.blue;
              return CarCard(
                name: '${car.brand} ${car.model}',
                info: '${car.year}년 · ${car.formattedMileage}',
                price: '${car.actualPrice}만원',
                color: displayColor,
                isDark: isDark,
                onTap: () => _showRecentCarDetail(car),
              );
            },
          ),
        );
      },
    );
  }
  
  /// 최근 조회 차량 클릭 시 상세 분석 모달 표시
  void _showRecentCarDetail(RecommendedCar car) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DealAnalysisModal(
        deal: car,
        predictedPrice: car.predictedPrice,
      ),
    );
  }

  /// 인기 모델 클릭 시 해당 모델의 실매물 모달 표시
  void _showPopularModelDeals(PopularCar car) {
    // 최근 조회 Provider (모달에서 매물 클릭 시 기록 추가용)
    final recentViewsProvider = context.read<RecentViewsProvider>();
    
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => ModelDealsModal(
        brand: car.brand,
        model: car.model,
        avgPrice: car.avgPrice,
        medianPrice: car.medianPrice,
        listings: car.listings,
        onCarViewed: (viewedCar) {
          recentViewsProvider.addRecentCar(viewedCar);
        },
      ),
    );
  }

  // 매물 수 포맷팅 (직접적인 대수 대신 친근한 표현)
  String _formatListingsCount(int count) {
    if (count >= 3000) {
      return '인기 🔥';
    } else if (count >= 2000) {
      return '많은 매물';
    } else if (count >= 1000) {
      return '적당한 매물';
    } else if (count >= 500) {
      return '희소 매물';
    } else {
      return '레어 ✨';
    }
  }
  
  // 인기 모델 추천 리스트 (Provider 연동)
  Widget _buildPopularCarsList({required bool isDark}) {
    return Consumer<PopularCarsProvider>(
      builder: (context, provider, child) {
        if (provider.isLoading && provider.topDomestic.isEmpty) {
          return const SizedBox(
            height: 190,
            child: Center(child: CircularProgressIndicator()),
          );
        }
        
        // 국산차와 수입차 합쳐서 표시
        final allCars = [...provider.topDomestic, ...provider.topImported];
        
        if (allCars.isEmpty) {
          return SizedBox(
            height: 190,
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.trending_up, size: 48, color: Colors.grey[400]),
                  const SizedBox(height: 8),
                  Text(
                    '추천 데이터를 불러오는 중...',
                    style: TextStyle(color: Colors.grey[500], fontSize: 14),
                  ),
                ],
              ),
            ),
          );
        }
        
        // 색상 팔레트
        final colors = [
          Colors.black87,
          Colors.grey[300]!,
          Colors.blue,
          Colors.yellow[700]!,
          Colors.green,
          Colors.purple,
        ];
        
        return SizedBox(
          height: 190,
          child: ListView.separated(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            scrollDirection: Axis.horizontal,
            itemCount: allCars.length,
            separatorBuilder: (context, index) => const SizedBox(width: 12),
            itemBuilder: (context, index) {
              final car = allCars[index];
              return CarCard(
                name: '${car.brand} ${car.model}',
                info: '평균 ${car.avgPrice}만원',
                price: _formatListingsCount(car.listings),
                color: colors[index % colors.length],
                isDark: isDark,
                onTap: () => _showPopularModelDeals(car),
              );
            },
          ),
        );
      },
    );
  }
}

// 분리된 차량 카드 위젯
class CarCard extends StatelessWidget {
  final String name;
  final String info;
  final String price;
  final Color color;
  final bool isDark;
  final VoidCallback? onTap;

  const CarCard({
    super.key,
    required this.name,
    required this.info,
    required this.price,
    required this.color,
    required this.isDark,
    this.onTap,
  });

  // 모델명에서 브랜드 로고 URL 추출
  String? _getImageUrl() {
    // name 형식: "브랜드 모델명" (예: "현대 그랜저", "기아 K5")
    final parts = name.split(' ');
    if (parts.length >= 2) {
      final brand = parts[0];
      final model = parts.sublist(1).join(' ');
      return CarImageMapper.getImageUrlByBrandModel(brand, model);
    }
    return CarImageMapper.getImageUrl(name);
  }

  @override
  Widget build(BuildContext context) {
    final cardColor = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final textColor = isDark ? Colors.white : Colors.black87;
    final imageUrl = _getImageUrl();

    return GestureDetector(
      onTap: onTap,
      child: Container(
      width: 140,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: isDark ? Colors.grey[800]! : Colors.grey[50]!),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 차량 이미지 영역
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Center(
                child: imageUrl != null
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: Image.network(
                          imageUrl,
                          width: 80,
                          height: 60,
                          fit: BoxFit.contain,
                          errorBuilder: (context, error, stackTrace) {
                            // 에러 로그 출력 (디버깅용)
                            print('[Image Error] $name: $error');
                            print('[Image URL] $imageUrl');
                            return Icon(
                              Icons.directions_car_filled,
                              color: color,
                              size: 48,
                            );
                          },
                          loadingBuilder: (context, child, loadingProgress) {
                            if (loadingProgress == null) return child;
                            return Icon(Icons.directions_car_filled, color: color.withValues(alpha: 0.3), size: 48);
                          },
                        ),
                      )
                    : Icon(
                        Icons.directions_car_filled,
                        color: color,
                        size: 48,
                      ),
              ),
            ),
          ),
          const SizedBox(height: 12),

          // 차량 정보 텍스트
          Text(
            name,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 14,
              color: textColor,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 4),
          Text(
            info,
            style: TextStyle(
              fontSize: 10,
              color: Colors.grey[500],
              fontWeight: FontWeight.w500,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 6),
          Text(
            price,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: Color(0xFF0066FF),
            ),
          ),
        ],
      ),
      ),
    );
  }
}
