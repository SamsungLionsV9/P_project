import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import 'car_info_input_page.dart';
import 'mypage.dart';
import 'settings_page.dart';
import 'recommendation_page.dart';
import 'comparison_page.dart';
import 'oauth_webview_page.dart';
import 'signup_page.dart';
import 'services/auth_service.dart';
import 'theme/theme_provider.dart';
import 'providers/comparison_provider.dart';
import 'providers/recent_views_provider.dart';
import 'providers/popular_cars_provider.dart';

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
          provider.setLoginState(authService.isLoggedIn);
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
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        return MaterialApp(
          title: '중고차 시세 예측',
          debugShowCheckedModeBanner: false,
          themeMode: themeProvider.themeMode,
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
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
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
      const HomePageContent(),
      const CarInfoInputPage(),
      const RecommendationPage(),
      const MyPage(),
      const SettingsPage(),
    ];

    return Scaffold(
      body: IndexedStack(
        index: _selectedIndex,
        children: pages,
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
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
    );
  }
}

class HomePageContent extends StatefulWidget {
  const HomePageContent({super.key});

  @override
  State<HomePageContent> createState() => _HomePageContentState();
}

class _HomePageContentState extends State<HomePageContent> {
  final AuthService _authService = AuthService();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  bool _isLoading = false;
  bool _isLoggedIn = false;

  @override
  void initState() {
    super.initState();
    _isLoggedIn = _authService.isLoggedIn;
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
      _showMessage('로그인 성공!');
      _emailController.clear();
      _passwordController.clear();
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
      _showMessage('${_getProviderName(provider)} 로그인 성공!');
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
            const SizedBox(height: 20),
            
            // 1. 메인 로그인 카드 영역
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: cardColor,
                  borderRadius: BorderRadius.circular(32),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: _isLoggedIn 
                  ? _buildLoggedInView(textColor)
                  : _buildLoginForm(isDark, textColor),
              ),
            ),

            const SizedBox(height: 32),

            // 2. 바로가기 버튼 (로그인 없이 조회)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: SizedBox(
                width: double.infinity,
                height: 52,
                child: OutlinedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => const CarInfoInputPage()),
                    );
                  },
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Color(0xFF0066FF)),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.search, color: Color(0xFF0066FF), size: 20),
                      SizedBox(width: 8),
                      Text(
                        "바로 시세 조회하기",
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF0066FF),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
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
        Text(
          "중고차 시세 예측 AI",
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: textColor,
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
        if (provider.isLoading && provider.recentViews.isEmpty) {
          return const SizedBox(
            height: 190,
            child: Center(child: CircularProgressIndicator()),
          );
        }
        
        if (provider.recentViews.isEmpty) {
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
            itemCount: provider.recentViews.length,
            separatorBuilder: (context, index) => const SizedBox(width: 12),
            itemBuilder: (context, index) {
              final car = provider.recentViews[index];
              return CarCard(
                name: car.name,
                info: car.info,
                price: car.price,
                color: car.color,
                isDark: isDark,
              );
            },
          ),
        );
      },
    );
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
                info: '${car.avgPrice}만원 ~',
                price: '${car.listings}대 매물',
                color: colors[index % colors.length],
                isDark: isDark,
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

  const CarCard({
    super.key,
    required this.name,
    required this.info,
    required this.price,
    required this.color,
    required this.isDark,
  });

  @override
  Widget build(BuildContext context) {
    final cardColor = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final textColor = isDark ? Colors.white : Colors.black87;

    return Container(
      width: 140,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: isDark ? Colors.grey[800]! : Colors.grey[50]!),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 차량 이미지 영역 (플레이스홀더)
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Center(
                child: Icon(
                  Icons.directions_car_filled,
                  color: Colors.white.withOpacity(0.5),
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
    );
  }
}
