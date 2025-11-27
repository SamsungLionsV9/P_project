import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'services/api_service.dart';

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
  List<SearchHistory> _recentSearches = [];

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
        _api.getHistory(limit: 5),
      ]);

      setState(() {
        _popularDomestic = results[0] as List<PopularCar>;
        _popularImported = results[1] as List<PopularCar>;
        _recommendations = results[2] as List<RecommendedCar>;
        _recentSearches = results[3] as List<SearchHistory>;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
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
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF6C63FF)))
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

  Widget _buildPopularCard(PopularCar car) {
    return Container(
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
        ],
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

  /// URL로 상세페이지 열기 (모바일 버전 우선)
  Future<void> _openDetailUrl(RecommendedCar car) async {
    // 엔카 모바일 URL 생성 (실제 URL이 있으면 모바일로 변환)
    final searchQuery = Uri.encodeComponent('${car.brand} ${car.model}');
    String url = car.detailUrl ?? 'https://m.encar.com/dc/dc_carsearchlist.do?q=$searchQuery';
    
    // www.encar.com을 m.encar.com으로 변환 (모바일 최적화)
    url = url.replaceAll('www.encar.com', 'm.encar.com');
    url = url.replaceAll('http://', 'https://');  // HTTPS 강제
    
    try {
      final uri = Uri.parse(url);
      if (await canLaunchUrl(uri)) {
        // 인앱 브라우저로 열기 (모바일 환경에 최적화)
        await launchUrl(
          uri, 
          mode: LaunchMode.inAppBrowserView,
          webViewConfiguration: const WebViewConfiguration(
            enableJavaScript: true,
          ),
        );
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('링크를 열 수 없습니다')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('오류: $e')),
        );
      }
    }
  }

  Widget _buildRecommendationCard(RecommendedCar car) {
    final isGood = car.isGoodDeal;
    return GestureDetector(
      onTap: () => _openDetailUrl(car),
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
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
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
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFF6C63FF).withOpacity(0.2),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  car.type == 'domestic' ? '국산' : '수입',
                  style: const TextStyle(color: Color(0xFF6C63FF), fontSize: 12),
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
          const SizedBox(height: 12),
          Row(
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('실제가', style: TextStyle(color: Colors.grey[500], fontSize: 12)),
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
                  Text('예측가', style: TextStyle(color: Colors.grey[500], fontSize: 12)),
                  Text(
                    '${car.predictedPrice}만원',
                    style: TextStyle(color: Colors.grey[400], fontSize: 16),
                  ),
                ],
              ),
              const SizedBox(width: 16),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
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
              Text('탭하여 상세보기', style: TextStyle(color: Colors.grey[500], fontSize: 11)),
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

  /// 최근 조회 탭
  Widget _buildHistoryTab() {
    return _recentSearches.isEmpty
        ? Center(
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
                  '차량을 검색하면 여기에 기록됩니다',
                  style: TextStyle(color: Colors.grey[600], fontSize: 14),
                ),
              ],
            ),
          )
        : ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: _recentSearches.length,
            itemBuilder: (context, index) {
              final history = _recentSearches[index];
              return Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF252542),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: Colors.white10,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Icon(Icons.history, color: Colors.white54),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${history.brand} ${history.model}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            '${history.year}년 • ${(history.mileage / 10000).toStringAsFixed(1)}만km',
                            style: TextStyle(color: Colors.grey[400], fontSize: 13),
                          ),
                        ],
                      ),
                    ),
                    if (history.predictedPrice != null)
                      Text(
                        '${history.predictedPrice!.toStringAsFixed(0)}만원',
                        style: const TextStyle(
                          color: Color(0xFF6C63FF),
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                  ],
                ),
              );
            },
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
