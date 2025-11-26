import 'package:flutter/material.dart';
import 'negotiation_page.dart';
import 'services/api_service.dart';

class ResultPage extends StatefulWidget {
  final SmartAnalysisResult analysisResult;
  final String brand;
  final String model;
  final int year;
  final int mileage;
  final String fuel;

  const ResultPage({
    super.key,
    required this.analysisResult,
    required this.brand,
    required this.model,
    required this.year,
    required this.mileage,
    required this.fuel,
  });

  @override
  State<ResultPage> createState() => _ResultPageState();
}

class _ResultPageState extends State<ResultPage> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final ApiService _api = ApiService();
  
  // 비슷한 차량 데이터
  SimilarResult? _similarResult;
  bool _loadingSimilar = true;
  
  // 편의를 위한 getter
  SmartAnalysisResult get result => widget.analysisResult;
  PredictionResult get prediction => result.prediction;
  TimingResult get timing => result.timing;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadSimilarData();
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
                      const SizedBox(height: 4),
                      const Text(
                        "예상 시세",
                        style: TextStyle(color: Colors.grey, fontSize: 12),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        "${_formatPrice(prediction.predictedPrice)}만원",
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF0066FF),
                        ),
                      ),
                      const SizedBox(height: 16),
                      Divider(color: borderColor),
                      const SizedBox(height: 16),
                      const Text(
                        "합리적 범위",
                        style: TextStyle(color: Colors.grey, fontSize: 12),
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
              labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
              tabs: const [
                Tab(text: "가격 분석"),
                Tab(text: "구매 타이밍"),
                Tab(text: "AI 조언"),
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
                          backgroundColor: isDark ? Colors.grey[800] : Colors.grey[200],
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
                            style: const TextStyle(fontSize: 12, color: Colors.grey),
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
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: textColor),
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
        ],
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
                        color: _getTimingColor(timing.timingScore).withOpacity(0.3),
                        blurRadius: 20,
                        offset: const Offset(0, 8),
                      ),
                    ],
                  ),
                  child: Center(
                    child: Text(
                      "${timing.timingScore.toStringAsFixed(0)}",
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
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: textColor),
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
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: textColor),
                ),
                const SizedBox(height: 16),
                ...timing.reasons.map((reason) => _buildCheckItem(reason, textColor)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCircularIndicator(int score, String label, bool isDark, Color textColor) {
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
        Text(label, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: textColor)),
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

  // Tab 3: AI 조언
  Widget _buildAIAdviceTab(bool isDark, Color cardColor, Color textColor) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          // AI 조언 카드
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
                  child: const Icon(Icons.smart_toy, color: Colors.white, size: 20),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "AI 조언",
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: textColor),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        "이 차량은 시세 대비 적정합니다. 현재 시장에서 동일한 연식과 주행거리를 가진 차량들과 비교했을 때 합리적인 가격대를 형성하고 있습니다.\n\n다만, 구매 전 반드시 차량 상태를 직접 확인하고, 정비 이력과 사고 이력을 꼼꼼히 확인하시기 바랍니다.",
                        style: TextStyle(color: textColor, height: 1.5, fontSize: 14),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // 허위매물 위험도
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
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      "허위매물 위험도",
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: textColor),
                    ),
                    Row(
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: const BoxDecoration(
                            color: Color(0xFF00C853),
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 4),
                        const Text(
                          "낮음",
                          style: TextStyle(
                            color: Color(0xFF00C853),
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                ClipRRect(
                  borderRadius: BorderRadius.circular(10),
                  child: LinearProgressIndicator(
                    value: 0.35,
                    backgroundColor: isDark ? Colors.grey[800] : Colors.grey[100],
                    color: const Color(0xFF00C853),
                    minHeight: 10,
                  ),
                ),
                const SizedBox(height: 8),
                const Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text("위험도 점수", style: TextStyle(color: Colors.grey, fontSize: 12)),
                    Text("35 / 100", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Colors.grey)),
                  ],
                ),
                const SizedBox(height: 16),
                const Text(
                  "가격, 사진, 상세 정보가 일치하며 신뢰할 수 있는 매물입니다. 판매자와 직접 통화하여 추가 확인을 권장합니다.",
                  style: TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // 버튼들
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const NegotiationPage(initialTabIndex: 0),
                      ),
                    );
                  },
                  icon: const Icon(Icons.copy, size: 18),
                  label: const Text("문자 복사"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF0066FF),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const NegotiationPage(initialTabIndex: 1),
                      ),
                    );
                  },
                  icon: const Icon(Icons.phone, size: 18),
                  label: const Text("전화 대본 보기"),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF0066FF),
                    side: const BorderSide(color: Color(0xFF0066FF)),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),

          // 구매 전 확인사항
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF3E2723) : const Color(0xFFFFF8E1),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: isDark ? const Color(0xFF4E342E) : const Color(0xFFFFECB3)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.info_outline, color: Color(0xFFFFAB00), size: 20),
                    const SizedBox(width: 8),
                    Text(
                      "구매 전 확인사항",
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: textColor),
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
              Text("비슷한 차량 데이터가 부족합니다", style: TextStyle(color: Colors.grey[400])),
            ],
          ),
        ),
      );
    }
    
    final similar = _similarResult!;
    final dist = similar.priceDistribution;
    final histogram = similar.histogram;
    
    // 히스토그램 최대값
    final maxCount = histogram.isEmpty ? 1 : histogram.map((h) => h['count'] as int).reduce((a, b) => a > b ? a : b);
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 통계 요약
        if (dist != null) ...[
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildStatItem("최저", "${(dist['min'] as num).toInt()}만", Colors.blue),
              _buildStatItem("중앙", "${(dist['median'] as num).toInt()}만", Colors.green),
              _buildStatItem("최고", "${(dist['max'] as num).toInt()}만", Colors.orange),
            ],
          ),
          const SizedBox(height: 16),
        ],
        
        // 히스토그램
        if (histogram.isNotEmpty) ...[
          SizedBox(
            height: 120,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: histogram.map((bar) {
                final count = bar['count'] as int;
                final rangeMin = bar['range_min'] as int;
                final rangeMax = bar['range_max'] as int;
                final height = maxCount > 0 ? (count / maxCount) * 100 : 0.0;
                final predictedInRange = prediction.predictedPrice >= rangeMin && 
                                         prediction.predictedPrice < rangeMax;
                
                return Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 2),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Text(
                          count > 0 ? "$count" : "",
                          style: TextStyle(fontSize: 10, color: Colors.grey[500]),
                        ),
                        const SizedBox(height: 4),
                        Container(
                          height: height,
                          decoration: BoxDecoration(
                            color: predictedInRange 
                                ? const Color(0xFF0066FF) 
                                : const Color(0xFF0066FF).withOpacity(0.3),
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 8),
          // X축 라벨
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text("${histogram.first['range_min']}만", 
                  style: TextStyle(fontSize: 10, color: Colors.grey[500])),
              Text("${histogram.last['range_max']}만", 
                  style: TextStyle(fontSize: 10, color: Colors.grey[500])),
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
            border: Border.all(color: _getPositionColor(similar.positionColor).withOpacity(0.3)),
          ),
          child: Row(
            children: [
              Icon(Icons.place, color: _getPositionColor(similar.positionColor), size: 20),
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
        Text(value, style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: color)),
      ],
    );
  }
  
  Color _getPositionColor(String color) {
    switch (color) {
      case 'green': return const Color(0xFF00C853);
      case 'blue': return const Color(0xFF0066FF);
      case 'orange': return const Color(0xFFFF9800);
      case 'red': return Colors.red;
      default: return Colors.grey;
    }
  }
}
