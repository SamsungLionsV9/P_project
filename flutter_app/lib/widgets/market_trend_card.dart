import 'package:flutter/material.dart';
import '../services/api_service.dart';

/// 오늘의 구매 지수 카드 - 실제 API 연동 버전
class MarketTrendCard extends StatefulWidget {
  const MarketTrendCard({super.key});

  @override
  State<MarketTrendCard> createState() => _MarketTrendCardState();
}

class _MarketTrendCardState extends State<MarketTrendCard> {
  final ApiService _apiService = ApiService();

  int _score = 0;
  String _label = '분석 중...';
  String _description = '시장 데이터를 분석하고 있습니다';
  bool _isLoading = true;
  bool _hasError = false;

  @override
  void initState() {
    super.initState();
    _loadMarketTrend();
  }

  Future<void> _loadMarketTrend() async {
    try {
      // 인기 차종들의 타이밍 점수 평균으로 시장 지수 계산
      final popularModels = ['아반떼', '소나타', 'K5', 'G80', '그랜저'];
      List<int> scores = [];

      for (final model in popularModels) {
        try {
          final timing = await _apiService.analyzeTiming(model);
          scores.add(timing.timingScore.toInt());
        } catch (e) {
          // 개별 모델 에러는 무시
        }
      }

      if (scores.isNotEmpty) {
        final avgScore =
            (scores.reduce((a, b) => a + b) / scores.length).round();

        if (mounted) {
          setState(() {
            _score = avgScore;
            _label = _getScoreLabel(avgScore);
            _description = _getScoreDescription(avgScore);
            _isLoading = false;
          });
        }
      } else {
        // API 호출 실패 시 시장 데이터 기반 fallback
        await _loadFallbackScore();
      }
    } catch (e) {
      await _loadFallbackScore();
    }
  }

  Future<void> _loadFallbackScore() async {
    // 추천 데이터에서 좋은 딜 비율로 계산
    try {
      final recommendations = await _apiService.getRecommendations(limit: 20);
      if (recommendations.isNotEmpty) {
        final goodDeals = recommendations.where((c) => c.isGoodDeal).length;
        final ratio = goodDeals / recommendations.length;
        final calculatedScore = (ratio * 100).round().clamp(30, 95);

        if (mounted) {
          setState(() {
            _score = calculatedScore;
            _label = _getScoreLabel(calculatedScore);
            _description = '현재 매물 중 ${(ratio * 100).toInt()}%가\n좋은 딜로 분석됐어요';
            _isLoading = false;
          });
        }
      } else {
        _setDefaultState();
      }
    } catch (e) {
      _setDefaultState();
    }
  }

  void _setDefaultState() {
    if (mounted) {
      setState(() {
        _score = 65;
        _label = '보통';
        _description = '데이터를 불러올 수 없습니다';
        _isLoading = false;
        _hasError = true;
      });
    }
  }

  String _getScoreLabel(int score) {
    if (score >= 80) return '매우 좋음';
    if (score >= 70) return '좋음';
    if (score >= 55) return '보통';
    if (score >= 40) return '주의';
    return '비추천';
  }

  String _getScoreDescription(int score) {
    if (score >= 80) return '지금이 구매하기\n가장 좋은 시기예요!';
    if (score >= 70) return '전반적으로\n좋은 구매 타이밍이에요';
    if (score >= 55) return '평소와 비슷한\n시장 상황이에요';
    if (score >= 40) return '조금 더 기다려보는 게\n좋을 수 있어요';
    return '지금은 구매를\n권장하지 않아요';
  }

  Color _getScoreColor(int score) {
    if (score >= 80) return const Color(0xFF00C853);
    if (score >= 70) return const Color(0xFF0066FF);
    if (score >= 55) return const Color(0xFFFFA726);
    if (score >= 40) return const Color(0xFFFF7043);
    return const Color(0xFFE53935);
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardColor = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final subTextColor = isDark ? Colors.grey[400] : Colors.grey[600];
    final accentColor =
        _isLoading ? const Color(0xFF0066FF) : _getScoreColor(_score);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
        border: Border.all(
          color: isDark ? Colors.grey[800]! : Colors.grey[100]!,
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: accentColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  "오늘의 구매 지수",
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    color: accentColor,
                  ),
                ),
              ),
              if (_isLoading)
                SizedBox(
                  width: 14,
                  height: 14,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(accentColor),
                  ),
                )
              else if (_hasError)
                const Icon(Icons.error_outline, size: 16, color: Colors.orange)
              else
                Icon(Icons.trending_up, size: 16, color: accentColor),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              SizedBox(
                width: 40,
                height: 40,
                child: _isLoading
                    ? CircularProgressIndicator(
                        strokeWidth: 4,
                        backgroundColor:
                            isDark ? Colors.grey[800] : Colors.grey[200],
                        valueColor: AlwaysStoppedAnimation<Color>(
                            accentColor.withOpacity(0.3)),
                        strokeCap: StrokeCap.round,
                      )
                    : CircularProgressIndicator(
                        value: _score / 100,
                        strokeWidth: 4,
                        backgroundColor:
                            isDark ? Colors.grey[800] : Colors.grey[200],
                        valueColor: AlwaysStoppedAnimation<Color>(accentColor),
                        strokeCap: StrokeCap.round,
                      ),
              ),
              const SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _isLoading ? "--점" : "$_score점",
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: accentColor,
                    ),
                  ),
                  Text(
                    _label,
                    style: TextStyle(
                      fontSize: 11,
                      color: subTextColor,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            _description,
            style: TextStyle(
              fontSize: 12,
              color: subTextColor,
              height: 1.3,
            ),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}
