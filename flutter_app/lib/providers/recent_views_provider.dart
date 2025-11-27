import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import '../models/car_data.dart';

/// 최근 조회 차량 Provider
/// - 개별 매물 클릭 시 저장 (추천 탭 + 결과 페이지 모두)
/// - SharedPreferences를 통해 로컬 캐시 사용
class RecentViewsProvider extends ChangeNotifier {
  static const String _localCacheKey = 'recent_viewed_cars';
  static const int _maxItems = 30;
  
  // RecommendedCar 형태의 데이터 저장
  List<RecommendedCar> _recentViewedCars = [];
  bool _isLoading = false;
  
  // Legacy support
  List<CarData> _recentViews = [];
  bool _isLoggedIn = false;
  String? _error;
  
  // Getters
  List<RecommendedCar> get recentViewedCars => List.unmodifiable(_recentViewedCars);
  List<CarData> get recentViews => List.unmodifiable(_recentViews);
  bool get isLoggedIn => _isLoggedIn;
  bool get isLoading => _isLoading;
  String? get error => _error;
  int get count => _recentViewedCars.length;
  
  /// 로그인 상태 설정
  void setLoginState(bool loggedIn) {
    _isLoggedIn = loggedIn;
    notifyListeners();
  }
  
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
      // 중복 제거 (동일 차량 제거 후 맨 앞에 추가)
      _recentViewedCars.removeWhere((c) => 
        c.brand == car.brand && 
        c.model == car.model && 
        c.year == car.year &&
        c.actualPrice == car.actualPrice
      );
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
  
  /// 레거시: CarData 형태로 추가 (하위 호환)
  Future<void> addView(CarData car) async {
    try {
      _recentViews.removeWhere((c) => c.id == car.id);
      _recentViews.insert(0, car);
      if (_recentViews.length > _maxItems) {
        _recentViews = _recentViews.sublist(0, _maxItems);
      }
      notifyListeners();
    } catch (e) {
      debugPrint('Failed to add view: $e');
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
  
  /// 조회 기록 삭제 (레거시)
  Future<void> removeView(String carId) async {
    _recentViews.removeWhere((c) => c.id == carId);
    notifyListeners();
  }
  
  /// 전체 기록 삭제
  Future<void> clearAll() async {
    _recentViewedCars.clear();
    _recentViews.clear();
    notifyListeners();
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_localCacheKey);
  }
  
  /// 로그인 시 로컬 캐시를 서버로 동기화
  Future<void> syncLocalCacheToServer() async {
    if (!_isLoggedIn) return;
    
    try {
      final prefs = await SharedPreferences.getInstance();
      final cached = prefs.getString(_localCacheKey);
      
      if (cached != null) {
        final List<dynamic> items = jsonDecode(cached);
        
        // 로컬 캐시의 항목들을 서버에 저장
        for (final item in items) {
          final car = CarData.fromJson(item);
          await _saveToApi(car);
        }
        
        // 로컬 캐시 삭제
        await prefs.remove(_localCacheKey);
        
        // 서버에서 다시 로드
        await _loadFromApi();
      }
    } catch (e) {
      debugPrint('Failed to sync local cache: $e');
    }
  }
  
  // ========== Private Methods ==========
  
  /// API에서 최근 조회 기록 로드
  Future<void> _loadFromApi() async {
    try {
      final history = await _apiService.getHistory(limit: _maxLocalItems);
      _recentViews = history.map((h) => CarData(
        id: h.id?.toString() ?? DateTime.now().millisecondsSinceEpoch.toString(),
        name: '${h.brand} ${h.model}',
        price: '${h.predictedPrice?.toStringAsFixed(0) ?? 0}만원',
        info: '${h.year}년 · ${(h.mileage / 10000).toStringAsFixed(1)}만km',
        date: h.timestamp ?? '',
        color: const Color(0xFF0066FF),
      )).toList();
    } catch (e) {
      debugPrint('Failed to load from API: $e');
      // API 실패 시 로컬 캐시로 폴백
      await _loadFromLocalCache();
    }
  }
  
  /// API에 조회 기록 저장
  Future<void> _saveToApi(CarData car) async {
    try {
      // car 데이터에서 정보 추출
      final parts = car.name.split(' ');
      final brand = parts.isNotEmpty ? parts[0] : '';
      final model = parts.length > 1 ? parts.sublist(1).join(' ') : '';
      
      // info에서 연식과 주행거리 추출
      final infoMatch = RegExp(r'(\d+)년.*?(\d+\.?\d*)만km').firstMatch(car.info);
      final year = int.tryParse(infoMatch?.group(1) ?? '2020') ?? 2020;
      final mileageKm = (double.tryParse(infoMatch?.group(2) ?? '0') ?? 0) * 10000;
      
      // price에서 가격 추출
      final priceMatch = RegExp(r'(\d+)').firstMatch(car.price);
      final price = double.tryParse(priceMatch?.group(1) ?? '0') ?? 0;
      
      await _apiService.addHistory(
        brand: brand,
        model: model,
        year: year,
        mileage: mileageKm.toInt(),
        predictedPrice: price,
      );
    } catch (e) {
      debugPrint('Failed to save to API: $e');
    }
  }
  
  /// 로컬 캐시에서 로드 (RecommendedCar)
  Future<void> _loadFromLocalCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cached = prefs.getString(_localCacheKey);
      
      if (cached != null) {
        final List<dynamic> items = jsonDecode(cached);
        _recentViewedCars = items.map((item) => RecommendedCar(
          brand: item['brand'] ?? '',
          model: item['model'] ?? '',
          year: item['year'] ?? 2020,
          mileage: item['mileage'] ?? 0,
          fuel: item['fuel'] ?? '가솔린',
          actualPrice: item['actualPrice'] ?? 0,
          predictedPrice: item['predictedPrice'] ?? 0,
          priceDiff: item['priceDiff'] ?? 0,
          valueScore: (item['valueScore'] ?? 0).toDouble(),
          isGoodDeal: item['isGoodDeal'] ?? false,
          carId: item['carId'],
          detailUrl: item['detailUrl'],
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
        'brand': c.brand,
        'model': c.model,
        'year': c.year,
        'mileage': c.mileage,
        'fuel': c.fuel,
        'actualPrice': c.actualPrice,
        'predictedPrice': c.predictedPrice,
        'priceDiff': c.priceDiff,
        'valueScore': c.valueScore,
        'isGoodDeal': c.isGoodDeal,
        'carId': c.carId,
        'detailUrl': c.detailUrl,
      }).toList();
      await prefs.setString(_localCacheKey, jsonEncode(items));
    } catch (e) {
      debugPrint('Failed to save to local cache: $e');
    }
  }
}
