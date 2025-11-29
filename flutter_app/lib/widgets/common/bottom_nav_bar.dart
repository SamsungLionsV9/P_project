import 'package:flutter/material.dart';

/// 공유 하단 네비게이션 바 위젯
/// push된 화면에서도 하단 네비게이션을 유지하기 위해 사용
class SharedBottomNavBar extends StatelessWidget {
  /// 현재 선택된 탭 인덱스 (0: 홈, 1: 내 차 찾기, 2: 추천, 3: 마이, 4: 설정)
  final int currentIndex;
  
  /// 다른 탭으로 이동할 때 호출되는 콜백
  /// 보통 Navigator.popUntil로 홈으로 돌아간 후 탭 전환
  final Function(int)? onTap;

  const SharedBottomNavBar({
    super.key,
    required this.currentIndex,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final navBgColor = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final unselectedItemColor = isDark ? Colors.grey[600] : Colors.grey[400];

    return Container(
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
        currentIndex: currentIndex,
        selectedItemColor: const Color(0xFF0066FF),
        unselectedItemColor: unselectedItemColor,
        selectedFontSize: 12,
        unselectedFontSize: 12,
        elevation: 0,
        onTap: (index) {
          if (index == currentIndex) return;
          if (onTap != null) {
            onTap!(index);
          } else {
            // 기본 동작: 홈으로 돌아간 후 탭 전환
            _navigateToTab(context, index);
          }
        },
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
    );
  }

  /// 기본 탭 이동 로직
  void _navigateToTab(BuildContext context, int tabIndex) {
    // 루트까지 모든 화면을 pop하고 MainScreen으로 돌아감
    Navigator.of(context).popUntil((route) => route.isFirst);
    
    // MainScreen의 탭 전환을 위해 콜백 호출
    // MainScreen은 GlobalKey를 통해 접근하거나 InheritedWidget/Provider를 사용
    MainScreenNavigator.of(context)?.switchTab(tabIndex);
  }
}

/// MainScreen 탭 전환을 위한 InheritedWidget
class MainScreenNavigator extends InheritedWidget {
  final void Function(int) switchTab;

  const MainScreenNavigator({
    super.key,
    required this.switchTab,
    required super.child,
  });

  static MainScreenNavigator? of(BuildContext context) {
    return context.dependOnInheritedWidgetOfExactType<MainScreenNavigator>();
  }

  @override
  bool updateShouldNotify(MainScreenNavigator oldWidget) => false;
}

