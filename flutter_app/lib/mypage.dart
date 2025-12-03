import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/api_service.dart';
import 'providers/comparison_provider.dart';
import 'providers/recent_views_provider.dart';
import 'models/car_data.dart';
import 'comparison_page.dart';
import 'widgets/deal_analysis_modal.dart';
import 'widgets/common/option_badges.dart';

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
        _api.getAlerts(),
      ]);

      setState(() {
        _favorites = results[0] as List<Favorite>;
        _alerts = results[1] as List<PriceAlert>;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _removeFavorite(Favorite fav) async {
    await _api.removeFavorite(fav.id);
    _showSnackBar("'${fav.brand} ${fav.model}' 찜 목록에서 삭제되었습니다.");
    _loadData();
  }

  Future<void> _toggleAlert(Favorite fav) async {
    // 알림이 있는지 확인
    final existing = _alerts
        .where((a) =>
            a.brand == fav.brand && a.model == fav.model && a.year == fav.year)
        .toList();

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

  void _showSnackBar(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration: const Duration(seconds: 2),
        backgroundColor: isError ? Colors.red : null,
      ),
    );
  }

  bool _hasActiveAlert(Favorite fav) {
    return _alerts.any((a) =>
        a.brand == fav.brand &&
        a.model == fav.model &&
        a.year == fav.year &&
        a.isActive);
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
                      labelStyle: const TextStyle(
                          fontWeight: FontWeight.bold, fontSize: 14),
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
    final comparisonProvider = Provider.of<ComparisonProvider>(context);

    if (_favorites.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.favorite_border, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text("찜한 차량이 없습니다",
                style: TextStyle(color: Colors.grey[500], fontSize: 16)),
            const SizedBox(height: 8),
            Text("최근 분석에서 하트를 눌러 추가하세요",
                style: TextStyle(color: Colors.grey[600], fontSize: 14)),
          ],
        ),
      );
    }

    return Column(
      children: [
        // 가격 비교 버튼
        if (comparisonProvider.hasEnoughToCompare)
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 0),
            child: SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                        builder: (context) => const ComparisonPage()),
                  );
                },
                icon: const Icon(Icons.compare_arrows),
                label: Text("${comparisonProvider.compareCount}대 가격 비교하기"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0066FF),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
          ),

        Expanded(
          child: RefreshIndicator(
            onRefresh: _loadData,
            child: ListView.separated(
              padding: const EdgeInsets.all(20),
              itemCount: _favorites.length,
              separatorBuilder: (context, index) => const SizedBox(height: 16),
              itemBuilder: (context, index) {
                return _buildFavoriteCard(
                    _favorites[index], isDark, cardColor, textColor);
              },
            ),
          ),
        ),
      ],
    );
  }

  // 2. 최근 분석 탭 (분석 페이지에서 클릭한 매물들)
  Widget _buildHistoryTab(bool isDark, Color cardColor, Color textColor) {
    return Consumer<RecentViewsProvider>(
      builder: (context, provider, child) {
        // 분석 페이지에서 클릭한 매물만 표시
        final analysisDeals = provider.analysisOnlyCars;

        if (analysisDeals.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.history, size: 64, color: Colors.grey[400]),
                const SizedBox(height: 16),
                Text("최근 분석한 매물이 없습니다",
                    style: TextStyle(color: Colors.grey[500], fontSize: 16)),
                const SizedBox(height: 8),
                Text("시세 예측 결과에서 매물을 클릭하면\n여기에 기록됩니다",
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.grey[600], fontSize: 14)),
              ],
            ),
          );
        }

        return Column(
          children: [
            // 헤더
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    "총 ${analysisDeals.length}개의 매물",
                    style: TextStyle(color: Colors.grey[500], fontSize: 14),
                  ),
                  TextButton.icon(
                    onPressed: () => _clearAnalysisDeals(provider),
                    icon: const Icon(Icons.delete_outline,
                        size: 18, color: Colors.red),
                    label: const Text("전체 삭제",
                        style: TextStyle(color: Colors.red)),
                  ),
                ],
              ),
            ),
            Expanded(
              child: ListView.separated(
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
                itemCount: analysisDeals.length,
                separatorBuilder: (context, index) =>
                    const SizedBox(height: 12),
                itemBuilder: (context, index) {
                  final deal = analysisDeals[index];
                  return _buildAnalysisDealCard(
                      deal, isDark, cardColor, textColor);
                },
              ),
            ),
          ],
        );
      },
    );
  }

  /// 분석 매물 전체 삭제
  Future<void> _clearAnalysisDeals(RecentViewsProvider provider) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('전체 삭제'),
        content: const Text('분석한 매물 기록을 모두 삭제하시겠습니까?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('취소'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('삭제', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      provider.clearBySource('analysis');
    }
  }

  /// 분석 매물 카드 위젯
  Widget _buildAnalysisDealCard(
      RecommendedCar deal, bool isDark, Color cardColor, Color textColor) {
    final isGood = deal.priceDiff > 0;
    // 찜 여부 확인 (고유 매물 단위로 구별)
    final isFavorite = _favorites.any((f) => f.isSameDeal(deal));

    return GestureDetector(
      onTap: () => _showDealAnalysis(deal),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: cardColor,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isGood
                ? Colors.green.withOpacity(0.3)
                : (isDark ? Colors.grey[800]! : Colors.grey[200]!),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                if (isGood)
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    margin: const EdgeInsets.only(right: 8),
                    decoration: BoxDecoration(
                      color: Colors.green.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: const Text('가성비',
                        style: TextStyle(
                            color: Colors.green,
                            fontSize: 11,
                            fontWeight: FontWeight.bold)),
                  ),
                Expanded(
                  child: Text(
                    '${deal.brand} ${deal.model}',
                    style: TextStyle(
                        color: textColor,
                        fontSize: 15,
                        fontWeight: FontWeight.w600),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                // 찜하기 버튼
                GestureDetector(
                  onTap: () => _toggleFavoriteFromDeal(deal),
                  child: Icon(
                    isFavorite ? Icons.favorite : Icons.favorite_border,
                    color: isFavorite ? Colors.red : Colors.grey[400],
                    size: 22,
                  ),
                ),
                const SizedBox(width: 8),
                Icon(Icons.chevron_right, color: Colors.grey[400], size: 20),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              '${deal.year}년 · ${deal.formattedMileage} · ${deal.fuel}',
              style: TextStyle(color: Colors.grey[500], fontSize: 13),
            ),
            // 옵션 배지 표시
            if (deal.options != null) ...[
              const SizedBox(height: 8),
              OptionBadges(options: deal.options!, compact: true),
            ],
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('실제가',
                          style:
                              TextStyle(color: Colors.grey[500], fontSize: 11)),
                      Text('${deal.actualPrice}만원',
                          style: TextStyle(
                              color: textColor,
                              fontSize: 16,
                              fontWeight: FontWeight.bold)),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('예측가',
                          style:
                              TextStyle(color: Colors.grey[500], fontSize: 11)),
                      Text('${deal.predictedPrice}만원',
                          style:
                              TextStyle(color: Colors.grey[400], fontSize: 16)),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text('차이',
                        style:
                            TextStyle(color: Colors.grey[500], fontSize: 11)),
                    Text(
                      '${deal.priceDiff > 0 ? "-" : "+"}${deal.priceDiff.abs()}만원',
                      style: TextStyle(
                        color: deal.priceDiff > 0 ? Colors.green : Colors.red,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// RecommendedCar에서 찜 토글 (고유 매물 단위로 구별 + 즉시 UI 반영)
  Future<void> _toggleFavoriteFromDeal(RecommendedCar deal) async {
    // isSameDeal로 정확한 매물 구별 (detailUrl 또는 가격+주행거리 조합)
    final existing = _favorites.where((f) => f.isSameDeal(deal)).toList();
    final isCurrentlyFavorite = existing.isNotEmpty;

    // 1. 즉시 로컬 상태 업데이트 (optimistic update)
    if (isCurrentlyFavorite) {
      setState(() {
        _favorites.removeWhere((f) => f.isSameDeal(deal));
      });
    } else {
      // 임시 Favorite 객체 생성
      final tempFavorite = Favorite(
        id: DateTime.now().millisecondsSinceEpoch,
        carId: deal.carId,
        brand: deal.brand,
        model: deal.model,
        year: deal.year,
        mileage: deal.mileage,
        predictedPrice: deal.predictedPrice.toDouble(),
        actualPrice: deal.actualPrice,
        detailUrl: deal.detailUrl,
      );
      setState(() {
        _favorites.add(tempFavorite);
      });
    }

    // 2. 서버에 요청
    try {
      if (isCurrentlyFavorite) {
        await _api.removeFavorite(existing.first.id);
        _showSnackBar("'${deal.brand} ${deal.model}' 찜 목록에서 삭제되었습니다.");
      } else {
        await _api.addFavorite(
          brand: deal.brand,
          model: deal.model,
          year: deal.year,
          mileage: deal.mileage,
          predictedPrice: deal.predictedPrice.toDouble(),
          actualPrice: deal.actualPrice,
          detailUrl: deal.detailUrl,
          carId: deal.carId,
        );
        _showSnackBar("'${deal.brand} ${deal.model}' 찜 목록에 추가되었습니다.");
      }

      // 3. 서버에서 최신 상태로 동기화
      await _loadData();
    } catch (e) {
      // 실패 시 원래 상태로 복구
      await _loadData();
      _showSnackBar("오류가 발생했습니다.");
    }
  }

  /// 매물 상세 분석 모달 표시
  void _showDealAnalysis(RecommendedCar deal) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DealAnalysisModal(
        deal: deal,
        predictedPrice: deal.predictedPrice,
      ),
    );
  }

  // 찜한 차량 카드 위젯
  Widget _buildFavoriteCard(
      Favorite fav, bool isDark, Color cardColor, Color textColor) {
    final comparisonProvider = Provider.of<ComparisonProvider>(context);
    final borderColor = isDark ? Colors.grey[800]! : Colors.grey[100]!;
    final hasAlert = _hasActiveAlert(fav);

    // Favorite를 CarData로 변환
    final carData = CarData(
      id: fav.id.toString(),
      name: "${fav.brand} ${fav.model}",
      price: "${fav.predictedPrice?.toStringAsFixed(0) ?? 0}만원",
      info: "${fav.year}년 · ${(fav.mileage / 10000).toStringAsFixed(1)}만km",
      date: fav.createdAt ?? '',
      color: const Color(0xFF0066FF),
      isLiked: true,
    );
    final isComparing = comparisonProvider.isComparing(carData);

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
            child: const Icon(Icons.directions_car,
                color: Color(0xFF0066FF), size: 40),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "${fav.brand} ${fav.model}",
                  style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: textColor),
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
              // 비교 버튼
              GestureDetector(
                onTap: () {
                  final success = comparisonProvider.toggleCompare(carData);
                  if (!success && !isComparing) {
                    _showSnackBar("최대 3대까지 비교할 수 있습니다");
                  } else {
                    _showSnackBar(isComparing
                        ? "비교 목록에서 제거되었습니다"
                        : "비교 목록에 추가되었습니다 (${comparisonProvider.compareCount + 1}/3)");
                  }
                },
                child: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: isComparing
                        ? (isDark
                            ? const Color(0xFF1A237E)
                            : const Color(0xFFE3F2FD))
                        : (isDark ? Colors.grey[800] : Colors.grey[100]),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Icon(
                    isComparing ? Icons.compare_arrows : Icons.add_chart,
                    color: isComparing
                        ? const Color(0xFF0066FF)
                        : Colors.grey[400],
                    size: 20,
                  ),
                ),
              ),
              const SizedBox(height: 8),
              // 알림 버튼
              GestureDetector(
                onTap: () => _toggleAlert(fav),
                child: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: hasAlert
                        ? (isDark
                            ? const Color(0xFF3E2723)
                            : const Color(0xFFFFF8E1))
                        : (isDark ? Colors.grey[800] : Colors.grey[100]),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Icon(
                    hasAlert
                        ? Icons.notifications_active
                        : Icons.notifications_none,
                    color:
                        hasAlert ? const Color(0xFFFFAB00) : Colors.grey[400],
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
                    color: isDark
                        ? const Color(0xFF3E2020)
                        : const Color(0xFFFFEBEE),
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
}
