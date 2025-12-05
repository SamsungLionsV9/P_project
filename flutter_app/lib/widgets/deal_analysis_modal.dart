import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../negotiation_page.dart';
import 'common/option_badges.dart';
import '../providers/favorites_provider.dart';

/// 개별 매물 분석 모달
/// 가격 적정성, 허위매물 위험도, 네고 포인트 등 상세 분석 제공
class DealAnalysisModal extends StatefulWidget {
  final RecommendedCar deal;
  final int predictedPrice;

  const DealAnalysisModal({
    super.key,
    required this.deal,
    required this.predictedPrice,
  });

  @override
  State<DealAnalysisModal> createState() => _DealAnalysisModalState();
}

class _DealAnalysisModalState extends State<DealAnalysisModal> {
  final ApiService _api = ApiService();
  DealAnalysis? _analysis;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadAnalysis();
  }

  Future<void> _loadAnalysis() async {
    try {
      final analysis = await _api.analyzeDeal(
        brand: widget.deal.brand,
        model: widget.deal.model,
        year: widget.deal.year,
        mileage: widget.deal.mileage,
        actualPrice: widget.deal.actualPrice,
        predictedPrice: widget.predictedPrice,
        fuel: widget.deal.fuel,
      );
      setState(() {
        _analysis = analysis;
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
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return DraggableScrollableSheet(
      initialChildSize: 0.85,
      minChildSize: 0.5,
      maxChildSize: 0.95,
      builder: (context, scrollController) {
        return Scaffold(
          backgroundColor: Colors.transparent,
          body: Container(
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF1E1E1E) : Colors.white,
              borderRadius:
                  const BorderRadius.vertical(top: Radius.circular(20)),
            ),
            child: Column(
              children: [
                // 핸들
                Container(
                  margin: const EdgeInsets.only(top: 12),
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey[400],
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                // 헤더
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        "📊 매물 상세 분석",
                        style: TextStyle(
                            fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      Row(
                        children: [
                          Consumer<FavoritesProvider>(
                            builder: (context, provider, child) {
                              final isFavorite =
                                  provider.isFavorite(widget.deal);
                              return IconButton(
                                onPressed: () async {
                                  final wasFavorite =
                                      provider.isFavorite(widget.deal);
                                  await provider.toggleFavorite(widget.deal);
                                  if (!context.mounted) return;

                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text(wasFavorite
                                          ? "'${widget.deal.brand} ${widget.deal.model}' 찜 목록에서 삭제되었습니다."
                                          : "'${widget.deal.brand} ${widget.deal.model}' 찜 목록에 추가되었습니다."),
                                      duration: const Duration(seconds: 2),
                                    ),
                                  );
                                },
                                icon: Icon(
                                  isFavorite
                                      ? Icons.favorite
                                      : Icons.favorite_border,
                                  color: isFavorite ? Colors.red : Colors.grey,
                                ),
                              );
                            },
                          ),
                          IconButton(
                            onPressed: () => Navigator.pop(context),
                            icon: const Icon(Icons.close),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const Divider(height: 1),
                // 내용
                Expanded(
                  child: _isLoading
                      ? const Center(child: CircularProgressIndicator())
                      : _error != null
                          ? Center(child: Text("분석 실패: $_error"))
                          : _buildContent(scrollController, isDark),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildContent(ScrollController scrollController, bool isDark) {
    if (_analysis == null) return const SizedBox();

    final analysis = _analysis!;
    final summary = analysis.summary;
    final textColor = isDark ? Colors.white : Colors.black;

    return ListView(
      controller: scrollController,
      padding: const EdgeInsets.all(16),
      children: [
        // 차량 정보 및 가격 비교
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: isDark ? const Color(0xFF2A2A2A) : Colors.grey[50],
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      "${widget.deal.brand} ${widget.deal.model} ${widget.deal.year}년",
                      style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: textColor),
                    ),
                  ),
                  // 옵션 배지 (compact)
                  if (widget.deal.options != null)
                    OptionBadges(options: widget.deal.options!, compact: true),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: Column(
                      children: [
                        const Text("실제가",
                            style: TextStyle(color: Colors.grey, fontSize: 12)),
                        const SizedBox(height: 4),
                        Text(
                          "${summary.actualPrice}만원",
                          style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: textColor),
                        ),
                      ],
                    ),
                  ),
                  Expanded(
                    child: Column(
                      children: [
                        const Text("예측가",
                            style: TextStyle(color: Colors.grey, fontSize: 12)),
                        const SizedBox(height: 4),
                        Text(
                          "${summary.predictedPrice}만원",
                          style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF0066FF)),
                        ),
                      ],
                    ),
                  ),
                  Expanded(
                    child: Column(
                      children: [
                        const Text("차이",
                            style: TextStyle(color: Colors.grey, fontSize: 12)),
                        const SizedBox(height: 4),
                        Text(
                          "${summary.priceDiff > 0 ? '-' : '+'}${summary.priceDiff.abs()}만원",
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: summary.priceDiff > 0
                                ? Colors.green
                                : Colors.red,
                          ),
                        ),
                        Text(
                          "(${summary.priceDiffPct.abs().toStringAsFixed(1)}%${summary.priceDiff > 0 ? '↓' : '↑'})",
                          style: TextStyle(
                            fontSize: 12,
                            color: summary.priceDiff > 0
                                ? Colors.green
                                : Colors.red,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: summary.isGoodDeal
                      ? Colors.green.withOpacity(0.1)
                      : Colors.orange.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      summary.isGoodDeal ? Icons.thumb_up : Icons.info_outline,
                      color: summary.isGoodDeal ? Colors.green : Colors.orange,
                      size: 18,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      summary.isGoodDeal ? "추천 매물" : "검토 필요",
                      style: TextStyle(
                        color:
                            summary.isGoodDeal ? Colors.green : Colors.orange,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // 가격 적정성
        _buildSection(
          title: "💰 가격 적정성",
          isDark: isDark,
          trailing: Text(
            analysis.priceFairness.label,
            style: TextStyle(
              color: _getFairnessColor(analysis.priceFairness.label),
              fontWeight: FontWeight.bold,
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                analysis.priceFairness.label,
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: _getFairnessColor(analysis.priceFairness.label),
                ),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Text("상위 ${analysis.priceFairness.percentile}%",
                      style: TextStyle(color: Colors.grey[600])),
                ],
              ),
              const SizedBox(height: 12),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: analysis.priceFairness.score / 100,
                  backgroundColor: isDark ? Colors.grey[800] : Colors.grey[200],
                  color: _getFairnessColor(analysis.priceFairness.label),
                  minHeight: 8,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                analysis.priceFairness.description,
                style: TextStyle(color: textColor, height: 1.5),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // 허위매물 위험도
        _buildSection(
          title: "⚠️ 허위매물 위험도",
          isDark: isDark,
          trailing: Row(
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: analysis.fraudRisk.level == 'low'
                      ? Colors.green
                      : analysis.fraudRisk.level == 'medium'
                          ? Colors.orange
                          : Colors.red,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 6),
              Text(
                analysis.fraudRisk.level == 'low'
                    ? '낮음'
                    : analysis.fraudRisk.level == 'medium'
                        ? '보통'
                        : '높음',
                style: TextStyle(
                  color: analysis.fraudRisk.level == 'low'
                      ? Colors.green
                      : analysis.fraudRisk.level == 'medium'
                          ? Colors.orange
                          : Colors.red,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                "${analysis.fraudRisk.score} / 100",
                style: TextStyle(color: Colors.grey[600], fontSize: 12),
              ),
              const SizedBox(height: 8),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: analysis.fraudRisk.score / 100,
                  backgroundColor: isDark ? Colors.grey[800] : Colors.grey[200],
                  color: analysis.fraudRisk.level == 'low'
                      ? Colors.green
                      : analysis.fraudRisk.level == 'medium'
                          ? Colors.orange
                          : Colors.red,
                  minHeight: 8,
                ),
              ),
              const SizedBox(height: 16),
              ...analysis.fraudRisk.factors.map((factor) => Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      children: [
                        Icon(
                          factor.status == 'pass'
                              ? Icons.check_circle
                              : Icons.warning,
                          size: 18,
                          color: factor.status == 'pass'
                              ? Colors.green
                              : Colors.orange,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(factor.msg,
                              style: TextStyle(color: textColor)),
                        ),
                      ],
                    ),
                  )),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // 네고 포인트
        _buildSection(
          title: "💡 네고 포인트",
          isDark: isDark,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: analysis.negoPoints
                .map((point) => Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text("• ", style: TextStyle(fontSize: 16)),
                          Expanded(
                            child: Text(point,
                                style:
                                    TextStyle(color: textColor, height: 1.4)),
                          ),
                        ],
                      ),
                    ))
                .toList(),
          ),
        ),
        const SizedBox(height: 16),

        // 차량 옵션 상세 (옵션 데이터가 있는 경우만)
        if (widget.deal.options != null)
          OptionDetailSection(options: widget.deal.options!, isDark: isDark),

        const SizedBox(height: 24),

        // 버튼
        Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => NegotiationPage(
                        initialTabIndex: 0,
                        carName:
                            "${widget.deal.brand} ${widget.deal.model} ${widget.deal.year}년",
                        price: "${widget.deal.actualPrice}만원",
                        // 정확한 가격 정보 전달
                        actualPrice: widget.deal.actualPrice,
                        predictedPrice: widget.predictedPrice,
                        year: widget.deal.year,
                        mileage: widget.deal.mileage,
                      ),
                    ),
                  );
                },
                icon: const Icon(Icons.copy, size: 18),
                label: const Text("네고 문자"),
                style: OutlinedButton.styleFrom(
                  foregroundColor: const Color(0xFF0066FF),
                  side: const BorderSide(color: Color(0xFF0066FF)),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: ElevatedButton.icon(
                onPressed: () => _openEncar(),
                icon: const Icon(Icons.open_in_browser, size: 18),
                label: const Text("엔카에서 보기"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0066FF),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 32),
      ],
    );
  }

  Widget _buildSection({
    required String title,
    required bool isDark,
    required Widget child,
    Widget? trailing,
  }) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF2A2A2A) : Colors.grey[50],
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style:
                    const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              if (trailing != null) trailing,
            ],
          ),
          const SizedBox(height: 16),
          child,
        ],
      ),
    );
  }

  Color _getFairnessColor(String label) {
    switch (label) {
      case '매우 저렴':
        return const Color(0xFF00C853);
      case '저렴':
        return const Color(0xFF66BB6A);
      case '적정':
        return const Color(0xFF0066FF);
      case '다소 비쌈':
        return const Color(0xFFFFA726);
      case '비쌈':
        return const Color(0xFFE53935);
      default:
        return Colors.grey;
    }
  }

  Future<void> _openEncar() async {
    final url = widget.deal.detailUrl ??
        'https://www.encar.com/dc/dc_carsearchlist.do?q=${Uri.encodeComponent('${widget.deal.brand} ${widget.deal.model}')}';

    try {
      final uri = Uri.parse(url);
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } catch (e) {
      // ignore
    }
  }
}
