import 'package:flutter/material.dart';
import 'package:percent_indicator/circular_percent_indicator.dart';
import 'package:animate_do/animate_do.dart';
import '../services/api_service.dart';
import 'common/hover_card.dart';

/// ★ 전문적인 구매 타이밍 카드 (토스/당근마켓 스타일)
/// 
/// 특징:
/// - 원형 게이지로 점수 시각화
/// - 경제지표 실시간 표시 (금리/환율/유가)
/// - 추세 화살표 (▲/▼)
/// - 그림자/깊이감 강화
/// - 애니메이션 효과
class ProfessionalTimingCard extends StatelessWidget {
  final MarketTimingResult timing;
  final VoidCallback? onTap;
  final bool isLoading;

  const ProfessionalTimingCard({
    super.key,
    required this.timing,
    this.onTap,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return _buildLoadingState();
    }

    final scoreColor = timing.getScoreColor();
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor = isDark ? Colors.white : Colors.black87;

    return FadeInUp(
      duration: const Duration(milliseconds: 600),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        child: HoverCard(
          onTap: onTap,
          hoverScale: 1.02,
          hoverElevation: 20,
          borderRadius: BorderRadius.circular(24),
          backgroundColor: isDark ? const Color(0xFF1E1E1E) : Colors.white,
          child: Container(
            width: double.infinity,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(24),
            ),
            child: Column(
            children: [
              // 상단: 브랜딩 헤더
              _buildHeader(scoreColor, textColor),
              
              // 중앙: 점수 게이지 + 경제지표
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 16, 20, 20),
                child: Row(
                  children: [
                    // 왼쪽: 원형 게이지
                    _buildCircularGauge(scoreColor, textColor),
                    
                    const SizedBox(width: 24),
                    
                    // 오른쪽: 경제지표 리스트
                    Expanded(
                      child: _buildIndicatorsList(textColor),
                    ),
                  ],
                ),
              ),
              
              // 하단: 추천 메시지
              _buildRecommendation(scoreColor, textColor),
            ],
          ),
          ),
        ),
      ),
    );
  }

  Widget _buildLoadingState() {
    return Container(
      width: double.infinity,
      height: 200,
      margin: const EdgeInsets.symmetric(horizontal: 20),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(24),
      ),
      child: const Center(
        child: CircularProgressIndicator(),
      ),
    );
  }

  Widget _buildHeader(Color scoreColor, Color textColor) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            scoreColor.withOpacity(0.1),
            scoreColor.withOpacity(0.05),
          ],
        ),
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(24),
          topRight: Radius.circular(24),
        ),
      ),
      child: Row(
        children: [
          // 아이콘 배지
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: scoreColor.withOpacity(0.15),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              Icons.trending_up_rounded,
              color: scoreColor,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          
          // 타이틀
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "오늘의 구매 타이밍",
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: textColor,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  "경제지표 기반 AI 분석",
                  style: TextStyle(
                    fontSize: 12,
                    color: textColor.withOpacity(0.6),
                  ),
                ),
              ],
            ),
          ),
          
          // 상태 배지
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: scoreColor,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              timing.label,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCircularGauge(Color scoreColor, Color textColor) {
    return CircularPercentIndicator(
      radius: 60,
      lineWidth: 10,
      percent: timing.score / 100,
      center: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            timing.score.toInt().toString(),
            style: TextStyle(
              fontSize: 32,
              fontWeight: FontWeight.w800,
              color: scoreColor,
              height: 1,
            ),
          ),
          Text(
            "/ 100",
            style: TextStyle(
              fontSize: 12,
              color: textColor.withOpacity(0.5),
            ),
          ),
        ],
      ),
      progressColor: scoreColor,
      backgroundColor: scoreColor.withOpacity(0.15),
      circularStrokeCap: CircularStrokeCap.round,
      animation: true,
      animationDuration: 1500,
    );
  }

  Widget _buildIndicatorsList(Color textColor) {
    // 기본 경제지표 (API에서 오지 않으면 기본값)
    final indicators = timing.indicators.isNotEmpty 
        ? timing.indicators.take(3).toList()
        : [
            {'name': '금리', 'status': 'positive', 'desc': '안정적'},
            {'name': '유가', 'status': 'positive', 'desc': '하락세'},
            {'name': '신차출시', 'status': 'neutral', 'desc': '-'},
          ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          "📊 경제지표 현황",
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: textColor.withOpacity(0.7),
          ),
        ),
        const SizedBox(height: 12),
        ...indicators.map((indicator) => _buildIndicatorRow(
          indicator['name'] as String,
          indicator['status'] as String,
          indicator['desc'] as String? ?? '',
          textColor,
        )),
      ],
    );
  }

  Widget _buildIndicatorRow(String name, String status, String desc, Color textColor) {
    final isPositive = status == 'positive';
    final isNegative = status == 'negative';
    
    final icon = isPositive 
        ? Icons.arrow_drop_up_rounded
        : isNegative 
            ? Icons.arrow_drop_down_rounded 
            : Icons.remove_rounded;
    
    final color = isPositive 
        ? const Color(0xFF10B981) // 초록
        : isNegative 
            ? const Color(0xFFEF4444) // 빨강
            : const Color(0xFF6B7280); // 회색

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Text(
            name,
            style: TextStyle(
              fontSize: 13,
              color: textColor.withOpacity(0.8),
            ),
          ),
          const Spacer(),
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 2),
          Text(
            isPositive ? "좋음" : isNegative ? "주의" : "보통",
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendation(Color scoreColor, Color textColor) {
    final message = timing.score >= 70 
        ? "💡 지금이 구매하기 좋은 시기입니다!"
        : timing.score >= 50 
            ? "⏳ 조금 더 지켜보는 것을 추천합니다"
            : "⚠️ 구매 시기를 재고려해 보세요";

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: scoreColor.withOpacity(0.05),
        borderRadius: const BorderRadius.only(
          bottomLeft: Radius.circular(24),
          bottomRight: Radius.circular(24),
        ),
        border: Border(
          top: BorderSide(
            color: scoreColor.withOpacity(0.1),
            width: 1,
          ),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: Text(
              message,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: scoreColor,
              ),
            ),
          ),
          Icon(
            Icons.arrow_forward_ios_rounded,
            size: 14,
            color: scoreColor.withOpacity(0.5),
          ),
        ],
      ),
    );
  }
}
