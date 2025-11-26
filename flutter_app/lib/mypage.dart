import 'package:flutter/material.dart';
import 'services/api_service.dart';

/// 마이페이지 - 백엔드 연동 버전
/// 찜한 차량, 최근 분석, 가격 알림 모두 DB에서 관리
class MyPage extends StatefulWidget {
  const MyPage({super.key});

  @override
  State<MyPage> createState() => _MyPageState();
}

class _MyPageState extends State<MyPage> with SingleTickerProviderStateMixin {
  final ApiService _api = ApiService();
  late TabController _tabController;

  // 데이터 상태
  List<Favorite> _favorites = [];
  List<SearchHistory> _history = [];
  List<PriceAlert> _alerts = [];
  
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final results = await Future.wait([
        _api.getFavorites(),
        _api.getHistory(limit: 20),
        _api.getAlerts(),
      ]);

      setState(() {
        _favorites = results[0] as List<Favorite>;
        _history = results[1] as List<SearchHistory>;
        _alerts = results[2] as List<PriceAlert>;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _toggleFavorite(SearchHistory item) async {
    // 이미 즐겨찾기에 있는지 확인
    final existing = _favorites.where((f) => 
      f.brand == item.brand && f.model == item.model && f.year == item.year
    ).toList();

    if (existing.isNotEmpty) {
      // 삭제
      await _api.removeFavorite(existing.first.id);
      _showSnackBar("'${item.brand} ${item.model}' 찜 목록에서 삭제되었습니다.");
    } else {
      // 추가
      await _api.addFavorite(
        brand: item.brand,
        model: item.model,
        year: item.year,
        mileage: item.mileage,
        predictedPrice: item.predictedPrice,
      );
      _showSnackBar("'${item.brand} ${item.model}' 찜 목록에 추가되었습니다.");
    }
    
    _loadData();
  }

  Future<void> _removeFavorite(Favorite fav) async {
    await _api.removeFavorite(fav.id);
    _showSnackBar("'${fav.brand} ${fav.model}' 찜 목록에서 삭제되었습니다.");
    _loadData();
  }

  Future<void> _toggleAlert(Favorite fav) async {
    // 알림이 있는지 확인
    final existing = _alerts.where((a) => 
      a.brand == fav.brand && a.model == fav.model && a.year == fav.year
    ).toList();

    if (existing.isNotEmpty) {
      // 토글
      await _api.toggleAlert(existing.first.id);
      final newState = !existing.first.isActive;
      _showSnackBar(newState 
        ? "'${fav.brand} ${fav.model}' 알림이 활성화되었습니다."
        : "'${fav.brand} ${fav.model}' 알림이 비활성화되었습니다.");
    } else {
      // 새로 추가
      await _api.addAlert(
        brand: fav.brand,
        model: fav.model,
        year: fav.year,
        targetPrice: fav.predictedPrice ?? 0,
      );
      _showSnackBar("'${fav.brand} ${fav.model}' 목표 가격 알림이 설정되었습니다.");
    }
    
    _loadData();
  }

  void _showSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), duration: const Duration(seconds: 2)),
    );
  }

  bool _isInFavorites(SearchHistory item) {
    return _favorites.any((f) => 
      f.brand == item.brand && f.model == item.model && f.year == item.year
    );
  }

  bool _hasActiveAlert(Favorite fav) {
    return _alerts.any((a) => 
      a.brand == fav.brand && a.model == fav.model && a.year == fav.year && a.isActive
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor = isDark ? Colors.white : Colors.black;
    final cardColor = isDark ? const Color(0xFF1E1E1E) : Colors.white;

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        elevation: 0,
        title: Text(
          "마이 페이지",
          style: TextStyle(
            color: textColor,
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: Icon(Icons.refresh, color: textColor),
            onPressed: _loadData,
          ),
        ],
      ),
      body: _isLoading 
        ? const Center(child: CircularProgressIndicator())
        : _error != null 
          ? _buildErrorView()
          : Column(
              children: [
                TabBar(
                  controller: _tabController,
                  labelColor: const Color(0xFF0066FF),
                  unselectedLabelColor: Colors.grey[400],
                  indicatorColor: const Color(0xFF0066FF),
                  indicatorWeight: 3,
                  labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                  tabs: const [
                    Tab(text: "찜한 차량"),
                    Tab(text: "최근 분석"),
                  ],
                ),
                Expanded(
                  child: TabBarView(
                    controller: _tabController,
                    children: [
                      _buildFavoritesTab(isDark, cardColor, textColor),
                      _buildHistoryTab(isDark, cardColor, textColor),
                    ],
                  ),
                ),
              ],
            ),
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, color: Colors.red, size: 48),
          const SizedBox(height: 16),
          const Text("데이터를 불러올 수 없습니다", style: TextStyle(color: Colors.grey)),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: _loadData,
            icon: const Icon(Icons.refresh),
            label: const Text("다시 시도"),
          ),
        ],
      ),
    );
  }

  // 1. 찜한 차량 탭 (DB 기반)
  Widget _buildFavoritesTab(bool isDark, Color cardColor, Color textColor) {
    if (_favorites.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.favorite_border, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text("찜한 차량이 없습니다", style: TextStyle(color: Colors.grey[500], fontSize: 16)),
            const SizedBox(height: 8),
            Text("최근 분석에서 하트를 눌러 추가하세요", style: TextStyle(color: Colors.grey[600], fontSize: 14)),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadData,
      child: ListView.separated(
        padding: const EdgeInsets.all(20),
        itemCount: _favorites.length,
        separatorBuilder: (context, index) => const SizedBox(height: 16),
        itemBuilder: (context, index) {
          return _buildFavoriteCard(_favorites[index], isDark, cardColor, textColor);
        },
      ),
    );
  }

  // 2. 최근 분석 탭 (DB 기반)
  Widget _buildHistoryTab(bool isDark, Color cardColor, Color textColor) {
    if (_history.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.history, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text("최근 분석 기록이 없습니다", style: TextStyle(color: Colors.grey[500], fontSize: 16)),
            const SizedBox(height: 8),
            Text("차량을 검색하면 여기에 기록됩니다", style: TextStyle(color: Colors.grey[600], fontSize: 14)),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadData,
      child: ListView.separated(
        padding: const EdgeInsets.all(20),
        itemCount: _history.length,
        separatorBuilder: (context, index) => const SizedBox(height: 16),
        itemBuilder: (context, index) {
          return _buildHistoryCard(_history[index], isDark, cardColor, textColor);
        },
      ),
    );
  }

  // 찜한 차량 카드 위젯
  Widget _buildFavoriteCard(Favorite fav, bool isDark, Color cardColor, Color textColor) {
    final borderColor = isDark ? Colors.grey[800]! : Colors.grey[100]!;
    final hasAlert = _hasActiveAlert(fav);
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          // 차량 아이콘
          Container(
            width: 100,
            height: 80,
            decoration: BoxDecoration(
              color: const Color(0xFF0066FF).withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.directions_car, color: Color(0xFF0066FF), size: 40),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "${fav.brand} ${fav.model}",
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: textColor),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  "${fav.predictedPrice?.toStringAsFixed(0) ?? '-'}만원",
                  style: const TextStyle(
                    color: Color(0xFF0066FF),
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  "${fav.year}년 · ${(fav.mileage / 10000).toStringAsFixed(1)}만km",
                  style: TextStyle(color: Colors.grey[500], fontSize: 12),
                ),
              ],
            ),
          ),
          Column(
            children: [
              // 알림 버튼
              GestureDetector(
                onTap: () => _toggleAlert(fav),
                child: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: hasAlert 
                        ? (isDark ? const Color(0xFF3E2723) : const Color(0xFFFFF8E1)) 
                        : (isDark ? Colors.grey[800] : Colors.grey[100]),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Icon(
                    hasAlert ? Icons.notifications_active : Icons.notifications_none,
                    color: hasAlert ? const Color(0xFFFFAB00) : Colors.grey[400],
                    size: 20,
                  ),
                ),
              ),
              const SizedBox(height: 8),
              // 삭제 버튼
              GestureDetector(
                onTap: () => _removeFavorite(fav),
                child: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: isDark ? const Color(0xFF3E2020) : const Color(0xFFFFEBEE),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Icon(
                    Icons.favorite,
                    color: Color(0xFFFF5252),
                    size: 20,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // 최근 분석 카드 위젯
  Widget _buildHistoryCard(SearchHistory item, bool isDark, Color cardColor, Color textColor) {
    final borderColor = isDark ? Colors.grey[800]! : Colors.grey[100]!;
    final isLiked = _isInFavorites(item);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          // 차량 아이콘
          Container(
            width: 80,
            height: 60,
            decoration: BoxDecoration(
              color: Colors.grey[isDark ? 800 : 200],
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(Icons.directions_car, color: Colors.grey[isDark ? 400 : 600], size: 30),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "${item.brand} ${item.model}",
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: textColor),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  "예상가 ${item.predictedPrice?.toStringAsFixed(0) ?? '-'}만원",
                  style: const TextStyle(
                    color: Color(0xFF0066FF),
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  "${item.year}년 · ${(item.mileage / 10000).toStringAsFixed(1)}만km",
                  style: TextStyle(color: Colors.grey[500], fontSize: 12),
                ),
              ],
            ),
          ),
          // 좋아요 버튼
          IconButton(
            onPressed: () => _toggleFavorite(item),
            icon: Icon(
              isLiked ? Icons.favorite : Icons.favorite_border,
              color: isLiked ? const Color(0xFFFF5252) : Colors.grey[400],
              size: 24,
            ),
          ),
        ],
      ),
    );
  }
}
