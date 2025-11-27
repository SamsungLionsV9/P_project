import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';

/// 인기 모델 추천 Provider
/// - ml-service에서 인기 차량 데이터를 가져와 캐싱
/// - 홈페이지와 추천 탭 간 데이터 동기화
class PopularCarsProvider extends ChangeNotifier {
  static const String _domesticCacheKey = 'popular_domestic_cache';
  static const String _importedCacheKey = 'popular_imported_cache';
  static const String _recommendationsCacheKey = 'recommendations_cache';
  static const String _lastSyncKey = 'popular_last_sync';
  static const Duration _cacheValidDuration = Duration(hours: 1);
  
  final ApiService _apiService = ApiService();
  
  List<PopularCar> _domesticCars = [];
  List<PopularCar> _importedCars = [];
  List<RecommendedCar> _recommendations = [];
  
  bool _isLoading = false;
  String? _error;
  DateTime? _lastSyncTime;
  
  // Getters
  List<PopularCar> get domesticCars => List.unmodifiable(_domesticCars);
  List<PopularCar> get importedCars => List.unmodifiable(_importedCars);
  List<RecommendedCar> get recommendations => List.unmodifiable(_recommendations);
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get needsRefresh => _lastSyncTime == null || 
    DateTime.now().difference(_lastSyncTime!) > _cacheValidDuration;
  
  /// 홈 화면용 간단 데이터 (각 5개씩)
  List<PopularCar> get topDomestic => _domesticCars.take(5).toList();
  List<PopularCar> get topImported => _importedCars.take(5).toList();
  List<RecommendedCar> get topRecommendations => _recommendations.take(6).toList();
  
  /// 초기 데이터 로드 (캐시 우선, 필요시 API 호출)
  Future<void> loadData({bool forceRefresh = false}) async {
    if (_isLoading) return;
    
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      // 캐시에서 먼저 로드
      await _loadFromCache();
      notifyListeners();
      
      // 강제 새로고침이거나 캐시가 오래된 경우 API 호출
      if (forceRefresh || needsRefresh) {
        await _fetchFromApi();
        await _saveToCache();
      }
    } catch (e) {
      _error = e.toString();
      debugPrint('PopularCarsProvider Error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  /// 추천 데이터만 새로고침 (필터 적용 시)
  Future<void> refreshRecommendations({
    String? category,
    int? budgetMin,
    int? budgetMax,
  }) async {
    try {
      _recommendations = await _apiService.getRecommendations(
        category: category ?? 'all',
        budgetMin: budgetMin,
        budgetMax: budgetMax,
        limit: 20,
      );
      notifyListeners();
    } catch (e) {
      debugPrint('Failed to refresh recommendations: $e');
    }
  }
  
  /// 카테고리별 인기 모델 조회
  List<PopularCar> getPopularByCategory(String category) {
    switch (category) {
      case 'domestic':
        return _domesticCars;
      case 'imported':
        return _importedCars;
      default:
        return [..._domesticCars, ..._importedCars];
    }
  }
  
  // ========== Private Methods ==========
  
  Future<void> _fetchFromApi() async {
    final results = await Future.wait([
      _apiService.getPopular(category: 'domestic', limit: 10),
      _apiService.getPopular(category: 'imported', limit: 10),
      _apiService.getRecommendations(category: 'all', limit: 20),
    ]);
    
    _domesticCars = results[0] as List<PopularCar>;
    _importedCars = results[1] as List<PopularCar>;
    _recommendations = results[2] as List<RecommendedCar>;
    _lastSyncTime = DateTime.now();
  }
  
  Future<void> _loadFromCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      // 마지막 동기화 시간 확인
      final lastSyncStr = prefs.getString(_lastSyncKey);
      if (lastSyncStr != null) {
        _lastSyncTime = DateTime.tryParse(lastSyncStr);
      }
      
      // 국산차 캐시
      final domesticJson = prefs.getString(_domesticCacheKey);
      if (domesticJson != null) {
        final List<dynamic> items = jsonDecode(domesticJson);
        _domesticCars = items.map((e) => PopularCar.fromJson(e)).toList();
      }
      
      // 수입차 캐시
      final importedJson = prefs.getString(_importedCacheKey);
      if (importedJson != null) {
        final List<dynamic> items = jsonDecode(importedJson);
        _importedCars = items.map((e) => PopularCar.fromJson(e)).toList();
      }
      
      // 추천 캐시
      final recJson = prefs.getString(_recommendationsCacheKey);
      if (recJson != null) {
        final List<dynamic> items = jsonDecode(recJson);
        _recommendations = items.map((e) => RecommendedCar.fromJson(e)).toList();
      }
    } catch (e) {
      debugPrint('Failed to load from cache: $e');
    }
  }
  
  Future<void> _saveToCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      await prefs.setString(_lastSyncKey, DateTime.now().toIso8601String());
      await prefs.setString(
        _domesticCacheKey, 
        jsonEncode(_domesticCars.map((e) => e.toJson()).toList())
      );
      await prefs.setString(
        _importedCacheKey, 
        jsonEncode(_importedCars.map((e) => e.toJson()).toList())
      );
      await prefs.setString(
        _recommendationsCacheKey, 
        jsonEncode(_recommendations.map((e) => e.toJson()).toList())
      );
    } catch (e) {
      debugPrint('Failed to save to cache: $e');
    }
  }
}
