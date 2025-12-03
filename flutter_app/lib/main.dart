import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'car_info_input_page.dart';
import 'mypage.dart';
import 'settings_page.dart';
import 'recommendation_page.dart';

import 'login_page.dart';
import 'services/auth_service.dart';
import 'services/api_service.dart';
import 'theme/theme_provider.dart';
import 'providers/comparison_provider.dart';
import 'providers/recent_views_provider.dart';
import 'providers/popular_cars_provider.dart';
import 'widgets/deal_analysis_modal.dart';
import 'widgets/model_deals_modal.dart';
import 'widgets/market_trend_card.dart';
import 'widgets/ai_pick_card.dart';

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
              label: '시세조회',
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
  bool _isLoggedIn = false;

  @override
  void initState() {
    super.initState();
    _checkLoginStatus();
  }

  Future<void> _checkLoginStatus() async {
    final isLoggedIn = _authService.isLoggedIn;
    if (mounted) {
      setState(() {
        _isLoggedIn = isLoggedIn;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor = isDark ? Colors.white : Colors.black87;

    return SafeArea(
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1. Hero Section (New Design)
            _buildHeroSection(isDark),

            const SizedBox(height: 24),

            // 1.5 Market Trend & AI Pick Cards
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Row(
                children: [
                  Expanded(child: const MarketTrendCard()),
                  const SizedBox(width: 12),
                  Expanded(
                    child: AiPickCard(
                      onTap: _showAiPickDetails,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 32),

            // 2. 인기 모델 추천 섹션
            _buildSectionTitle("인기 모델 추천", textColor),
            const SizedBox(height: 12),
            _buildPopularCarsList(isDark: isDark),

            const SizedBox(height: 32),

            // 3. 최근 조회 차량 섹션
            _buildSectionTitle("최근 조회 차량", textColor),
            const SizedBox(height: 12),
            _buildRecentViewsList(isDark: isDark),

            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _buildHeroSection(bool isDark) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(24, 40, 24, 40),
      decoration: const BoxDecoration(
        color: Color(0xFF001F3F), // Dark Blue Background
        borderRadius: BorderRadius.only(
          bottomLeft: Radius.circular(32),
          bottomRight: Radius.circular(32),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "AI Price Check, Signal",
            style: TextStyle(
              color: Color(0xFF4DA8DA), // Light Blue Accent
              fontSize: 14,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            "내 차 시세,\nAI로 정확하게 확인하세요",
            style: TextStyle(
              color: Colors.white,
              fontSize: 28,
              fontWeight: FontWeight.bold,
              height: 1.3,
            ),
          ),
          const SizedBox(height: 42),

          // Check Price Button
          SizedBox(
            width: double.infinity,
            height: 56,
            child: ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) =>
                          const CarInfoInputPage(showBackButton: true)),
                );
              },
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
                    "바로 시세 조회하기",
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(width: 8),
                  Icon(Icons.arrow_forward_rounded),
                ],
              ),
            ),
          ),

          const SizedBox(height: 42),

          // Login / Signup or Welcome Message
          if (!_isLoggedIn)
            Center(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Text(
                    "관심 차량 찜하고, 가격 알림 받아보세요!",
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.7),
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 8),
                  OutlinedButton(
                    onPressed: () async {
                      await Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) => const LoginPage()),
                      );
                      _checkLoginStatus(); // Refresh status after returning
                    },
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.white,
                      side: const BorderSide(color: Colors.white, width: 1),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(30),
                      ),
                      padding: const EdgeInsets.symmetric(
                          horizontal: 24, vertical: 12),
                    ),
                    child: const Text(
                      "로그인 / 회원가입",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                  ),
                ],
              ),
            )
          else
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  "환영합니다, ${_authService.userEmail ?? '사용자'}님!",
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
        ],
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
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: textColor,
            ),
          ),
          Icon(Icons.arrow_forward_ios, size: 16, color: Colors.grey[400]),
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

  /// AI 추천 픽 클릭 시 상세 분석 모달 표시 (하드코딩된 데이터 사용)
  void _showAiPickDetails() {
    // 최근 조회 Provider (모달에서 매물 클릭 시 기록 추가용)
    final recentViewsProvider = context.read<RecentViewsProvider>();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => ModelDealsModal(
        brand: "현대",
        model: "그랜저 IG",
        avgPrice: 2450,
        medianPrice: 2380,
        listings: 1240,
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

  @override
  Widget build(BuildContext context) {
    final cardColor = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final textColor = isDark ? Colors.white : Colors.black87;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 140,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: cardColor,
          borderRadius: BorderRadius.circular(20),
          border:
              Border.all(color: isDark ? Colors.grey[800]! : Colors.grey[50]!),
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
      ),
    );
  }
}
