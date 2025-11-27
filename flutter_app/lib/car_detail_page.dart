import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'models/car_data.dart';
import 'negotiation_page.dart';
import 'providers/comparison_provider.dart';

class CarDetailPage extends StatelessWidget {
  final CarData car;

  const CarDetailPage({super.key, required this.car});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final backgroundColor = Theme.of(context).scaffoldBackgroundColor;
    final cardColor = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final textColor = isDark ? Colors.white : Colors.black;
    final subTextColor = isDark ? Colors.grey[400]! : Colors.grey[600]!;
    final borderColor = isDark ? Colors.grey[800]! : Colors.grey[200]!;

    return Scaffold(
      backgroundColor: backgroundColor,
      body: SafeArea(
        child: Column(
          children: [
            // 상단 앱바 및 이미지 영역
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 1. 이미지 영역 (Custom AppBar)
                    // 1. 이미지 영역 (Custom AppBar)
                    Stack(
                      children: [
                        Container(
                          width: double.infinity,
                          height: 300,
                          color: car.color,
                          child: Icon(
                            Icons.directions_car,
                            size: 100,
                            color: Colors.white.withOpacity(0.5),
                          ),
                        ),
                        // 뒤로가기 버튼
                        Positioned(
                          top: 16,
                          left: 16,
                          child: CircleAvatar(
                            backgroundColor: Colors.black.withOpacity(0.3),
                            child: IconButton(
                              icon: const Icon(Icons.arrow_back_ios_new,
                                  color: Colors.white, size: 20),
                              onPressed: () => Navigator.pop(context),
                            ),
                          ),
                        ),
                        // 액션 버튼들 (비교, 공유, 좋아요)
                        Positioned(
                          top: 16,
                          right: 16,
                          child: Row(
                            children: [
                              CircleAvatar(
                                backgroundColor: Colors.black.withOpacity(0.3),
                                child: IconButton(
                                  icon: const Icon(Icons.compare_arrows,
                                      color: Colors.white, size: 20),
                                  onPressed: () {
                                    final provider =
                                        context.read<ComparisonProvider>();
                                    if (provider.isComparing(car)) {
                                      ScaffoldMessenger.of(context)
                                          .showSnackBar(
                                        const SnackBar(
                                            content: Text("이미 비교함에 있는 차량입니다.")),
                                      );
                                    } else {
                                      if (provider.comparingCars.length >= 3) {
                                        ScaffoldMessenger.of(context)
                                            .showSnackBar(
                                          const SnackBar(
                                              content:
                                                  Text("최대 3대까지만 비교할 수 있습니다.")),
                                        );
                                      } else {
                                        provider.addCar(car);
                                        ScaffoldMessenger.of(context)
                                            .showSnackBar(
                                          const SnackBar(
                                              content: Text("비교함에 추가되었습니다.")),
                                        );
                                      }
                                    }
                                  },
                                ),
                              ),
                              const SizedBox(width: 8),
                              CircleAvatar(
                                backgroundColor: Colors.black.withOpacity(0.3),
                                child: IconButton(
                                  icon: const Icon(Icons.share,
                                      color: Colors.white, size: 20),
                                  onPressed: () {},
                                ),
                              ),
                              const SizedBox(width: 8),
                              const _LikeButton(),
                            ],
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 24),

                    // 주요 스펙 (가로 스크롤 또는 Grid)
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 20),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          _buildSpecItem(Icons.local_gas_station, "가솔린", "연료",
                              isDark, textColor, subTextColor),
                          _buildSpecItem(Icons.settings, "오토", "변속기", isDark,
                              textColor, subTextColor),
                          _buildSpecItem(Icons.palette, "블랙", "색상", isDark,
                              textColor, subTextColor),
                          _buildSpecItem(Icons.verified_user, "무사고", "사고유무",
                              isDark, textColor, subTextColor),
                        ],
                      ),
                    ),

                    const SizedBox(height: 32),
                    Divider(color: borderColor),
                    const SizedBox(height: 24),

                    // 판매자 정보
                    Text(
                      "판매자 정보",
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: textColor,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        const CircleAvatar(
                          radius: 24,
                          backgroundColor: Color(0xFF0066FF),
                          child: Icon(Icons.person, color: Colors.white),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                "김딜러",
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16,
                                  color: textColor,
                                ),
                              ),
                              Text(
                                "수원 오토컬렉션",
                                style: TextStyle(
                                  fontSize: 12,
                                  color: subTextColor,
                                ),
                              ),
                            ],
                          ),
                        ),
                        _buildContactButton(Icons.call, "전화", isDark),
                        const SizedBox(width: 8),
                        _buildContactButton(Icons.message, "문자", isDark),
                      ],
                    ),

                    const SizedBox(height: 32),

                    // 차량 설명
                    Text(
                      "차량 설명",
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: textColor,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      "1인 신조 완전 무사고 차량입니다. 비흡연 차량이며 주기적으로 관리하여 상태 최상입니다. 스마트키 2개 보유 중이며 타이어 교체한지 1달 되었습니다.",
                      style: TextStyle(
                        fontSize: 14,
                        height: 1.6,
                        color: subTextColor,
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // 하단 고정 버튼
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: cardColor,
                border: Border(top: BorderSide(color: borderColor)),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 10,
                    offset: const Offset(0, -4),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const NegotiationPage(),
                          ),
                        );
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF0066FF),
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                        ),
                        elevation: 0,
                      ),
                      child: const Text(
                        "이 차로 네고해보기",
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSpecItem(IconData icon, String value, String label, bool isDark,
      Color textColor, Color subTextColor) {
    return Container(
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF2C2C2C) : const Color(0xFFF5F7FA),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 20, color: const Color(0xFF0066FF)),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 12,
              color: textColor,
            ),
          ),
          Text(
            label,
            style: TextStyle(
              fontSize: 10,
              color: subTextColor,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildContactButton(IconData icon, String label, bool isDark) {
    return Container(
      decoration: BoxDecoration(
        border:
            Border.all(color: isDark ? Colors.grey[700]! : Colors.grey[300]!),
        borderRadius: BorderRadius.circular(8),
      ),
      child: IconButton(
        icon:
            Icon(icon, size: 20, color: isDark ? Colors.white : Colors.black87),
        onPressed: () {},
        tooltip: label,
      ),
    );
  }
}

class _LikeButton extends StatefulWidget {
  const _LikeButton();

  @override
  State<_LikeButton> createState() => _LikeButtonState();
}

class _LikeButtonState extends State<_LikeButton> {
  bool isLiked = false;

  @override
  Widget build(BuildContext context) {
    return CircleAvatar(
      backgroundColor: Colors.black.withOpacity(0.3),
      child: IconButton(
        icon: Icon(
          isLiked ? Icons.favorite : Icons.favorite_border,
          color: isLiked ? Colors.red : Colors.white,
          size: 20,
        ),
        onPressed: () {
          setState(() {
            isLiked = !isLiked;
          });
        },
      ),
    );
  }
}
