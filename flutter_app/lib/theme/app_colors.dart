import 'package:flutter/material.dart';

/// 앱 전역 색상 시스템 (토스/당근마켓 스타일)
class AppColors {
  // Primary (메인 브랜드 색상)
  static const primary = Color(0xFF2D5BFF);
  static const primaryLight = Color(0xFF5A7FFF);
  static const primaryDark = Color(0xFF1E3A8A);
  
  // Semantic (의미있는 색상)
  static const success = Color(0xFF10B981);  // 구매 적기
  static const warning = Color(0xFFF59E0B);  // 보통
  static const error = Color(0xFFEF4444);    // 대기
  
  // Neutral (배경/텍스트)
  static const gray50 = Color(0xFFF9FAFB);
  static const gray100 = Color(0xFFF3F4F6);
  static const gray200 = Color(0xFFE5E7EB);
  static const gray400 = Color(0xFF9CA3AF);
  static const gray600 = Color(0xFF4B5563);
  static const gray900 = Color(0xFF111827);
  
  // Gradient
  static const primaryGradient = LinearGradient(
    colors: [Color(0xFF2D5BFF), Color(0xFF8B5CF6)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const successGradient = LinearGradient(
    colors: [Color(0xFF10B981), Color(0xFF34D399)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  // 타이밍 점수 색상
  static Color getTimingColor(double score) {
    if (score >= 70) return success;
    if (score >= 50) return warning;
    return error;
  }
}
