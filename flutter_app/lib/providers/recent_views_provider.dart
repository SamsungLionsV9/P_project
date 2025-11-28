import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';

/// 최근 조회 차량 Provider
/// - 개별 매물 클릭 시 저장 (추천 탭 + 결과 페이지 모두)
/// - SharedPreferences를 통해 로컬 캐시 사용
/// - source 필드로 'analysis' (분석) vs 'recommendation' (추천) 구분
class RecentViewsProvider extends ChangeNotifier {
  static const String _localCacheKey = 'recent_viewed_cars_v4';  // 버전 업 (carId 필드 추가)
  static const int _maxItems = 30;
  
  List<RecommendedCar> _recentViewedCars = [];
  bool _isLoading = false;
  String? _error;
  
  // Getters
  /// 전체 최근 조회 차량 (홈 화면용 - 분석 + 추천 모두)
  List<RecommendedCar> get recentViewedCars => List.unmodifiable(_recentViewedCars);
  
  /// 추천 탭에서 조회한 차량만 (추천 페이지 "최근 조회" 탭용)
  List<RecommendedCar> get recommendationOnlyCars => 
      List.unmodifiable(_recentViewedCars.where((c) => c.source == 'recommendation').toList());
  
  /// 분석 페이지에서 조회한 차량만
  List<RecommendedCar> get analysisOnlyCars => 
      List.unmodifiable(_recentViewedCars.where((c) => c.source == 'analysis').toList());
  
  bool get isLoading => _isLoading;
  String? get error => _error;
  int get count => _recentViewedCars.length;
  
  /// 초기 데이터 로드
  Future<void> loadRecentViews() async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      await _loadFromLocalCache();
    } catch (e) {
      _error = e.toString();
      debugPrint('RecentViewsProvider Error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  /// 매물 조회 기록 추가 (RecommendedCar)
  Future<void> addRecentCar(RecommendedCar car) async {
    try {
      // 중복 제거 (carId > actualPrice 순으로 비교)
      _recentViewedCars.removeWhere((c) {
        // carId가 있으면 carId로 비교
        if (c.carId != null && c.carId!.isNotEmpty && 
            car.carId != null && car.carId!.isNotEmpty) {
          return c.carId == car.carId;
        }
        // 없으면 brand+model+year+actualPrice+mileage로 비교
        return c.brand == car.brand && 
               c.model == car.model && 
               c.year == car.year &&
               c.actualPrice == car.actualPrice &&
               c.mileage == car.mileage;
      });
      _recentViewedCars.insert(0, car);
      
      // 최대 개수 제한
      if (_recentViewedCars.length > _maxItems) {
        _recentViewedCars = _recentViewedCars.sublist(0, _maxItems);
      }
      
      notifyListeners();
      await _saveToLocalCache();
    } catch (e) {
      debugPrint('Failed to add recent car: $e');
    }
  }
  
  /// 조회 기록 삭제 (인덱스 기반)
  Future<void> removeAt(int index) async {
    if (index >= 0 && index < _recentViewedCars.length) {
      _recentViewedCars.removeAt(index);
      notifyListeners();
      await _saveToLocalCache();
    }
  }
  
  /// 전체 기록 삭제
  Future<void> clearAll() async {
    _recentViewedCars.clear();
    notifyListeners();
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_localCacheKey);
  }
  
  /// 특정 source의 기록만 삭제
  Future<void> clearBySource(String source) async {
    _recentViewedCars.removeWhere((c) => c.source == source);
    notifyListeners();
    await _saveToLocalCache();
  }
  
  // ========== Private Methods ==========
  
  /// 로컬 캐시에서 로드 (RecommendedCar)
  Future<void> _loadFromLocalCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cached = prefs.getString(_localCacheKey);
      
      if (cached != null) {
        final List<dynamic> items = jsonDecode(cached);
        _recentViewedCars = items.map<RecommendedCar>((item) => RecommendedCar(
          carId: item['carId'],  // 엔카 차량 고유 ID
          brand: item['brand'] ?? '',
          model: item['model'] ?? '',
          year: item['year'] ?? 2020,
          mileage: item['mileage'] ?? 0,
          fuel: item['fuel'] ?? '가솔린',
          actualPrice: item['actualPrice'] ?? 0,
          predictedPrice: item['predictedPrice'] ?? 0,
          priceDiff: item['priceDiff'] ?? 0,
          score: (item['score'] ?? 0).toDouble(),
          isGoodDeal: item['isGoodDeal'] ?? false,
          type: item['type'] ?? 'domestic',
          detailUrl: item['detailUrl'],
          source: item['source'] ?? 'recommendation',
          options: item['options'] != null ? CarOptions.fromJson(item['options']) : null,
        )).toList();
      }
    } catch (e) {
      debugPrint('Failed to load from local cache: $e');
      _recentViewedCars = [];
    }
  }
  
  /// 로컬 캐시에 저장 (RecommendedCar)
  Future<void> _saveToLocalCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final items = _recentViewedCars.map((c) => {
        'carId': c.carId,  // 엔카 차량 고유 ID
        'brand': c.brand,
        'model': c.model,
        'year': c.year,
        'mileage': c.mileage,
        'fuel': c.fuel,
        'actualPrice': c.actualPrice,
        'predictedPrice': c.predictedPrice,
        'priceDiff': c.priceDiff,
        'score': c.score,
        'isGoodDeal': c.isGoodDeal,
        'type': c.type,
        'detailUrl': c.detailUrl,
        'source': c.source,
        'options': c.options?.toJson(),
      }).toList();
      await prefs.setString(_localCacheKey, jsonEncode(items));
    } catch (e) {
      debugPrint('Failed to save to local cache: $e');
    }
  }
}
