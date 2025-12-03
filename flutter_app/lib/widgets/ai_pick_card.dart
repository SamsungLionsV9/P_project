import 'package:flutter/material.dart';
import '../services/api_service.dart';

/// AI 추천 픽 카드 - 실제 API 연동 버전
class AiPickCard extends StatefulWidget {
  final Function(RecommendedCar car)? onTap;

  const AiPickCard({super.key, this.onTap});

  @override
  State<AiPickCard> createState() => _AiPickCardState();
}

class _AiPickCardState extends State<AiPickCard> {
  final ApiService _apiService = ApiService();
  
  RecommendedCar? _topPick;
  bool _isLoading = true;
  bool _hasError = false;
  int _priceDropPercent = 0;

  @override
  void initState() {
    super.initState();
    _loadAiPick();
  }

  Future<void> _loadAiPick() async {
    try {
      // 추천 차량 중 가장 점수 높은 것을 가져옴
      final recommendations = await _apiService.getRecommendations(
        category: 'all',
        limit: 20,
      );
      
      if (recommendations.isNotEmpty) {
        // 점수 기준 정렬 후 가장 높은 것 선택
        recommendations.sort((a, b) => b.score.compareTo(a.score));
        final topPick = recommendations.first;
        
        // 가격 하락률 계산 (예측가 대비 실제가가 낮으면 좋은 딜)
        final priceDrop = topPick.predictedPrice > 0
            ? ((topPick.predictedPrice - topPick.actualPrice) / topPick.predictedPrice * 100).round()
            : 0;
        
        if (mounted) {
          setState(() {
            _topPick = topPick;
            _priceDropPercent = priceDrop.clamp(-50, 50);
            _isLoading = false;
          });
        }
      } else {
        _setDefaultState();
      }
    } catch (e) {
      debugPrint('AI Pick 로드 에러: $e');
      _setDefaultState();
    }
  }

  void _setDefaultState() {
    if (mounted) {
      setState(() {
        _isLoading = false;
        _hasError = true;
      });
    }
  }

  String _getScoreEmoji(double score) {
    if (score >= 90) return '🚀';
    if (score >= 80) return '🔥';
    if (score >= 70) return '✨';
    if (score >= 60) return '👍';
    return '💡';
  }

  String _getPriceDescription() {
    if (_priceDropPercent > 0) {
      return '시세보다\n$_priceDropPercent% 저렴해요';
    } else if (_priceDropPercent < 0) {
      return '시세와\n비슷한 가격이에요';
    } else {
      return '가성비 좋은\n추천 매물이에요';
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardColor = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final textColor = isDark ? Colors.white : Colors.black87;
    final subTextColor = isDark ? Colors.grey[400] : Colors.grey[600];
    const accentColor = Color(0xFF0066FF);

    return GestureDetector(
      onTap: () {
        if (_topPick != null && widget.onTap != null) {
          widget.onTap!(_topPick!);
        }
      },
      child: Container(
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
        child: _isLoading
            ? _buildLoadingState(subTextColor)
            : _hasError
                ? _buildErrorState(textColor, subTextColor)
                : _buildContentState(textColor, subTextColor, accentColor),
      ),
    );
  }

  Widget _buildLoadingState(Color? subTextColor) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.purple.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Text(
                "AI 추천 픽",
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  color: Colors.purple,
                ),
              ),
            ),
            SizedBox(
              width: 14,
              height: 14,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(Colors.purple[300]!),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Center(
          child: Column(
            children: [
              SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.purple[300]!),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                "추천 분석 중...",
                style: TextStyle(fontSize: 12, color: subTextColor),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildErrorState(Color textColor, Color? subTextColor) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.purple.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Text(
                "AI 추천 픽",
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  color: Colors.purple,
                ),
              ),
            ),
            const Icon(Icons.refresh, size: 16, color: Colors.purple),
          ],
        ),
        const SizedBox(height: 16),
        Center(
          child: Column(
            children: [
              Icon(Icons.auto_awesome, size: 28, color: Colors.grey[400]),
              const SizedBox(height: 8),
              Text(
                "추천을 불러올 수 없습니다",
                style: TextStyle(fontSize: 12, color: subTextColor),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildContentState(Color textColor, Color? subTextColor, Color accentColor) {
    final car = _topPick!;
    final displayName = '${car.brand} ${car.model}';
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.purple.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Text(
                "AI 추천 픽",
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  color: Colors.purple,
                ),
              ),
            ),
            Icon(Icons.auto_awesome, size: 16, color: Colors.purple[300]),
          ],
        ),
        const SizedBox(height: 12),
        Text(
          displayName,
          style: TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.bold,
            color: textColor,
          ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        const SizedBox(height: 4),
        Row(
          children: [
            Text(
              "${car.score.toInt()}점",
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: accentColor,
              ),
            ),
            const SizedBox(width: 4),
            Text(
              _getScoreEmoji(car.score),
              style: const TextStyle(fontSize: 14),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          _getPriceDescription(),
          style: TextStyle(
            fontSize: 12,
            color: subTextColor,
            height: 1.3,
          ),
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
      ],
    );
  }
}
