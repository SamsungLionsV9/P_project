import 'package:flutter/material.dart';

class AppTheme {
  // 브랜드 컬러
  static const Color primaryBlue = Color(0xFF2563EB);  // 신뢰의 파란색
  static const Color secondaryGreen = Color(0xFF10B981); // 긍정/매수
  static const Color warningYellow = Color(0xFFF59E0B); // 관망
  static const Color dangerRed = Color(0xFFEF4444);    // 회피
  static const Color darkText = Color(0xFF1F2937);
  static const Color lightBg = Color(0xFFF9FAFB);

  static ThemeData get theme {
    return ThemeData(
      primaryColor: primaryBlue,
      scaffoldBackgroundColor: Colors.white,
      fontFamily: 'Pretendard', // 한글 폰트 권장 (없으면 기본)
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: IconThemeData(color: darkText),
        titleTextStyle: TextStyle(
          color: darkText,
          fontSize: 20,
          fontWeight: FontWeight.bold,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryBlue,
          foregroundColor: Colors.white,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
        ),
      ),
    );
  }
}
