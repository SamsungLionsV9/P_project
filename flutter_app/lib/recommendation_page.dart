import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'services/api_service.dart';
import 'widgets/deal_analysis_modal.dart';
import 'providers/recent_views_provider.dart';
import 'widgets/common/option_badges.dart';

/// 차량 추천 페이지
/// 엔카 데이터 기반 인기 모델 및 가성비 차량 추천
class RecommendationPage extends StatefulWidget {
  const RecommendationPage({super.key});

  @override
  State<RecommendationPage> createState() => _RecommendationPageState();
}

class _RecommendationPageState extends State<RecommendationPage>
    with SingleTickerProviderStateMixin {
  final ApiService _api = ApiService();
  late TabController _tabController;

  List<PopularCar> _popularDomestic = [];
  List<PopularCar> _popularImported = [];
  List<RecommendedCar> _recommendations = [];
  List<Favorite> _favorites = []; // 찜 목록

  bool _isLoading = true;
  String? _error;

  // 예산 필터
  int? _budgetMin;
  int? _budgetMax;
  String _category = 'all';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadData();
    _loadFavorites(); // 찜 목록 로드
    // Provider 초기화
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<RecentViewsProvider>().loadRecentViews();
    });
  }

  /// 찜 목록 로드
  Future<void> _loadFavorites() async {
    try {
      final favorites = await _api.getFavorites();
      if (mounted) {
        setState(() => _favorites = favorites);
      }
    } catch (e) {
      // 무시
    }
  }

  /// 찜 토글 (고유 매물 단위로 구별 + 즉시 UI 반영)
  Future<void> _toggleFavorite(RecommendedCar car) async {
    // isSameDeal로 정확한 매물 구별
    final existing = _favorites.where((f) => f.isSameDeal(car)).toList();
    final isCurrentlyFavorite = existing.isNotEmpty;

    // 1. 즉시 로컬 상태 업데이트 (optimistic update)
    if (isCurrentlyFavorite) {
      setState(() {
        _favorites.removeWhere((f) => f.isSameDeal(car));
      });
    } else {
      // 임시 Favorite 객체 생성
      final tempFavorite = Favorite(
        id: DateTime.now().millisecondsSinceEpoch,
        carId: car.carId,
        brand: car.brand,
        model: car.model,
        year: car.year,
        mileage: car.mileage,
        predictedPrice: car.predictedPrice.toDouble(),
        actualPrice: car.actualPrice,
        detailUrl: car.detailUrl,
      );
      setState(() {
        _favorites.add(tempFavorite);
      });
    }

    // 2. 서버에 요청
    try {
      if (isCurrentlyFavorite) {
        await _api.removeFavorite(existing.first.id);
        _showSnackBar("'${car.brand} ${car.model}' 찜 목록에서 삭제되었습니다.");
      } else {
        await _api.addFavorite(
          brand: car.brand,
          model: car.model,
          year: car.year,
          mileage: car.mileage,
          predictedPrice: car.predictedPrice.toDouble(),
          actualPrice: car.actualPrice,
          detailUrl: car.detailUrl,
          carId: car.carId,
        );
        _showSnackBar("'${car.brand} ${car.model}' 찜 목록에 추가되었습니다.");
      }

      // 3. 서버에서 최신 상태로 동기화
      await _loadFavorites();
    } catch (e) {
      // 실패 시 원래 상태로 복구
      await _loadFavorites();
      _showSnackBar("오류가 발생했습니다.");
    }
  }

  void _showSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), duration: const Duration(seconds: 2)),
    );
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
        _api.getPopular(category: 'domestic', limit: 10),
        _api.getPopular(category: 'imported', limit: 10),
        _api.getRecommendations(
          category: _category,
          budgetMin: _budgetMin,
          budgetMax: _budgetMax,
          limit: 20,
        ),
      ]);

      setState(() {
        _popularDomestic = results[0] as List<PopularCar>;
        _popularImported = results[1] as List<PopularCar>;
        _recommendations = results[2] as List<RecommendedCar>;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  /// 최근 조회 기록에 매물 추가 (Provider를 통해 전역 저장)
  void _addToRecentViewed(RecommendedCar car) {
    context.read<RecentViewsProvider>().addRecentCar(car);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1A1A2E),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1A1A2E),
        title: const Text(
          '🚗 차량 추천',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: const Color(0xFF6C63FF),
          labelColor: Colors.white,
          unselectedLabelColor: Colors.grey,
          tabs: const [
            Tab(text: '인기 모델', icon: Icon(Icons.trending_up)),
            Tab(text: '추천 차량', icon: Icon(Icons.recommend)),
            Tab(text: '최근 조회', icon: Icon(Icons.history)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: _loadData,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(color: Color(0xFF6C63FF)))
          : _error != null
              ? _buildErrorView()
              : TabBarView(
                  controller: _tabController,
                  children: [
                    _buildPopularTab(),
                    _buildRecommendationTab(),
                    _buildHistoryTab(),
                  ],
                ),
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, color: Colors.red, size: 64),
          const SizedBox(height: 16),
          Text(
            '데이터를 불러올 수 없습니다',
            style: TextStyle(color: Colors.grey[400], fontSize: 18),
          ),
          const SizedBox(height: 8),
          Text(_error ?? '', style: TextStyle(color: Colors.grey[600])),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _loadData,
            icon: const Icon(Icons.refresh),
            label: const Text('다시 시도'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF6C63FF),
            ),
          ),
        ],
      ),
    );
  }

  /// 인기 모델 탭
  Widget _buildPopularTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionTitle('🇰🇷 국산차 인기 모델', '엔카 등록 기준'),
          const SizedBox(height: 12),
          ..._popularDomestic.map((car) => _buildPopularCard(car)),
          const SizedBox(height: 24),
          _buildSectionTitle('🌍 수입차 인기 모델', '엔카 등록 기준'),
          const SizedBox(height: 12),
          ..._popularImported.map((car) => _buildPopularCard(car)),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title, String subtitle) {
    return Row(
      children: [
        Text(
          title,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const Spacer(),
        Text(
          subtitle,
          style: TextStyle(color: Colors.grey[500], fontSize: 12),
        ),
      ],
    );
  }

  /// 인기 모델 클릭 시 가성비 매물 모달 표시
  void _showModelDeals(PopularCar car) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _ModelDealsModal(
        brand: car.brand,
        model: car.model,
        avgPrice: car.avgPrice,
        medianPrice: car.medianPrice,
        listings: car.listings,
        onCarViewed: _addToRecentViewed, // 최근 조회 콜백
      ),
    );
  }

  Widget _buildPopularCard(PopularCar car) {
    return GestureDetector(
      onTap: () => _showModelDeals(car),
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF252542),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.white10),
        ),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: const Color(0xFF6C63FF).withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.directions_car, color: Color(0xFF6C63FF)),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${car.brand} ${car.model}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '등록 ${car.listings}건 • 평균 ${car.avgPrice}만원',
                    style: TextStyle(color: Colors.grey[400], fontSize: 13),
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${car.medianPrice}만원',
                  style: const TextStyle(
                    color: Color(0xFF6C63FF),
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  '중앙값',
                  style: TextStyle(color: Colors.grey[500], fontSize: 11),
                ),
              ],
            ),
            const SizedBox(width: 8),
            Icon(Icons.chevron_right, color: Colors.grey[600], size: 20),
          ],
        ),
      ),
    );
  }

  /// 추천 차량 탭
  Widget _buildRecommendationTab() {
    return Column(
      children: [
        // 필터
        Container(
          padding: const EdgeInsets.all(16),
          color: const Color(0xFF252542),
          child: Row(
            children: [
              Expanded(
                child: _buildFilterChip('전체', _category == 'all', () {
                  setState(() => _category = 'all');
                  _loadData();
                }),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildFilterChip('국산', _category == 'domestic', () {
                  setState(() => _category = 'domestic');
                  _loadData();
                }),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildFilterChip('수입', _category == 'imported', () {
                  setState(() => _category = 'imported');
                  _loadData();
                }),
              ),
              const SizedBox(width: 16),
              IconButton(
                icon: const Icon(Icons.filter_list, color: Colors.white),
                onPressed: _showBudgetFilter,
              ),
            ],
          ),
        ),
        // 리스트
        Expanded(
          child: _recommendations.isEmpty
              ? Center(
                  child: Text(
                    '추천 차량이 없습니다',
                    style: TextStyle(color: Colors.grey[500]),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _recommendations.length,
                  itemBuilder: (context, index) {
                    return _buildRecommendationCard(_recommendations[index]);
                  },
                ),
        ),
      ],
    );
  }

  Widget _buildFilterChip(String label, bool selected, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10),
        decoration: BoxDecoration(
          color: selected ? const Color(0xFF6C63FF) : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: selected ? const Color(0xFF6C63FF) : Colors.grey[700]!,
          ),
        ),
        child: Center(
          child: Text(
            label,
            style: TextStyle(
              color: selected ? Colors.white : Colors.grey[400],
              fontWeight: selected ? FontWeight.bold : FontWeight.normal,
            ),
          ),
        ),
      ),
    );
  }

  /// 추천 차량 클릭 시 상세 분석 모달 표시 + 최근 조회 저장
  void _showRecommendationAnalysis(RecommendedCar car) {
    // 최근 조회 기록에 추가 (로컬)
    _addToRecentViewed(car);

    // 상세 분석 모달 표시
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

  Widget _buildRecommendationCard(RecommendedCar car) {
    final isGood = car.isGoodDeal;
    return GestureDetector(
      onTap: () => _showRecommendationAnalysis(car),
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF252542),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isGood ? Colors.green.withOpacity(0.5) : Colors.white10,
            width: isGood ? 2 : 1,
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
                    decoration: BoxDecoration(
                      color: Colors.green.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: const Text(
                      '🔥 가성비',
                      style: TextStyle(color: Colors.green, fontSize: 12),
                    ),
                  ),
                if (isGood) const SizedBox(width: 8),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: const Color(0xFF6C63FF).withOpacity(0.2),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    car.type == 'domestic' ? '국산' : '수입',
                    style:
                        const TextStyle(color: Color(0xFF6C63FF), fontSize: 12),
                  ),
                ),
                const Spacer(),
                Text(
                  '점수 ${car.score.toStringAsFixed(1)}',
                  style: TextStyle(color: Colors.grey[500], fontSize: 12),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              '${car.brand} ${car.model}',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                _buildInfoChip(Icons.calendar_today, '${car.year}년'),
                const SizedBox(width: 12),
                _buildInfoChip(Icons.speed, car.formattedMileage),
                const SizedBox(width: 12),
                _buildInfoChip(Icons.local_gas_station, car.fuel),
              ],
            ),
            // 옵션 배지 표시
            if (car.options != null) ...[
              const SizedBox(height: 10),
              OptionBadges(options: car.options!, compact: true),
            ],
            const SizedBox(height: 12),
            Row(
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('실제가',
                        style:
                            TextStyle(color: Colors.grey[500], fontSize: 12)),
                    Text(
                      '${car.actualPrice}만원',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const Spacer(),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text('예측가',
                        style:
                            TextStyle(color: Colors.grey[500], fontSize: 12)),
                    Text(
                      '${car.predictedPrice}만원',
                      style: TextStyle(color: Colors.grey[400], fontSize: 16),
                    ),
                  ],
                ),
                const SizedBox(width: 16),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: car.priceDiff > 0
                        ? Colors.green.withOpacity(0.2)
                        : Colors.red.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '${car.priceDiff > 0 ? "+" : ""}${car.priceDiff}만원',
                    style: TextStyle(
                      color: car.priceDiff > 0 ? Colors.green : Colors.red,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            // 상세보기 안내
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                Icon(Icons.open_in_new, size: 14, color: Colors.grey[500]),
                const SizedBox(width: 4),
                Text('탭하여 상세보기',
                    style: TextStyle(color: Colors.grey[500], fontSize: 11)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoChip(IconData icon, String text) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 14, color: Colors.grey[500]),
        const SizedBox(width: 4),
        Text(text, style: TextStyle(color: Colors.grey[400], fontSize: 13)),
      ],
    );
  }

  /// 최근 조회 탭 (Provider 기반 - 추천 탭에서 클릭한 매물만)
  Widget _buildHistoryTab() {
    return Consumer<RecentViewsProvider>(
      builder: (context, provider, child) {
        // 추천 탭에서 조회한 차량만 표시 (분석 페이지 매물 제외)
        final recentCars = provider.recommendationOnlyCars;

        if (recentCars.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.history, size: 64, color: Colors.grey[700]),
                const SizedBox(height: 16),
                Text(
                  '최근 조회한 차량이 없습니다',
                  style: TextStyle(color: Colors.grey[500], fontSize: 16),
                ),
                const SizedBox(height: 8),
                Text(
                  '인기 모델이나 추천 차량의 매물을\n클릭하면 여기에 기록됩니다',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.grey[600], fontSize: 14),
                ),
              ],
            ),
          );
        }

        return Column(
          children: [
            // 헤더
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '총 ${recentCars.length}건',
                    style: TextStyle(color: Colors.grey[400], fontSize: 14),
                  ),
                  TextButton.icon(
                    onPressed: _clearRecentViewed,
                    icon: const Icon(Icons.delete_sweep,
                        size: 18, color: Colors.red),
                    label: const Text('전체 삭제',
                        style: TextStyle(color: Colors.red, fontSize: 13)),
                  ),
                ],
              ),
            ),
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: recentCars.length,
                itemBuilder: (context, index) {
                  final car = recentCars[index];
                  // 고유 매물 단위로 찜 여부 확인
                  final isFavorite = _favorites.any((f) => f.isSameDeal(car));
                  return GestureDetector(
                    onTap: () => _showRecommendationAnalysis(car),
                    child: Container(
                      margin: const EdgeInsets.only(bottom: 12),
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: const Color(0xFF252542),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: car.isGoodDeal
                              ? Colors.green.withOpacity(0.4)
                              : Colors.white10,
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                width: 48,
                                height: 48,
                                decoration: BoxDecoration(
                                  color: car.isGoodDeal
                                      ? Colors.green.withOpacity(0.1)
                                      : Colors.white10,
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Icon(
                                  car.isGoodDeal
                                      ? Icons.thumb_up
                                      : Icons.directions_car,
                                  color: car.isGoodDeal
                                      ? Colors.green
                                      : Colors.white54,
                                ),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      '${car.brand} ${car.model}',
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontSize: 16,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      '${car.year}년 • ${(car.mileage / 10000).toStringAsFixed(1)}만km • ${car.fuel}',
                                      style: TextStyle(
                                          color: Colors.grey[400],
                                          fontSize: 13),
                                    ),
                                  ],
                                ),
                              ),
                              // 찜하기 버튼
                              GestureDetector(
                                onTap: () => _toggleFavorite(car),
                                child: Container(
                                  padding: const EdgeInsets.all(8),
                                  child: Icon(
                                    isFavorite
                                        ? Icons.favorite
                                        : Icons.favorite_border,
                                    color: isFavorite
                                        ? Colors.red
                                        : Colors.grey[500],
                                    size: 22,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 4),
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.end,
                                children: [
                                  Text(
                                    '${car.actualPrice}만원',
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  if (car.priceDiff > 0)
                                    Text(
                                      '-${car.priceDiff}만원',
                                      style: const TextStyle(
                                        color: Colors.green,
                                        fontSize: 12,
                                      ),
                                    ),
                                ],
                              ),
                              const SizedBox(width: 8),
                              GestureDetector(
                                onTap: () => provider.removeAt(index),
                                child: Icon(Icons.close,
                                    size: 18, color: Colors.grey[600]),
                              ),
                            ],
                          ),
                          // 옵션 배지 표시
                          if (car.options != null) ...[
                            const SizedBox(height: 10),
                            OptionBadges(options: car.options!, compact: true),
                          ],
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        );
      },
    );
  }

  /// 최근 조회 전체 삭제
  void _clearRecentViewed() {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        backgroundColor: const Color(0xFF252542),
        title: const Text('전체 삭제', style: TextStyle(color: Colors.white)),
        content: const Text('모든 조회 기록을 삭제하시겠습니까?',
            style: TextStyle(color: Colors.white70)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('취소'),
          ),
          TextButton(
            onPressed: () {
              context.read<RecentViewsProvider>().clearAll();
              Navigator.pop(dialogContext);
            },
            child: const Text('삭제', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  void _showBudgetFilter() {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF252542),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '💰 예산 필터',
              style: TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 24),
            _buildBudgetOption('전체', null, null),
            _buildBudgetOption('1,000만원 이하', null, 1000),
            _buildBudgetOption('1,000 ~ 2,000만원', 1000, 2000),
            _buildBudgetOption('2,000 ~ 3,000만원', 2000, 3000),
            _buildBudgetOption('3,000 ~ 5,000만원', 3000, 5000),
            _buildBudgetOption('5,000만원 이상', 5000, null),
          ],
        ),
      ),
    );
  }

  Widget _buildBudgetOption(String label, int? min, int? max) {
    final isSelected = _budgetMin == min && _budgetMax == max;
    return ListTile(
      onTap: () {
        setState(() {
          _budgetMin = min;
          _budgetMax = max;
        });
        Navigator.pop(context);
        _loadData();
      },
      leading: Icon(
        isSelected ? Icons.radio_button_checked : Icons.radio_button_off,
        color: isSelected ? const Color(0xFF6C63FF) : Colors.grey,
      ),
      title: Text(
        label,
        style: TextStyle(
          color: isSelected ? Colors.white : Colors.grey[400],
          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
        ),
      ),
    );
  }
}

