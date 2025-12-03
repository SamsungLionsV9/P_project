import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../widgets/hero_section.dart';
import '../widgets/feature_card.dart';
import '../widgets/interactive_demo.dart';

class LandingScreen extends StatelessWidget {
  const LandingScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: const [
            Icon(Icons.access_time_filled, color: AppTheme.primaryBlue),
            SizedBox(width: 8),
            Text("언제 살까?"),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {},
            child: const Text("로그인"),
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // 1. Hero Section
            HeroSection(
              onStartPressed: () {
                // TODO: 분석 페이지로 이동
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text("분석 화면으로 이동합니다")),
                );
              },
            ),

            const SizedBox(height: 40),

            // 2. Interactive Demo
            const InteractiveDemo(),

            const SizedBox(height: 60),

            // 3. Features Section
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    "🎯 차별화된 3가지 기능",
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.darkText,
                    ),
                  ),
                  const SizedBox(height: 24),
                  // 타이밍 분석을 가장 먼저 배치 (차별화 포인트)
                  const FeatureCard(
                    icon: Icons.access_time_filled,
                    title: "구매 타이밍 분석",
                    description: "금리·유가·환율 등 경제지표를 분석해 '지금이 살 때인지' 알려드립니다.",
                    iconColor: AppTheme.secondaryGreen,
                  ),
                  const SizedBox(height: 16),
                  const FeatureCard(
                    icon: Icons.attach_money,
                    title: "AI 시세 예측",
                    description: "119,343대 데이터 학습 AI가 R² 0.87 정확도로 적정 가격을 산정합니다.",
                    iconColor: AppTheme.primaryBlue,
                  ),
                  const SizedBox(height: 16),
                  const FeatureCard(
                    icon: Icons.smart_toy,
                    title: "Groq AI 자문",
                    description: "허위 매물 탐지부터 가격 네고 대본까지, AI 딜러가 직접 조언해드립니다.",
                    iconColor: Colors.purple,
                  ),
                ],
              ),
            ),

            const SizedBox(height: 60),

            // 4. Bottom CTA
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(40),
              color: Colors.grey[50],
              child: Column(
                children: [
                  const Text(
                    "지금 바로 시작하세요",
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    "회원가입 없이 3초 만에 결과를 확인할 수 있습니다.",
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.grey),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () {},
                    child: const Text("무료로 분석하기"),
                  ),
                  const SizedBox(height: 40),
                  const Text(
                    "© 2025 언제 살까? - 경제지표 기반 구매 타이밍 어드바이저",
                    style: TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        backgroundColor: AppTheme.primaryBlue,
        child: const Icon(Icons.chat_bubble_outline),
      ),
    );
  }
}
