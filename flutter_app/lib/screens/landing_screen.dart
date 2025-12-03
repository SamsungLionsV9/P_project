import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../widgets/hero_section.dart';
import '../widgets/feature_card.dart';
import '../widgets/interactive_demo.dart';

import '../car_info_input_page.dart';

class LandingScreen extends StatelessWidget {
  const LandingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.directions_car, color: AppTheme.primaryBlue),
            SizedBox(width: 8),
            Text("Car-Sentix"),
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
                Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) => const CarInfoInputPage()),
                );
              },
            ),

            const SizedBox(height: 40),

            // 2. Interactive Demo
            const InteractiveDemo(),

            const SizedBox(height: 60),

            // 3. Features Section
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    "🎯 3가지 핵심 기능",
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.darkText,
                    ),
                  ),
                  SizedBox(height: 24),
                  FeatureCard(
                    icon: Icons.attach_money,
                    title: "AI 가격 예측",
                    description:
                        "119,343대 데이터를 학습한 AI가 R² 0.87 정확도로 적정 시세를 알려드립니다.",
                    iconColor: AppTheme.primaryBlue,
                  ),
                  SizedBox(height: 16),
                  FeatureCard(
                    icon: Icons.timeline,
                    title: "시장 타이밍 분석",
                    description: "금리, 유가, 신차 출시일 등 거시 데이터를 분석해 '살 때'를 알려드립니다.",
                    iconColor: AppTheme.secondaryGreen,
                  ),
                  SizedBox(height: 16),
                  FeatureCard(
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
                    "© 2025 Car-Sentix. Built with Flutter & Python",
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
