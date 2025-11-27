import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'models/car_data.dart';
import 'providers/comparison_provider.dart';
import 'theme/theme_provider.dart';

/// 차량 비교 페이지
class ComparisonPage extends StatelessWidget {
  const ComparisonPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer2<ThemeProvider, ComparisonProvider>(
      builder: (context, themeProvider, comparisonProvider, child) {
        final isDark = themeProvider.isDarkMode;
        final bgColor = isDark ? const Color(0xFF1A1A1A) : const Color(0xFFF5F7FA);
        final cardColor = isDark ? const Color(0xFF2C2C2C) : Colors.white;
        final textColor = isDark ? Colors.white : Colors.black87;
        final subTextColor = isDark ? Colors.grey[400]! : Colors.grey[600]!;
        final cars = comparisonProvider.comparingCars;

        return Scaffold(
          backgroundColor: bgColor,
          appBar: AppBar(
            backgroundColor: cardColor,
            elevation: 0,
            leading: IconButton(
              icon: Icon(Icons.arrow_back, color: textColor),
              onPressed: () => Navigator.pop(context),
            ),
            title: Text(
              '차량 비교 (${cars.length}/3)',
              style: TextStyle(color: textColor, fontWeight: FontWeight.bold),
            ),
            actions: [
              if (cars.isNotEmpty)
                TextButton(
                  onPressed: () {
                    comparisonProvider.clear();
                  },
                  child: const Text('초기화', style: TextStyle(color: Color(0xFF0066FF))),
                ),
            ],
          ),
          body: cars.isEmpty
              ? _buildEmptyState(textColor, subTextColor)
              : SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // 차량 헤더
                      _buildCarHeaders(cars, isDark, cardColor, textColor),
                      
                      // 기본 정보 비교
                      _buildSectionTitle('기본 정보', textColor),
                      _buildComparisonRow('차량명', (car) => car.name, isDark, textColor, cars),
                      _buildComparisonRow('가격', (car) => car.price, isDark, textColor, cars),
                      _buildComparisonRow('정보', (car) => car.info, isDark, textColor, cars),
                      
                      // 가격 그래프
                      _buildSectionTitle('가격 비교', textColor),
                      _buildPriceGraph(isDark, textColor, cars),
                      
                      // 가격 분석
                      if (cars.length >= 2) ...[
                        _buildSectionTitle('가격 분석', textColor),
                        _buildPriceAnalysis(comparisonProvider, isDark, cardColor, textColor, subTextColor),
                      ],
                      
                      // 감가율 차트
                      _buildSectionTitle('예상 감가율', textColor),
                      _buildDepreciationChart(isDark, textColor, cars),
                      
                      const SizedBox(height: 100),
                    ],
                  ),
                ),
        );
      },
    );
  }

  Widget _buildEmptyState(Color textColor, Color subTextColor) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.compare_arrows, size: 80, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            '비교할 차량을 추가해주세요',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: textColor),
          ),
          const SizedBox(height: 8),
          Text(
            '찜한 차량이나 분석 결과에서\n최대 3대까지 비교할 수 있습니다',
            textAlign: TextAlign.center,
            style: TextStyle(color: subTextColor),
          ),
        ],
      ),
    );
  }

  Widget _buildCarHeaders(List<CarData> cars, bool isDark, Color cardColor, Color textColor) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: cardColor,
        border: Border(bottom: BorderSide(color: isDark ? Colors.grey[800]! : Colors.grey[200]!)),
      ),
      child: Row(
        children: [
          const SizedBox(width: 80), // 라벨 공간
          ...cars.map((car) => Expanded(
            child: Column(
              children: [
                Container(
                  width: 60,
                  height: 60,
                  decoration: BoxDecoration(
                    color: car.color,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.directions_car, color: Colors.white, size: 30),
                ),
                const SizedBox(height: 8),
                Text(
                  car.name,
                  style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: textColor),
                  textAlign: TextAlign.center,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          )),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title, Color textColor) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 24, 16, 8),
      child: Text(
        title,
        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: textColor),
      ),
    );
  }

  Widget _buildComparisonRow(String label, String Function(CarData) getValue,
      bool isDark, Color textColor, List<CarData> cars) {
    final borderColor = isDark ? Colors.grey[800]! : Colors.grey[200]!;

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
      decoration: BoxDecoration(
        border: Border(bottom: BorderSide(color: borderColor)),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 80,
            child: Text(label, style: TextStyle(color: Colors.grey[600], fontSize: 14)),
          ),
          ...cars.map((car) => Expanded(
            child: Center(
              child: Text(
                getValue(car),
                style: TextStyle(color: textColor, fontWeight: FontWeight.w500, fontSize: 14),
                textAlign: TextAlign.center,
              ),
            ),
          )),
        ],
      ),
    );
  }

  Widget _buildPriceGraph(bool isDark, Color textColor, List<CarData> cars) {
    if (cars.isEmpty) return const SizedBox();

    final prices = cars.map((c) => c.priceValue).toList();
    final maxPrice = prices.reduce((a, b) => a > b ? a : b);

    return Container(
      height: 200,
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF2C2C2C) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: isDark ? Colors.grey[800]! : Colors.grey[200]!),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: List.generate(cars.length, (index) {
          final car = cars[index];
          final price = prices[index];
          final heightFactor = maxPrice > 0 ? price / maxPrice : 0.0;

          return Column(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              Text(
                '${(price / 10000).toStringAsFixed(1)}억',
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: textColor),
              ),
              const SizedBox(height: 8),
              TweenAnimationBuilder<double>(
                tween: Tween(begin: 0, end: heightFactor),
                duration: const Duration(milliseconds: 800),
                curve: Curves.easeOut,
                builder: (context, value, child) {
                  return Container(
                    width: 50,
                    height: 100 * value,
                    decoration: BoxDecoration(
                      color: car.color.withOpacity(0.8),
                      borderRadius: const BorderRadius.vertical(top: Radius.circular(8)),
                    ),
                  );
                },
              ),
              const SizedBox(height: 8),
              SizedBox(
                width: 60,
                child: Text(
                  car.name.split(' ').first,
                  style: TextStyle(fontSize: 10, color: textColor),
                  textAlign: TextAlign.center,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          );
        }),
      ),
    );
  }

  Widget _buildPriceAnalysis(ComparisonProvider provider, bool isDark, 
      Color cardColor, Color textColor, Color subTextColor) {
    final analysis = provider.getPriceComparison();
    final cheapest = analysis['cheapest'] as CarData;
    final priceDiff = analysis['priceDifference'] as double;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: isDark ? Colors.grey[800]! : Colors.grey[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.emoji_events, color: Color(0xFFFFD700), size: 24),
              const SizedBox(width: 8),
              Text(
                '가장 저렴: ${cheapest.name}',
                style: TextStyle(fontWeight: FontWeight.bold, color: textColor),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            '최저가 대비 최고가 차이: ${priceDiff.toStringAsFixed(0)}만원',
            style: TextStyle(color: subTextColor),
          ),
          const SizedBox(height: 8),
          ...(analysis['cars'] as List).map((item) {
            final car = item['car'] as CarData;
            final diff = item['diffFromCheapest'] as double;
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                children: [
                  Container(width: 12, height: 12, decoration: BoxDecoration(color: car.color, shape: BoxShape.circle)),
                  const SizedBox(width: 8),
                  Expanded(child: Text(car.name, style: TextStyle(color: textColor, fontSize: 13))),
                  Text(
                    diff > 0 ? '+${diff.toStringAsFixed(0)}만' : '최저가',
                    style: TextStyle(
                      color: diff > 0 ? Colors.red : const Color(0xFF00C853),
                      fontWeight: FontWeight.bold,
                      fontSize: 13,
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildDepreciationChart(bool isDark, Color textColor, List<CarData> cars) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF2C2C2C) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: isDark ? Colors.grey[800]! : Colors.grey[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 차트 설명
          Row(
            children: [
              Icon(Icons.info_outline, size: 14, color: Colors.grey[500]),
              const SizedBox(width: 4),
              Text(
                '선이 낮을수록 가치 유지율이 높습니다',
                style: TextStyle(fontSize: 11, color: Colors.grey[500]),
              ),
            ],
          ),
          const SizedBox(height: 8),
          // Y축 설명
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Column(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('100%', style: TextStyle(fontSize: 9, color: Colors.grey[500])),
                  const SizedBox(height: 55),
                  Text('70%', style: TextStyle(fontSize: 9, color: Colors.grey[500])),
                  const SizedBox(height: 55),
                  Text('40%', style: TextStyle(fontSize: 9, color: Colors.grey[500])),
                ],
              ),
              const SizedBox(width: 8),
              Expanded(
                child: SizedBox(
                  height: 150,
                  child: CustomPaint(
                    size: const Size(double.infinity, 150),
                    painter: DepreciationPainter(cars: cars, isDark: isDark),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          // 범례
          Wrap(
            spacing: 16,
            runSpacing: 8,
            children: cars.map((car) {
              return Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(width: 12, height: 12, decoration: BoxDecoration(color: car.color, shape: BoxShape.circle)),
                  const SizedBox(width: 4),
                  Text(car.name.split(' ').first, style: TextStyle(fontSize: 11, color: textColor)),
                ],
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}

/// 감가율 차트 페인터
class DepreciationPainter extends CustomPainter {
  final List<CarData> cars;
  final bool isDark;

  DepreciationPainter({required this.cars, required this.isDark});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.0;

    final axisPaint = Paint()
      ..color = isDark ? Colors.grey[700]! : Colors.grey[300]!
      ..strokeWidth = 1.0;

    // 축 그리기
    canvas.drawLine(Offset(0, size.height), Offset(size.width, size.height), axisPaint);
    canvas.drawLine(const Offset(0, 0), Offset(0, size.height), axisPaint);

    // 각 차량별 감가 곡선
    for (int i = 0; i < cars.length; i++) {
      final car = cars[i];
      paint.color = car.color;

      final path = Path();
      path.moveTo(0, size.height * 0.1);

      // 차량별 감가율 시뮬레이션 (연식 기반)
      double dropRate = 0.1 + (car.id.hashCode % 5) * 0.02;

      path.quadraticBezierTo(
        size.width * 0.5,
        size.height * (0.1 + dropRate * 1.5),
        size.width,
        size.height * (0.1 + dropRate * 3),
      );

      canvas.drawPath(path, paint);
    }

    // X축 라벨
    final textPainter = TextPainter(textDirection: TextDirection.ltr);
    final labels = ['현재', '1년후', '2년후', '3년후'];
    for (int i = 0; i < labels.length; i++) {
      textPainter.text = TextSpan(
        text: labels[i],
        style: TextStyle(color: isDark ? Colors.grey[500] : Colors.grey[600], fontSize: 10),
      );
      textPainter.layout();
      textPainter.paint(canvas, Offset(i * size.width / 3 - (i == 0 ? 0 : 15), size.height + 5));
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
