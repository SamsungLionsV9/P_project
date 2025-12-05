import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/api_service.dart';
import 'widgets/deal_analysis_modal.dart';
import 'widgets/common/option_badges.dart';
import 'providers/recent_views_provider.dart';

class ResultPage extends StatefulWidget {
  final SmartAnalysisResult analysisResult;
  final String brand;
  final String model;
  final int year;
  final int mileage;
  final String fuel;
  final Map<String, bool>? selectedOptions; // 선택한 옵션 정보
  final String? inspectionGrade; // 성능점검 등급

  const ResultPage({
    super.key,
    required this.analysisResult,
    required this.brand,
    required this.model,
    required this.year,
    required this.mileage,
    required this.fuel,
    this.selectedOptions,
    this.inspectionGrade,
  });

  @override
  State<ResultPage> createState() => _ResultPageState();
}

class _ResultPageState extends State<ResultPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final ApiService _api = ApiService();

  // 비슷한 차량 데이터
  SimilarResult? _similarResult;
  bool _loadingSimilar = true;

  // 실매물 데이터
  List<RecommendedCar> _realDeals = [];
  bool _loadingDeals = true;

  // 편의를 위한 getter
  SmartAnalysisResult get result => widget.analysisResult;
  PredictionResult get prediction => result.prediction;
  TimingResult get timing => result.timing;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadSimilarData();
    _loadRealDeals();
  }

  Future<void> _loadSimilarData() async {
    try {
      final similar = await _api.getSimilar(
        brand: widget.brand,
        model: widget.model,
        year: widget.year,
        mileage: widget.mileage,
        predictedPrice: prediction.predictedPrice,
      );
      setState(() {
        _similarResult = similar;
        _loadingSimilar = false;
      });
    } catch (e) {
      setState(() => _loadingSimilar = false);
    }
  }

  Future<void> _loadRealDeals() async {
    try {
      final deals = await _api.getModelDeals(
        brand: widget.brand,
        model: widget.model,
        limit: 5,
      );
      setState(() {
        _realDeals = deals;
        _loadingDeals = false;
      });
    } catch (e) {
      setState(() => _loadingDeals = false);
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardColor = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final textColor = isDark ? Colors.white : Colors.black;
    final subTextColor = isDark ? Colors.grey[400] : Colors.grey[600];
    final borderColor = isDark ? Colors.grey[800]! : Colors.grey[100]!;

    return Scaffold(
      // backgroundColor uses theme default
      appBar: AppBar(
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios, color: textColor),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          "중고차 시세 예측 결과",
          style: TextStyle(
            color: textColor,
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        centerTitle: true,
      ),
      body: Column(
        children: [
          // 1. 상단 고정 영역 (예상 시세)
          Container(
            color: Theme.of(context).scaffoldBackgroundColor,
            padding: const EdgeInsets.fromLTRB(20, 10, 20, 20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(20),
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
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // 차량 정보
                      Text(
                        "${widget.brand} ${widget.model} (${widget.year}년식)",
                        style: TextStyle(color: subTextColor, fontSize: 12),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  "예상 시세",
                                  style: TextStyle(
                                      color: Colors.grey, fontSize: 12),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  "${_formatPrice(prediction.predictedPrice)}만원",
                                  style: const TextStyle(
                                    fontSize: 22,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF0066FF),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Container(
                            width: 1,
                            height: 40,
                            color: borderColor,
                            margin: const EdgeInsets.symmetric(horizontal: 16),
                          ),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  "합리적 범위",
                                  style: TextStyle(
                                      color: Colors.grey, fontSize: 12),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  "${_formatPrice(prediction.priceRange[0])} ~ ${_formatPrice(prediction.priceRange[1])}만원",
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                    color: textColor,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // 2. 탭 바
          Container(
            color: Theme.of(context).scaffoldBackgroundColor,
            child: TabBar(
              controller: _tabController,
              labelColor: const Color(0xFF0066FF),
              unselectedLabelColor: Colors.grey[400],
              indicatorColor: const Color(0xFF0066FF),
              indicatorWeight: 3,
              labelStyle:
                  const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
              tabs: const [
                Tab(text: "가격 분석"),
                Tab(text: "구매 타이밍"),
                Tab(text: "시장 조언"),
              ],
            ),
          ),

          // 3. 탭 뷰
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildPriceAnalysisTab(isDark, cardColor, textColor),
                _buildBuyingTimingTab(isDark, cardColor, textColor),
                _buildAIAdviceTab(isDark, cardColor, textColor),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // Tab 1: 가격 분석
  Widget _buildPriceAnalysisTab(bool isDark, Color cardColor, Color textColor) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          // 신뢰도 카드
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Column(
              children: [
                const Text("신뢰도", style: TextStyle(color: Colors.grey)),
                const SizedBox(height: 20),
                SizedBox(
                  height: 150,
                  width: 150,
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
                      SizedBox(
                        width: 120,
                        height: 120,
                        child: CircularProgressIndicator(
                          value: prediction.confidence / 100,
                          strokeWidth: 12,
                          backgroundColor:
                              isDark ? Colors.grey[800] : Colors.grey[200],
                          color: _getConfidenceColor(prediction.confidence),
                        ),
                      ),
                      Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            "${prediction.confidence.toStringAsFixed(0)}%",
                            style: TextStyle(
                              fontSize: 32,
                              fontWeight: FontWeight.bold,
                              color: _getConfidenceColor(prediction.confidence),
                            ),
                          ),
                          Text(
                            _getConfidenceLabel(prediction.confidence),
                            style: const TextStyle(
                                fontSize: 12, color: Colors.grey),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // 비슷한 차량 가격 분포
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "비슷한 차량 가격 분포",
                  style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: textColor),
                ),
                const Text(
                  "최근 3개월 거래 데이터 기준",
                  style: TextStyle(fontSize: 12, color: Colors.grey),
                ),
                const SizedBox(height: 20),
                _buildSimilarDistribution(cardColor, textColor),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // 실매물 섹션
          _buildRealDealsSection(cardColor, textColor, isDark),
        ],
      ),
    );
  }

  /// 실매물 섹션 위젯
  Widget _buildRealDealsSection(Color cardColor, Color textColor, bool isDark) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(Icons.directions_car,
                      color: Color(0xFF0066FF), size: 20),
                  const SizedBox(width: 8),
                  Text(
                    "이 조건의 실매물",
                    style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: textColor),
                  ),
                ],
              ),
              if (_realDeals.isNotEmpty)
                Text(
                  "${_realDeals.length}건",
                  style: TextStyle(color: Colors.grey[500], fontSize: 12),
                ),
            ],
          ),

          // 예측 조건 표시 (옵션, 성능점검 등)
          if (widget.selectedOptions != null ||
              widget.inspectionGrade != null) ...[
            const SizedBox(height: 12),
            _buildPredictionConditions(isDark),
          ],

          const SizedBox(height: 16),

          if (_loadingDeals)
            const SizedBox(
              height: 100,
              child: Center(child: CircularProgressIndicator()),
            )
          else if (_realDeals.isEmpty)
            SizedBox(
              height: 80,
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.search_off, color: Colors.grey[400], size: 32),
                    const SizedBox(height: 8),
                    Text("매물 데이터가 없습니다",
                        style: TextStyle(color: Colors.grey[400])),
                  ],
                ),
              ),
            )
          else
            Column(
              children: _realDeals
                  .map((deal) => _buildDealCard(deal, textColor, isDark))
                  .toList(),
            ),
        ],
      ),
    );
  }

  /// 예측 조건 표시 위젯 (선택한 옵션, 성능점검 등급)
  Widget _buildPredictionConditions(bool isDark) {
    final options = widget.selectedOptions ?? {};
    final grade = widget.inspectionGrade;

    // 활성화된 옵션만 필터
    final activeOptions = <String>[];
    if (options['sunroof'] == true) activeOptions.add('선루프');
    if (options['navigation'] == true) activeOptions.add('내비게이션');
    if (options['leatherSeat'] == true) activeOptions.add('가죽시트');
    if (options['smartKey'] == true) activeOptions.add('스마트키');
    if (options['rearCamera'] == true) activeOptions.add('후방카메라');

    // 성능점검 등급 텍스트
    String gradeText = '';
    if (grade == 'excellent') {
      gradeText = '성능점검 ★★★★★';
    } else if (grade == 'good') {
      gradeText = '성능점검 ★★★★';
    } else if (grade == 'average') {
      gradeText = '성능점검 ★★★';
    } else if (grade == 'poor') {
      gradeText = '성능점검 ★★';
    }

    if (activeOptions.isEmpty && gradeText.isEmpty) {
      return const SizedBox.shrink();
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: isDark
            ? Colors.blue.withOpacity(0.1)
            : Colors.blue.withOpacity(0.05),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.withOpacity(0.2)),
      ),
      child: Row(
        children: [
          Icon(Icons.info_outline, size: 16, color: Colors.blue[400]),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              '예측 조건: ${[
                '${widget.year}년식',
                widget.fuel,
                if (gradeText.isNotEmpty) gradeText,
                ...activeOptions,
              ].join(' · ')}',
              style: TextStyle(
                color: Colors.blue[400],
                fontSize: 12,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  /// 개별 매물 카드
  Widget _buildDealCard(RecommendedCar deal, Color textColor, bool isDark) {
    // 매물의 고유 조건 기준 예측가와 비교 (연식, 연료 등 반영)
    final priceDiff = deal.predictedPrice - deal.actualPrice;
    final isGood = priceDiff > 0;

    return GestureDetector(
      onTap: () => _showDealAnalysisModal(deal),
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isDark ? const Color(0xFF2A2A2A) : Colors.grey[50],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isGood
                ? Colors.green.withOpacity(0.3)
                : Colors.grey.withOpacity(0.2),
          ),
        ),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      if (isGood)
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 6, vertical: 2),
                          margin: const EdgeInsets.only(right: 8),
                          decoration: BoxDecoration(
                            color: Colors.green.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: const Text(
                            "🔥 가성비",
                            style: TextStyle(color: Colors.green, fontSize: 10),
                          ),
                        ),
                      Expanded(
                        child: Text(
                          "${deal.brand} ${deal.model}",
                          style: TextStyle(
                            color: textColor,
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    "${deal.year}년 • ${(deal.mileage / 10000).toStringAsFixed(1)}만km • ${deal.fuel}",
                    style: TextStyle(color: Colors.grey[500], fontSize: 12),
                  ),
                  // 옵션 정보 표시 (공통 위젯 사용)
                  if (deal.options != null) ...[
                    const SizedBox(height: 6),
                    OptionBadges(options: deal.options!, compact: true),
                  ],
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  "${_formatPrice(deal.actualPrice.toDouble())}만원",
                  style: TextStyle(
                    color: textColor,
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                Text(
                  isGood
                      ? "예측가 대비 -${priceDiff.abs()}만원"
                      : "예측가 대비 +${priceDiff.abs()}만원",
                  style: TextStyle(
                    color: isGood ? Colors.green : Colors.red,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
            const SizedBox(width: 8),
            Icon(Icons.chevron_right, color: Colors.grey[400], size: 20),
          ],
        ),
      ),
    );
  }

  /// 개별 매물 분석 모달 표시
  Future<void> _showDealAnalysisModal(RecommendedCar deal) async {
    // 최근 조회에 추가 (분석 페이지에서 클릭 = source: 'analysis')
    final dealWithSource = deal.copyWith(source: 'analysis');
    context.read<RecentViewsProvider>().addRecentCar(dealWithSource);

    // 매물의 고유 조건(연식, 연료 등)에 맞는 예측가 사용
    // deal.predictedPrice는 해당 매물의 실제 조건으로 계산된 예측가
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

  // Tab 2: 구매 타이밍
  Widget _buildBuyingTimingTab(bool isDark, Color cardColor, Color textColor) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          // 구매 적기 카드
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(30),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Column(
              children: [
                Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: _getTimingColor(timing.timingScore),
                    boxShadow: [
                      BoxShadow(
                        color: _getTimingColor(timing.timingScore)
                            .withOpacity(0.3),
                        blurRadius: 20,
                        offset: const Offset(0, 8),
                      ),
                    ],
                  ),
                  child: Center(
                    child: Text(
                      timing.timingScore.toStringAsFixed(0),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                Text(
                  timing.decision,
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: _getTimingColor(timing.timingScore),
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  _getTimingDescription(timing.timingScore),
                  style: const TextStyle(color: Colors.grey),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // 타이밍 지표
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "타이밍 지표",
                  style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: textColor),
                ),
                const SizedBox(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildCircularIndicator(
                      (timing.breakdown['macro'] ?? 70).toInt(),
                      "거시경제",
                      isDark,
                      textColor,
                    ),
                    _buildCircularIndicator(
                      (timing.breakdown['trend'] ?? 70).toInt(),
                      "트렌드",
                      isDark,
                      textColor,
                    ),
                    _buildCircularIndicator(
                      (timing.breakdown['new_car'] ?? 70).toInt(),
                      "신차 일정",
                      isDark,
                      textColor,
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // 상세 분석
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "상세 분석",
                  style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: textColor),
                ),
                const SizedBox(height: 16),
                ...timing.reasons
                    .map((reason) => _buildCheckItem(reason, textColor)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCircularIndicator(
      int score, String label, bool isDark, Color textColor) {
    final color = _getScoreColor(score);
    return Column(
      children: [
        SizedBox(
          width: 80,
          height: 80,
          child: Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 70,
                height: 70,
                child: CircularProgressIndicator(
                  value: score / 100,
                  strokeWidth: 6,
                  backgroundColor: isDark ? Colors.grey[800] : Colors.grey[100],
                  color: color,
                ),
              ),
              Text(
                score.toString(),
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 8),
        Text(label,
            style: TextStyle(
                fontWeight: FontWeight.bold, fontSize: 14, color: textColor)),
        const Text("/ 100", style: TextStyle(color: Colors.grey, fontSize: 10)),
      ],
    );
  }

  Widget _buildCheckItem(String text, Color textColor) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          const Icon(Icons.check, color: Color(0xFF00C853), size: 20),
          const SizedBox(width: 8),
          Text(text, style: TextStyle(fontSize: 14, color: textColor)),
        ],
      ),
    );
  }

  // Tab 3: 시장 조언 (개별 매물이 아닌 시장 전체 관점)
  Widget _buildAIAdviceTab(bool isDark, Color cardColor, Color textColor) {
    // 시장 상황 분석
    final priceAdvice = _getMarketPriceAdvice();
    final timingAdvice = _getMarketTimingAdvice();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          // 시장 조언 카드
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: const BoxDecoration(
                    color: Color(0xFF0066FF),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.analytics,
                      color: Colors.white, size: 20),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "시장 조언",
                        style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                            color: textColor),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        priceAdvice,
                        style: TextStyle(
                            color: textColor, height: 1.5, fontSize: 14),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // 추천 예산 범위
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.savings,
                        color: Color(0xFF0066FF), size: 20),
                    const SizedBox(width: 8),
                    Text(
                      "추천 예산 범위",
                      style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: textColor),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                _buildBudgetRange(textColor, isDark),
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: isDark
                        ? Colors.blue.withOpacity(0.1)
                        : const Color(0xFFE3F2FD),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.lightbulb,
                          color: Color(0xFF0066FF), size: 16),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          "예측가의 90~110% 범위에서 협상을 시작하세요",
                          style: TextStyle(color: textColor, fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // 구매 타이밍 요약
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.schedule,
                        color: Color(0xFF00C853), size: 20),
                    const SizedBox(width: 8),
                    Text(
                      "타이밍 요약",
                      style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: textColor),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  timingAdvice,
                  style: TextStyle(color: textColor, height: 1.5, fontSize: 14),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // 구매 전 확인사항
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF3E2723) : const Color(0xFFFFF8E1),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                  color: isDark
                      ? const Color(0xFF4E342E)
                      : const Color(0xFFFFECB3)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.info_outline,
                        color: Color(0xFFFFAB00), size: 20),
                    const SizedBox(width: 8),
                    Text(
                      "구매 전 확인사항",
                      style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                          color: textColor),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                _buildWarningItem("실물 차량 상태 점검", textColor),
                _buildWarningItem("사고 이력 및 정비 기록 확인", textColor),
                _buildWarningItem("판매자 신원 및 소유권 확인", textColor),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWarningItem(String text, Color textColor) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8, left: 28),
      child: Row(
        children: [
          Container(
            width: 4,
            height: 4,
            decoration: const BoxDecoration(
              color: Color(0xFFFFAB00),
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 8),
          Text(text, style: TextStyle(fontSize: 13, color: textColor)),
        ],
      ),
    );
  }

  // ========== 헬퍼 메서드 ==========

  /// 가격 포맷팅 (1234.5 → "1,235")
  String _formatPrice(double price) {
    return price.toStringAsFixed(0).replaceAllMapped(
          RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
          (Match m) => '${m[1]},',
        );
  }

  /// 신뢰도에 따른 색상
  Color _getConfidenceColor(double confidence) {
    if (confidence >= 80) return const Color(0xFF00C853);
    if (confidence >= 60) return const Color(0xFF0066FF);
    if (confidence >= 40) return const Color(0xFFFFAB00);
    return Colors.red;
  }

  /// 신뢰도 라벨
  String _getConfidenceLabel(double confidence) {
    if (confidence >= 80) return '매우 높음';
    if (confidence >= 60) return '높음';
    if (confidence >= 40) return '보통';
    return '낮음';
  }

  /// 타이밍 점수에 따른 색상
  Color _getTimingColor(double score) {
    if (score >= 70) return const Color(0xFF00C853);
    if (score >= 50) return const Color(0xFFFFAB00);
    return Colors.red;
  }

  /// 타이밍 설명
  String _getTimingDescription(double score) {
    if (score >= 70) return '구매하기 좋은 타이밍입니다';
    if (score >= 50) return '조금 더 기다려보세요';
    return '구매를 미루는 것이 좋습니다';
  }

  /// 점수에 따른 색상
  Color _getScoreColor(int score) {
    if (score >= 70) return const Color(0xFF00C853);
    if (score >= 50) return const Color(0xFFFFAB00);
    return Colors.red;
  }

  /// 시장 가격 조언 생성
  String _getMarketPriceAdvice() {
    final price = prediction.predictedPrice;
    final confidence = prediction.confidence;
    final brand = widget.brand;
    final model = widget.model;

    String advice = "$brand $model ${widget.year}년식의 ";

    if (confidence >= 80) {
      advice += "예상 시세는 ${_formatPrice(price)}만원입니다. ";
      advice += "동일 조건의 차량 데이터가 충분하여 신뢰도가 높습니다.\n\n";
    } else if (confidence >= 60) {
      advice += "예상 시세는 ${_formatPrice(price)}만원입니다. ";
      advice += "유사 차량 데이터를 기반으로 분석했습니다.\n\n";
    } else {
      advice += "예상 시세는 약 ${_formatPrice(price)}만원입니다. ";
      advice += "데이터가 부족하여 참고용으로 활용하세요.\n\n";
    }

    advice += "실제 매물을 확인할 때는 차량 상태, 옵션, 사고 이력에 따라 가격이 달라질 수 있습니다.";

    return advice;
  }

  /// 시장 타이밍 조언 생성
  String _getMarketTimingAdvice() {
    final score = timing.timingScore;

    if (score >= 70) {
      return "현재는 이 모델을 구매하기 좋은 시기입니다. "
          "시장 가격이 안정적이며, 매물도 충분합니다. "
          "마음에 드는 차량이 있다면 적극 검토해보세요.";
    } else if (score >= 50) {
      return "현재 시장 상황은 보통입니다. "
          "급하지 않다면 다음 달까지 기다려보는 것도 방법입니다. "
          "가격 변동을 지켜보며 결정하세요.";
    } else {
      return "현재는 구매를 서두르지 않는 것이 좋습니다. "
          "시장 상황이 안정될 때까지 기다려보세요. "
          "조금 더 기다려보세요.";
    }
  }

  /// 추천 예산 범위 위젯
  Widget _buildBudgetRange(Color textColor, bool isDark) {
    final predicted = prediction.predictedPrice;
    final minBudget = (predicted * 0.9).round();
    final maxBudget = (predicted * 1.1).round();

    return Row(
      children: [
        Expanded(
          child: Column(
            children: [
              Text("최소",
                  style: TextStyle(color: Colors.grey[500], fontSize: 12)),
              const SizedBox(height: 4),
              Text(
                "${_formatPrice(minBudget.toDouble())}만원",
                style: const TextStyle(
                  color: Color(0xFF0066FF),
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
        Container(
          height: 40,
          width: 1,
          color: isDark ? Colors.grey[700] : Colors.grey[300],
        ),
        Expanded(
          child: Column(
            children: [
              Text("예측가",
                  style: TextStyle(color: Colors.grey[500], fontSize: 12)),
              const SizedBox(height: 4),
              Text(
                "${_formatPrice(predicted)}만원",
                style: TextStyle(
                  color: textColor,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
        Container(
          height: 40,
          width: 1,
          color: isDark ? Colors.grey[700] : Colors.grey[300],
        ),
        Expanded(
          child: Column(
            children: [
              Text("최대",
                  style: TextStyle(color: Colors.grey[500], fontSize: 12)),
              const SizedBox(height: 4),
              Text(
                "${_formatPrice(maxBudget.toDouble())}만원",
                style: const TextStyle(
                  color: Color(0xFFE53935),
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  /// 비슷한 차량 분포 위젯
  Widget _buildSimilarDistribution(Color cardColor, Color textColor) {
    if (_loadingSimilar) {
      return const SizedBox(
        height: 180,
        child: Center(child: CircularProgressIndicator()),
      );
    }

    if (_similarResult == null || _similarResult!.similarCount == 0) {
      return SizedBox(
        height: 100,
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.search_off, color: Colors.grey[400], size: 32),
              const SizedBox(height: 8),
              Text("비슷한 차량 데이터가 부족합니다",
                  style: TextStyle(color: Colors.grey[400])),
            ],
          ),
        ),
      );
    }

    final similar = _similarResult!;
    final dist = similar.priceDistribution;
    final histogram = similar.histogram;

    // 히스토그램 최대 10개로 제한 (너무 많으면 UI 깨짐)
    final limitedHistogram =
        histogram.length > 10 ? histogram.sublist(0, 10) : histogram;

    // 히스토그램 최대값
    final maxCount = limitedHistogram.isEmpty
        ? 1
        : limitedHistogram
            .map((h) => h['count'] as int)
            .reduce((a, b) => a > b ? a : b);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 통계 요약
        if (dist != null) ...[
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildStatItem(
                  "최저", "${(dist['min'] as num).toInt()}만", Colors.blue),
              _buildStatItem(
                  "중앙", "${(dist['median'] as num).toInt()}만", Colors.green),
              _buildStatItem(
                  "최고", "${(dist['max'] as num).toInt()}만", Colors.orange),
            ],
          ),
          const SizedBox(height: 16),
        ],

        // 히스토그램 (최대 10개)
        if (limitedHistogram.isNotEmpty) ...[
          SizedBox(
            height: 140,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: limitedHistogram.map((bar) {
                final count = bar['count'] as int;
                final rangeMin = bar['range_min'] as int;
                final rangeMax = bar['range_max'] as int;
                final barHeight = maxCount > 0 ? (count / maxCount) * 100 : 0.0;
                final predictedInRange =
                    prediction.predictedPrice >= rangeMin &&
                        prediction.predictedPrice < rangeMax;

                return Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 1),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        // 숫자 (5 이상만 표시)
                        if (count >= 5)
                          Text(
                            "$count",
                            style:
                                TextStyle(fontSize: 8, color: Colors.grey[500]),
                          ),
                        const SizedBox(height: 2),
                        Container(
                          height: barHeight.clamp(4.0, 100.0),
                          constraints: const BoxConstraints(minHeight: 4),
                          decoration: BoxDecoration(
                            color: predictedInRange
                                ? const Color(0xFF0066FF)
                                : const Color(0xFF0066FF).withOpacity(0.3),
                            borderRadius: BorderRadius.circular(3),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 4),
          // X축 라벨
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text("${limitedHistogram.first['range_min']}만",
                  style: TextStyle(fontSize: 9, color: Colors.grey[500])),
              Text("${limitedHistogram.last['range_max']}만",
                  style: TextStyle(fontSize: 9, color: Colors.grey[500])),
            ],
          ),
        ],

        const SizedBox(height: 16),

        // 내 위치
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: _getPositionColor(similar.positionColor).withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
                color:
                    _getPositionColor(similar.positionColor).withOpacity(0.3)),
          ),
          child: Row(
            children: [
              Icon(Icons.place,
                  color: _getPositionColor(similar.positionColor), size: 20),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  "예측가 ${_formatPrice(prediction.predictedPrice)}만원은 ${similar.yourPosition}",
                  style: TextStyle(
                    color: _getPositionColor(similar.positionColor),
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 8),
        Text(
          "비교 대상: ${similar.similarCount}대",
          style: TextStyle(fontSize: 12, color: Colors.grey[500]),
        ),
      ],
    );
  }

  Widget _buildStatItem(String label, String value, Color color) {
    return Column(
      children: [
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[500])),
        const SizedBox(height: 4),
        Text(value,
            style: TextStyle(
                fontSize: 16, fontWeight: FontWeight.bold, color: color)),
      ],
    );
  }

  Color _getPositionColor(String color) {
    switch (color) {
      case 'green':
        return const Color(0xFF00C853);
      case 'blue':
        return const Color(0xFF0066FF);
      case 'orange':
        return const Color(0xFFFF9800);
      case 'red':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
}
