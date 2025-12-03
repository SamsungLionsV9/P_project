import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class HeroSection extends StatelessWidget {
  final VoidCallback onStartPressed;

  const HeroSection({Key? key, required this.onStartPressed}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(24, 60, 24, 40),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            AppTheme.primaryBlue.withOpacity(0.05),
            Colors.white,
          ],
        ),
      ),
      child: Column(
        children: [
          const Icon(
            Icons.access_time_filled,
            size: 64,
            color: AppTheme.primaryBlue,
          ),
          const SizedBox(height: 24),
          const Text(
            "지금 사면\n손해일까?",
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 32,
              fontWeight: FontWeight.bold,
              color: AppTheme.darkText,
              height: 1.3,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            "경제지표 기반 구매 타이밍 분석\n금리·유가·환율을 분석해 최적의 구매 시점을 알려드립니다.",
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey[600],
              height: 1.5,
            ),
          ),
          const SizedBox(height: 32),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: onStartPressed,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryBlue,
                padding: const EdgeInsets.symmetric(vertical: 20),
              ),
              child: const Text(
                "지금이 살 때인지 확인하기",
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _buildBadge("경제지표 연동"),
              const SizedBox(width: 12),
              _buildBadge("타이밍 분석"),
              const SizedBox(width: 12),
              _buildBadge("AI 시세"),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildBadge(String text) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.grey[300]!),
      ),
      child: Text(
        text,
        style: TextStyle(
          fontSize: 12,
          color: Colors.grey[700],
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
