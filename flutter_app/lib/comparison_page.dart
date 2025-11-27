import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'models/car_data.dart';
import 'providers/comparison_provider.dart';

class ComparisonPage extends StatelessWidget {
  const ComparisonPage({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final backgroundColor = Theme.of(context).scaffoldBackgroundColor;
    final cardColor = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final textColor = isDark ? Colors.white : Colors.black;
    final borderColor = isDark ? Colors.grey[800]! : Colors.grey[200]!;

    return Consumer<ComparisonProvider>(
      builder: (context, provider, child) {
        final comparingCars = provider.comparingCars;

        return Scaffold(
          backgroundColor: backgroundColor,
          appBar: AppBar(
            title: Text(
              "차량 비교",
              style: TextStyle(color: textColor, fontWeight: FontWeight.bold),
            ),
            backgroundColor: backgroundColor,
            elevation: 0,
            leading: IconButton(
              icon: Icon(Icons.arrow_back_ios, color: textColor),
              onPressed: () => Navigator.pop(context),
            ),
            actions: [
              IconButton(
                icon: Icon(Icons.delete_outline, color: textColor),
                onPressed: () {
                  provider.clear();
                  Navigator.pop(context);
                },
              ),
            ],
          ),
          body: comparingCars.isEmpty
              ? Center(
                  child: Text(
                    "비교할 차량이 없습니다.",
                    style: TextStyle(color: Colors.grey[500]),
                  ),
                )
              : Column(
                  children: [
                    // 1. Sticky Header (차량 기본 정보 고정)
                    Container(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      decoration: BoxDecoration(
                        color: cardColor,
                        border: Border(bottom: BorderSide(color: borderColor)),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.05),
                            blurRadius: 5,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Row(
                        children: [
                          const SizedBox(
                              width: 100,
                              child: Center(child: Text("구분"))), // 라벨 영역
                          Expanded(
                            child: Row(
                              children: comparingCars.map((car) {
                                return Expanded(
                                  child: Column(
                                    children: [
                                      Stack(
                                        alignment: Alignment.topRight,
                                        children: [
                                          Container(
                                            width: 60,
                                            height: 60,
                                            decoration: BoxDecoration(
                                              color: car.color,
                                              shape: BoxShape.circle,
                                            ),
                                            child: const Icon(
                                                Icons.directions_car,
                                                color: Colors.white),
                                          ),
                                          GestureDetector(
                                            onTap: () =>
                                                provider.removeCar(car),
                                            child: Container(
                                              padding: const EdgeInsets.all(2),
                                              decoration: const BoxDecoration(
                                                color: Colors.grey,
                                                shape: BoxShape.circle,
                                              ),
                                              child: const Icon(Icons.close,
                                                  size: 12,
                                                  color: Colors.white),
                                            ),
                                          ),
                                        ],
                                      ),
                                      const SizedBox(height: 8),
                                      Text(
                                        car.name,
                                        style: TextStyle(
                                            fontWeight: FontWeight.bold,
                                            fontSize: 12,
                                            color: textColor),
                                        textAlign: TextAlign.center,
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                      Text(
                                        car.price,
                                        style: const TextStyle(
                                            color: Color(0xFF0066FF),
                                            fontWeight: FontWeight.bold,
                                            fontSize: 12),
                                      ),
                                    ],
                                  ),
                                );
                              }).toList(),
                            ),
                          ),
                        ],
                      ),
                    ),

                    // 2. Scrollable Body (상세 비교 항목)
                    Expanded(
                      child: SingleChildScrollView(
                        child: Column(
                          children: [
                            _buildSectionTitle("기본 정보", textColor),
                            _buildComparisonRow(
                                "연식",
                                (car) => car.info.split('·')[1].trim(),
                                isDark,
                                textColor,
                                comparingCars),
                            _buildComparisonRow(
                                "주행거리",
                                (car) => car.info.split('·')[0].trim(),
                                isDark,
                                textColor,
                                comparingCars),
                            _buildComparisonRow("연료", (car) => "가솔린", isDark,
                                textColor, comparingCars), // Dummy
                            _buildComparisonRow("지역", (car) => "서울", isDark,
                                textColor, comparingCars), // Dummy
                            _buildComparisonRow("사고유무", (car) => "무사고", isDark,
                                textColor, comparingCars), // Dummy

                            const SizedBox(height: 24),
                            _buildSectionTitle("가격 분석", textColor),
                            _buildPriceGraph(isDark, textColor,
                                comparingCars), // Placeholder for graph

                            const SizedBox(height: 24),
                            _buildSectionTitle("감가율 예측", textColor),
                            _buildDepreciationChart(isDark, textColor,
                                comparingCars), // Placeholder for chart

                            const SizedBox(height: 24),
                            _buildSectionTitle("주요 옵션", textColor),
                            _buildOptionComparison(
                                isDark, textColor, comparingCars),

                            const SizedBox(height: 40),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
        );
      },
    );
  }

  Widget _buildSectionTitle(String title, Color textColor) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 24, 16, 8),
      child: Align(
        alignment: Alignment.centerLeft,
        child: Text(
          title,
          style: TextStyle(
              fontSize: 18, fontWeight: FontWeight.bold, color: textColor),
        ),
      ),
    );
  }

  Widget _buildComparisonRow(String label, String Function(CarData) getValue,
      bool isDark, Color textColor, List<CarData> cars) {
    final borderColor = isDark ? Colors.grey[800]! : Colors.grey[200]!;

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12),
      decoration: BoxDecoration(
        border: Border(bottom: BorderSide(color: borderColor)),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 100,
            child: Center(
              child: Text(label,
                  style: TextStyle(color: Colors.grey[600], fontSize: 14)),
            ),
          ),
          Expanded(
            child: Row(
              children: cars.map((car) {
                return Expanded(
                  child: Center(
                    child: Text(
                      getValue(car),
                      style: TextStyle(
                          color: textColor,
                          fontWeight: FontWeight.w500,
                          fontSize: 14),
                      textAlign: TextAlign.center,
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPriceGraph(bool isDark, Color textColor, List<CarData> cars) {
    if (cars.isEmpty) return const SizedBox();

    // 가격 문자열에서 숫자만 추출 (예: "3,500만원" -> 3500)
    double parsePrice(String price) {
      return double.tryParse(price.replaceAll(RegExp(r'[^0-9]'), '')) ?? 0;
    }

    final prices = cars.map((c) => parsePrice(c.price)).toList();
    final maxPrice = prices.reduce((a, b) => a > b ? a : b);

    return Container(
      height: 200,
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF2C2C2C) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border:
            Border.all(color: isDark ? Colors.grey[800]! : Colors.grey[200]!),
      ),
      child: Column(
        children: [
          Expanded(
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
                      "${(price / 10000).toStringAsFixed(1)}억",
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: textColor,
                      ),
                    ),
                    const SizedBox(height: 8),
                    TweenAnimationBuilder<double>(
                      tween: Tween(begin: 0, end: heightFactor),
                      duration: const Duration(milliseconds: 1000),
                      curve: Curves.easeOut,
                      builder: (context, value, child) {
                        return Container(
                          width: 40,
                          height: 100 * value,
                          decoration: BoxDecoration(
                            color: car.color.withOpacity(0.8),
                            borderRadius: const BorderRadius.vertical(
                                top: Radius.circular(8)),
                          ),
                        );
                      },
                    ),
                    const SizedBox(height: 8),
                    Text(
                      car.name,
                      style: TextStyle(fontSize: 10, color: textColor),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                );
              }),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDepreciationChart(
      bool isDark, Color textColor, List<CarData> cars) {
    return Container(
      height: 200,
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF2C2C2C) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border:
            Border.all(color: isDark ? Colors.grey[800]! : Colors.grey[200]!),
      ),
      child: Column(
        children: [
          Expanded(
            child: CustomPaint(
              size: const Size(double.infinity, 150),
              painter: DepreciationPainter(
                cars: cars,
                isDark: isDark,
              ),
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: cars.map((car) {
              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 8),
                child: Row(
                  children: [
                    Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: car.color,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 4),
                    Text(
                      car.name,
                      style: TextStyle(fontSize: 10, color: textColor),
                    ),
                  ],
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildOptionComparison(
      bool isDark, Color textColor, List<CarData> cars) {
    // Dummy options
    final options = ["선루프", "헤드업 디스플레이", "통풍시트", "어라운드뷰"];

    return Column(
      children: options.map((option) {
        return _buildComparisonRow(option, (car) {
          // Randomly assign O/X for demo
          return car.id.hashCode % 2 == 0 ? "O" : "X";
        }, isDark, textColor, cars);
      }).toList(),
    );
  }
}

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

    // Draw Axis
    canvas.drawLine(
        Offset(0, size.height), Offset(size.width, size.height), axisPaint);
    canvas.drawLine(const Offset(0, 0), Offset(0, size.height), axisPaint);

    // Draw Lines for each car
    for (int i = 0; i < cars.length; i++) {
      final car = cars[i];
      paint.color = car.color;

      final path = Path();
      // Dummy depreciation logic: price drops by 10% each year
      // Start (Year 0) -> End (Year 3)
      path.moveTo(0, size.height * 0.1); // Start high (high price)

      // Randomize slightly for demo
      double dropRate = 0.1 + (car.id.hashCode % 5) * 0.02;

      path.quadraticBezierTo(
        size.width * 0.5,
        size.height * (0.1 + dropRate * 1.5),
        size.width,
        size.height * (0.1 + dropRate * 3),
      );

      canvas.drawPath(path, paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
