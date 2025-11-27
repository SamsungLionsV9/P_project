import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:url_launcher/url_launcher.dart';
import 'car_info_input_page.dart';
import 'mypage.dart';
import 'settings_page.dart';
import 'recommendation_page.dart';
import 'oauth_webview_page.dart';
import 'signup_page.dart';
import 'services/auth_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // 저장된 토큰 로드
  await AuthService().loadSavedToken();
  
  // 웹 환경에서 OAuth 콜백 처리
  if (kIsWeb) {
    _handleWebOAuthCallback();
  }
  
  runApp(const CarPriceApp());
}

/// 웹 환경에서 OAuth 콜백 처리
void _handleWebOAuthCallback() {
  try {
    final uri = Uri.base;
    final token = uri.queryParameters['token'];
    final email = uri.queryParameters['email'];
    final provider = uri.queryParameters['provider'];
    
    if (token != null && email != null) {
      // 토큰 저장
      AuthService().handleOAuthCallback(token, email, provider ?? 'unknown');
      debugPrint('웹 OAuth 콜백 처리 완료: $email');
    }
  } catch (e) {
    debugPrint('OAuth 콜백 처리 오류: $e');
  }
}

class CarPriceApp extends StatefulWidget {
  const CarPriceApp({super.key});

  @override
  State<CarPriceApp> createState() => _CarPriceAppState();
}

class _CarPriceAppState extends State<CarPriceApp> {
  // 테마 모드 상태 관리 (기본값: 라이트 모드)
  ThemeMode _themeMode = ThemeMode.light;

  void _toggleTheme(bool isDark) {
    setState(() {
      _themeMode = isDark ? ThemeMode.dark : ThemeMode.light;
    });
  }


  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '중고차 시세 예측',
      debugShowCheckedModeBanner: false,
      themeMode: _themeMode,
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
      home: MainScreen(
        isDarkMode: _themeMode == ThemeMode.dark,
        onThemeChanged: _toggleTheme,
      ),
    );
  }
}

class MainScreen extends StatefulWidget {
  final bool isDarkMode;
  final ValueChanged<bool> onThemeChanged;

  const MainScreen({
    super.key,
    required this.isDarkMode,
    required this.onThemeChanged,
  });

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;

  late final List<Widget> _pages;

  @override
  void initState() {
    super.initState();
    // 페이지 리스트 초기화 시 콜백 전달
    _pages = [
      const HomePageContent(),
      const CarInfoInputPage(),
      const RecommendationPage(),  // 추천 페이지 추가
      const MyPage(),
      SettingsPage(
        isDarkMode: widget.isDarkMode,
        onThemeChanged: widget.onThemeChanged,
      ),
    ];
  }

  @override
  void didUpdateWidget(MainScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    // 테마 변경 시 SettingsPage 업데이트
    if (oldWidget.isDarkMode != widget.isDarkMode) {
      _pages[4] = SettingsPage(
        isDarkMode: widget.isDarkMode,
        onThemeChanged: widget.onThemeChanged,
      );
    }
  }

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    final isDark = widget.isDarkMode;
    final navBgColor = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final unselectedItemColor = isDark ? Colors.grey[600] : Colors.grey[400];