/// 모델별 가성비 매물 모달
class _ModelDealsModal extends StatefulWidget {
  final String brand;
  final String model;
  final int avgPrice;
  final int medianPrice;
  final int listings;
  final void Function(RecommendedCar car)? onCarViewed;

  const _ModelDealsModal({
    required this.brand,
    required this.model,
    required this.avgPrice,
    required this.medianPrice,
    required this.listings,
    this.onCarViewed,
  });

  @override
  State<_ModelDealsModal> createState() => _ModelDealsModalState();
}

class _ModelDealsModalState extends State<_ModelDealsModal> {
  final ApiService _api = ApiService();
  List<RecommendedCar> _deals = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadDeals();
  }

  Future<void> _loadDeals() async {
    try {
      final deals = await _api.getModelDeals(
        brand: widget.brand,
        model: widget.model,
        limit: 10,
      );
      if (mounted) {
        setState(() {
          _deals = deals;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  /// 매물 클릭 시 상세 분석 모달 표시
  void _showDealAnalysis(RecommendedCar car) {
    // 최근 조회 기록에 추가 (콜백 호출)
    widget.onCarViewed?.call(car);

    // 상세 분석 모달 표시
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DealAnalysisModal(
        deal: car,
        predictedPrice: car.predictedPrice, // 각 매물의 예측가 사용
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.7,
      minChildSize: 0.5,
      maxChildSize: 0.95,
      builder: (context, scrollController) {
        return Container(
          decoration: const BoxDecoration(
            color: Color(0xFF1A1A2E),
            borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
          ),
          child: Column(
            children: [
              // 핸들
              Container(
                margin: const EdgeInsets.symmetric(vertical: 12),
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey[600],
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              // 헤더
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            '${widget.brand} ${widget.model}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 22,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.close, color: Colors.white),
                          onPressed: () => Navigator.pop(context),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '등록 ${widget.listings}건 • 평균 ${widget.avgPrice}만원 • 중앙값 ${widget.medianPrice}만원',
                      style: TextStyle(color: Colors.grey[400], fontSize: 13),
                    ),
                    const SizedBox(height: 16),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 8),
                      decoration: BoxDecoration(
                        color: Colors.green.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.recommend, color: Colors.green, size: 18),
                          SizedBox(width: 6),
                          Text(
                            '가성비 좋은 매물 추천',
                            style: TextStyle(
                                color: Colors.green,
                                fontSize: 13,
                                fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const Divider(color: Colors.white12, height: 24),
              // 매물 리스트
              Expanded(
                child: _isLoading
                    ? const Center(child: CircularProgressIndicator())
                    : _error != null
                        ? Center(
                            child: Text(_error!,
                                style: const TextStyle(color: Colors.red)))
                        : _deals.isEmpty
                            ? Center(
                                child: Text('추천 매물이 없습니다',
                                    style: TextStyle(color: Colors.grey[500])))
                            : ListView.builder(
                                controller: scrollController,
                                padding:
                                    const EdgeInsets.symmetric(horizontal: 16),
                                itemCount: _deals.length,
                                itemBuilder: (context, index) {
                                  final deal = _deals[index];
                                  return _buildDealCard(deal, index + 1);
                                },
                              ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildDealCard(RecommendedCar deal, int rank) {
    final priceDiff = deal.priceDiff;
    final isGood = priceDiff > 0;

    return GestureDetector(
      onTap: () => _showDealAnalysis(deal),
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF252542),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isGood ? Colors.green.withOpacity(0.4) : Colors.white10,
            width: isGood ? 1.5 : 1,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                // 순위 뱃지
                Container(
                  width: 28,
                  height: 28,
                  decoration: BoxDecoration(
                    color:
                        rank <= 3 ? const Color(0xFF6C63FF) : Colors.grey[700],
                    shape: BoxShape.circle,
                  ),
                  child: Center(
                    child: Text(
                      '$rank',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        deal.model,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '${deal.year}년 • ${deal.formattedMileage} • ${deal.fuel}',
                        style: TextStyle(color: Colors.grey[400], fontSize: 12),
                      ),
                    ],
                  ),
                ),
                if (isGood)
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.green.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: const Text(
                      '추천',
                      style: TextStyle(
                          color: Colors.green,
                          fontSize: 11,
                          fontWeight: FontWeight.bold),
                    ),
                  ),
              ],
            ),
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
                      Text(
                        '${deal.actualPrice}만원',
                        style: const TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontWeight: FontWeight.bold),
                      ),
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
                      Text(
                        '${deal.predictedPrice}만원',
                        style: TextStyle(color: Colors.grey[300], fontSize: 16),
                      ),
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
                      '${priceDiff > 0 ? "-" : "+"}${priceDiff.abs()}만원',
                      style: TextStyle(
                        color: priceDiff > 0 ? Colors.green : Colors.red,
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
}
