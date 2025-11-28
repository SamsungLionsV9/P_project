import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// 테마 상태 관리 Provider
class ThemeProvider extends ChangeNotifier {
  static const String _themeKey = 'isDarkMode';
  bool _isDarkMode = false;

  bool get isDarkMode => _isDarkMode;
  ThemeMode get themeMode => _isDarkMode ? ThemeMode.dark : ThemeMode.light;

  ThemeProvider() {
    _loadTheme();
  }

  /// 저장된 테마 설정 로드
  Future<void> _loadTheme() async {
    final prefs = await SharedPreferences.getInstance();
    _isDarkMode = prefs.getBool(_themeKey) ?? false;
    notifyListeners();
  }

  /// 테마 토글
  Future<void> toggleTheme() async {
    _isDarkMode = !_isDarkMode;
    notifyListeners();
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_themeKey, _isDarkMode);
  }

  /// 다크 모드 설정
  Future<void> setDarkMode(bool isDark) async {
    if (_isDarkMode == isDark) return;
    
    _isDarkMode = isDark;
    notifyListeners();
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_themeKey, _isDarkMode);
  }

  // 색상 헬퍼
  Color get backgroundColor => _isDarkMode ? const Color(0xFF1A1A1A) : const Color(0xFFF5F7FA);
  Color get cardColor => _isDarkMode ? const Color(0xFF2C2C2C) : Colors.white;
  Color get textColor => _isDarkMode ? Colors.white : Colors.black87;
  Color get subTextColor => _isDarkMode ? Colors.grey[400]! : Colors.grey[600]!;
  Color get borderColor => _isDarkMode ? Colors.grey[800]! : Colors.grey[200]!;
}
