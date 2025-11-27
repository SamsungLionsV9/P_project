import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import '../models/car_data.dart';

/// 최근 조회 차량 Provider
/// - 로그인 상태: 백엔드 API를 통해 DB에 저장/조회
/// - 비로그인 상태: SharedPreferences를 통해 로컬 캐시 사용
class RecentViewsProvider extends ChangeNotifier {
  static const String _localCacheKey = 'recent_views_cache';
  static const int _maxLocalItems = 20;
  
  final ApiService _apiService = ApiService();
  
  List<CarData> _recentViews = [];
  bool _isLoggedIn = false;
  bool _isLoading = false;
  String? _error;
  
  // Getters
  List<CarData> get recentViews => List.unmodifiable(_recentViews);
  bool get isLoggedIn => _isLoggedIn;
  bool get isLoading => _isLoading;
  String? get error => _error;
  int get count => _recentViews.length;
  
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
      if (_isLoggedIn) {
        // 로그인 상태: API에서 가져오기
        await _loadFromApi();
      } else {
        // 비로그인 상태: 로컬 캐시에서 가져오기
        await _loadFromLocalCache();
      }
    } catch (e) {
      _error = e.toString();
      debugPrint('RecentViewsProvider Error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  /// 차량 조회 기록 추가
  Future<void> addView(CarData car) async {
    try {
      // 중복 제거 후 맨 앞에 추가
      _recentViews.removeWhere((c) => c.id == car.id);
      _recentViews.insert(0, car);
      
      // 최대 개수 제한
      if (_recentViews.length > _maxLocalItems) {
        _recentViews = _recentViews.sublist(0, _maxLocalItems);
      }
      
      notifyListeners();
      
      if (_isLoggedIn) {
        // 로그인 상태: API로 저장
        await _saveToApi(car);
      } else {
        // 비로그인 상태: 로컬 캐시에 저장
        await _saveToLocalCache();
      }
    } catch (e) {
      debugPrint('Failed to add view: $e');
    }
  }
  
  /// 조회 기록 삭제
  Future<void> removeView(String carId) async {
    _recentViews.removeWhere((c) => c.id == carId);
    notifyListeners();
    
    if (!_isLoggedIn) {
      await _saveToLocalCache();
    }
  }
  
  /// 전체 기록 삭제
  Future<void> clearAll() async {
    _recentViews.clear();
    notifyListeners();
    
    if (!_isLoggedIn) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_localCacheKey);
    }
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
  
  /// 로컬 캐시에서 로드
  Future<void> _loadFromLocalCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cached = prefs.getString(_localCacheKey);
      
      if (cached != null) {
        final List<dynamic> items = jsonDecode(cached);
        _recentViews = items.map((item) => CarData.fromJson(item)).toList();
      }
    } catch (e) {
      debugPrint('Failed to load from local cache: $e');
      _recentViews = [];
    }
  }
  
  /// 로컬 캐시에 저장
  Future<void> _saveToLocalCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final items = _recentViews.map((c) => c.toJson()).toList();
      await prefs.setString(_localCacheKey, jsonEncode(items));
    } catch (e) {
      debugPrint('Failed to save to local cache: $e');
    }
  }
}
