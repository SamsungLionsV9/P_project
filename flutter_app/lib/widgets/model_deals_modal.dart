import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'deal_analysis_modal.dart';
import 'common/option_badges.dart';

/// 모델별 가성비 매물 모달 (공유 위젯)
/// 홈페이지 인기 모델 클릭, 추천 페이지 인기 모델 클릭 시 사용
class ModelDealsModal extends StatefulWidget {
  final String brand;
  final String model;
  final int avgPrice;
  final int medianPrice;
  final int listings;
  final void Function(RecommendedCar car)? onCarViewed;

  const ModelDealsModal({
    super.key,
    required this.brand,
    required this.model,
    required this.avgPrice,
    required this.medianPrice,
    required this.listings,
    this.onCarViewed,
  });

  @override
  State<ModelDealsModal> createState() => _ModelDealsModalState();
}

class _ModelDealsModalState extends State<ModelDealsModal> {
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
        predictedPrice: car.predictedPrice,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor = isDark ? const Color(0xFF1A1A2E) : Colors.white;
    final cardColor = isDark ? const Color(0xFF252542) : Colors.grey[50];
    final textColor = isDark ? Colors.white : Colors.black87;
    final subtextColor = isDark ? Colors.grey[400] : Colors.grey[600];
    
    return DraggableScrollableSheet(
      initialChildSize: 0.7,
      minChildSize: 0.5,
      maxChildSize: 0.95,
      builder: (context, scrollController) {
        return Container(
          decoration: BoxDecoration(
            color: bgColor,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
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
                            style: TextStyle(
                              color: textColor,
                              fontSize: 22,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        IconButton(
                          icon: Icon(Icons.close, color: textColor),
                          onPressed: () => Navigator.pop(context),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '등록 ${widget.listings}건 • 평균 ${widget.avgPrice}만원 • 중앙값 ${widget.medianPrice}만원',
                      style: TextStyle(color: subtextColor, fontSize: 13),
                    ),
                    const SizedBox(height: 16),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
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
                            style: TextStyle(color: Colors.green, fontSize: 13, fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              Divider(color: isDark ? Colors.white12 : Colors.grey[300], height: 24),
              // 매물 리스트
              Expanded(
                child: _isLoading
                    ? const Center(child: CircularProgressIndicator())
                    : _error != null
                        ? Center(child: Text(_error!, style: const TextStyle(color: Colors.red)))
                        : _deals.isEmpty
                            ? Center(child: Text('추천 매물이 없습니다', style: TextStyle(color: subtextColor)))
                            : ListView.builder(
                                controller: scrollController,
                                padding: const EdgeInsets.symmetric(horizontal: 16),
                                itemCount: _deals.length,
                                itemBuilder: (context, index) {
                                  final deal = _deals[index];
                                  return _buildDealCard(deal, index + 1, isDark, cardColor!, textColor, subtextColor!);
                                },
                              ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildDealCard(RecommendedCar deal, int rank, bool isDark, Color cardColor, Color textColor, Color subtextColor) {
    final priceDiff = deal.priceDiff;
    final isGood = priceDiff > 0;
    
    return GestureDetector(
      onTap: () => _showDealAnalysis(deal),
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: cardColor,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isGood ? Colors.green.withOpacity(0.4) : (isDark ? Colors.white10 : Colors.grey[300]!),
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
                    color: rank <= 3 ? const Color(0xFF0066FF) : Colors.grey[600],
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
                        style: TextStyle(
                          color: textColor,
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '${deal.year}년 • ${deal.formattedMileage} • ${deal.fuel}',
                        style: TextStyle(color: subtextColor, fontSize: 12),
                      ),
                      // 옵션 배지 표시
                      if (deal.options != null) ...[
                        const SizedBox(height: 6),
                        OptionBadges(options: deal.options!, compact: true),
                      ],
                    ],
                  ),
                ),
                if (isGood)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.green.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: const Text(
                      '추천',
                      style: TextStyle(color: Colors.green, fontSize: 11, fontWeight: FontWeight.bold),
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
                      Text('실제가', style: TextStyle(color: subtextColor, fontSize: 11)),
                      Text(
                        '${deal.actualPrice}만원',
                        style: TextStyle(color: textColor, fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('예측가', style: TextStyle(color: subtextColor, fontSize: 11)),
                      Text(
                        '${deal.predictedPrice}만원',
                        style: TextStyle(color: subtextColor, fontSize: 16),
                      ),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text('차이', style: TextStyle(color: subtextColor, fontSize: 11)),
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