    return Scaffold(
      body: IndexedStack(
        index: _selectedIndex,
        children: _pages,
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
  bool _oauthCallbackProcessed = false; // OAuth 콜백 처리 플래그

  @override
  void initState() {
    super.initState();
    _checkLoginStatus();
    
    // 웹 환경에서 OAuth 콜백 확인
    if (kIsWeb) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _checkWebOAuthCallback();
      });
    }
  }
  
  /// 로그인 상태 확인
  void _checkLoginStatus() {
    setState(() {
      _isLoggedIn = _authService.isLoggedIn;
    });
  }
  
  /// 웹 환경에서 OAuth 콜백 확인 및 처리
  Future<void> _checkWebOAuthCallback() async {
    // 이미 처리된 경우 스킵
    if (_oauthCallbackProcessed) {
      return;
    }
    
    try {
      final uri = Uri.base;
      final token = uri.queryParameters['token'];
      final email = uri.queryParameters['email'];
      final provider = uri.queryParameters['provider'];
      final oauth = uri.queryParameters['oauth'];
      
      // OAuth 회원가입 리다이렉트 확인 (토큰 없이 oauth=true인 경우)
      if (oauth == 'true' && email != null && provider != null && token == null) {
        // 중복 처리 방지
        _oauthCallbackProcessed = true;
        
        debugPrint('🔑 OAuth 회원가입 리다이렉트 감지: $email ($provider)');
        
        // 기존 사용자인 경우 회원가입 페이지를 건너뛰고 바로 메인 페이지로
        final existing = uri.queryParameters['existing'];
        if (existing == 'true') {
          debugPrint('기존 사용자 감지, 메인 페이지로 이동');
          // 상태만 업데이트 (이미 메인 페이지에 있음)
          _checkLoginStatus();
          return;
        }
        
        // 회원가입 페이지로 이동
        if (mounted) {
          final result = await Navigator.push<bool>(
            context,
            MaterialPageRoute(
              builder: (context) => const SignupPage(),
            ),
          );
          
          // 회원가입 완료 후 처리
          if (result == true) {
            _checkLoginStatus(); // 로그인 상태 다시 확인
            // URL 정리 (웹 환경에서)
            if (kIsWeb) {
              // 쿼리 파라미터 제거를 위해 URL 변경
              // 실제로는 이미 메인 페이지에 있으므로 상태만 업데이트
            }
          }
        }
        return;
      }
      
      // 기존 사용자 로그인 (토큰이 있는 경우)
      if (token != null && email != null) {
        // 중복 처리 방지
        _oauthCallbackProcessed = true;
        
        debugPrint('🔑 OAuth 콜백 감지: $email ($provider)');
        
        // 토큰 저장 및 로그인 상태 업데이트
        await _authService.handleOAuthCallback(token, email, provider ?? 'unknown');
        
        // 로그인 상태 업데이트
        if (mounted) {
          setState(() {
            _isLoggedIn = true;
          });
          _showMessage('${_getProviderName(provider ?? 'unknown')} 로그인 성공!');
        }
      }
    } catch (e) {
      debugPrint('OAuth 콜백 처리 오류: $e');
      _oauthCallbackProcessed = false; // 에러 발생 시 재시도 가능하도록
      if (mounted) {
        _showMessage('로그인 처리 중 오류가 발생했습니다: $e', isError: true);
      }
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
      _showMessage('로그인 성공!');
      _emailController.clear();
      _passwordController.clear();
    } else {
      _showMessage(result['message'] ?? '로그인 실패', isError: true);
    }
  }

  /// 소셜 로그인
  Future<void> _socialLogin(String provider) async {
    final url = _authService.getSocialLoginUrl(provider);
    
    // 웹 환경에서는 WebView가 작동하지 않으므로 외부 브라우저 사용
    if (kIsWeb) {
      _showMessage('${_getProviderName(provider)} 로그인은 새 창에서 진행됩니다.');
      
      try {
        final uri = Uri.parse(url);
        if (await canLaunchUrl(uri)) {
          // 웹에서는 새 창으로 열기
          await launchUrl(uri, mode: LaunchMode.externalApplication);
          _showMessage('로그인 후 이 페이지로 돌아오세요.');
        } else {
          _showMessage('브라우저를 열 수 없습니다', isError: true);
        }
      } catch (e) {
        _showMessage('${_getProviderName(provider)} 로그인 오류: $e', isError: true);
      }
      return;
    }
    
    // 네이버는 WebView를 차단하므로 외부 브라우저 사용
    if (provider == 'naver') {
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
    
    // 모바일 앱에서는 WebView 사용
    final result = await Navigator.push<Map<String, dynamic>>(
      context,
      MaterialPageRoute(
        builder: (context) => OAuthWebViewPage(provider: provider),
      ),
    );

    if (result != null) {
      // 1. 기존 사용자 로그인 성공
      if (result['success'] == true) {
        setState(() => _isLoggedIn = true);
        _showMessage('${_getProviderName(provider)} 로그인 성공!');
      } 
      // 2. 신규 사용자 - 회원가입 필요
      else if (result['needsSignup'] == true) {
        _showMessage('회원가입이 필요합니다.');
        
        // 회원가입 페이지로 이동 (OAuth 정보 전달)
        final signupResult = await Navigator.push<bool>(
          context,
          MaterialPageRoute(
            builder: (context) => SignupPage(
              oauthEmail: result['email'],
              oauthProvider: result['provider'],
              oauthProviderId: result['providerId'],
              oauthImageUrl: result['imageUrl'],
            ),
          ),
        );
        
        // 회원가입 완료 후 로그인 상태 업데이트
        if (signupResult == true) {
          setState(() => _isLoggedIn = true);
          _showMessage('${_getProviderName(provider)} 회원가입 및 로그인 성공!');
        }
      }
      // 3. 에러
      else if (result['error'] != null) {
        _showMessage('로그인 실패: ${result['error']}', isError: true);
      }
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
    
    // 웹 환경에서 OAuth 콜백 확인 (빌드 시마다 확인)
    if (kIsWeb) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _checkWebOAuthCallback();
      });
    }
    
    // 로그인 상태 동기화
    final currentLoginStatus = _authService.isLoggedIn;
    if (_isLoggedIn != currentLoginStatus) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          setState(() {
            _isLoggedIn = currentLoginStatus;
          });
        }
      });
    }

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

            // 3. 최근 조회 차량 섹션
            _buildSectionTitle("최근 조회 차량", textColor),
            const SizedBox(height: 12),
            _buildHorizontalCarList(isReversed: false, isDark: isDark),

            const SizedBox(height: 32),

            // 3. 인기 모델 추천 섹션
            _buildSectionTitle("인기 모델 추천", textColor),
            const SizedBox(height: 12),
            _buildHorizontalCarList(isReversed: true, isDark: isDark),

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

  // Helper Widget: 가로 스크롤 차량 리스트
  Widget _buildHorizontalCarList({required bool isReversed, required bool isDark}) {
    // 더미 데이터
    final List<Map<String, dynamic>> cars = [
      {"name": "노란색 벤츠", "info": "2023년 / 0.8만KM", "price": "1억", "color": Colors.yellow},
      {"name": "파란색 차", "info": "2024년 / 1만KM", "price": "8000만원", "color": Colors.blue},
      {"name": "흰색 SUV", "info": "2025년 / 0.9만KM", "price": "9000만원", "color": Colors.grey[300]},
      {"name": "검정 세단", "info": "2022년 / 3만KM", "price": "5500만원", "color": Colors.black87},
    ];

    final displayList = isReversed ? cars.reversed.toList() : cars;

    return SizedBox(
      height: 190, // 카드 높이 + 그림자 여유분
      child: ListView.separated(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        scrollDirection: Axis.horizontal,
        itemCount: displayList.length,
        separatorBuilder: (context, index) => const SizedBox(width: 12),
        itemBuilder: (context, index) {
          final car = displayList[index];
          return CarCard(
            name: car['name'],
            info: car['info'],
            price: car['price'],
            color: car['color'],
            isDark: isDark,
          );
        },
      ),
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
