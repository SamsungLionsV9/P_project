import 'dart:convert';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:http/http.dart' as http;

/// Car-Sentix API Service
/// ML 서비스와 통신하는 클라이언트
/// 
/// 고도화 버전 v2.0
/// - 에뮬레이터 자동 감지 (Android: 10.0.2.2)
/// - 타임아웃 설정 (15초)
/// - 에러 핸들링 강화
/// - 연결 상태 확인
class ApiService {
  // 서버 포트
  static const int _port = 8001;
  
  // 타임아웃 설정
  static const Duration _timeout = Duration(seconds: 15);
  
  // 베이스 URL (플랫폼에 따라 자동 설정)
  static String get _baseUrl {
    if (kIsWeb) {
      return 'http://localhost:$_port/api';
    }
    // Android 에뮬레이터에서는 10.0.2.2가 호스트 머신의 localhost
    if (Platform.isAndroid) {
      return 'http://10.0.2.2:$_port/api';
    }
    // iOS 시뮬레이터, Windows, macOS 등
    return 'http://localhost:$_port/api';
  }
  
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();
  
  /// 현재 사용 중인 URL 확인 (디버깅용)
  String get currentBaseUrl => _baseUrl;

  /// 가격 예측
  Future<PredictionResult> predict({
    required String brand,
    required String model,
    required int year,
    required int mileage,
    required String fuel,
    bool hasSunroof = false,
    bool hasNavigation = false,
    bool hasLeatherSeat = false,
    bool hasSmartKey = false,
    bool hasRearCamera = false,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/predict'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'brand': brand,
          'model': model,
          'year': year,
          'mileage': mileage,
          'fuel': fuel,
          'has_sunroof': hasSunroof,
          'has_navigation': hasNavigation,
          'has_leather_seat': hasLeatherSeat,
          'has_smart_key': hasSmartKey,
          'has_rear_camera': hasRearCamera,
        }),
      ).timeout(_timeout);

      if (response.statusCode == 200) {
        return PredictionResult.fromJson(jsonDecode(response.body));
      } else {
        final error = _parseError(response);
        throw ApiException('가격 예측 실패: $error');
      }
    } on http.ClientException catch (e) {
      throw ApiException('서버 연결 실패: ${e.message}');
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('네트워크 오류: $e');
    }
  }

  /// 타이밍 분석
  Future<TimingResult> analyzeTiming(String model) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/timing'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'model': model}),
    );

    if (response.statusCode == 200) {
      return TimingResult.fromJson(jsonDecode(response.body));
    } else {
      throw ApiException('타이밍 분석 실패');
    }
  }

  /// 통합 스마트 분석 (가격 + 타이밍 + AI)
  Future<SmartAnalysisResult> smartAnalysis({
    required String brand,
    required String model,
    required int year,
    required int mileage,
    required String fuel,
    // 옵션
    bool hasSunroof = false,
    bool hasNavigation = false,
    bool hasLeatherSeat = false,
    bool hasSmartKey = false,
    bool hasRearCamera = false,
    bool hasHeatedSeat = false,
    bool hasVentilatedSeat = false,
    bool hasLedLamp = false,
    bool isAccidentFree = true,
    // AI 분석용
    int? salePrice,
    String? dealerDescription,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/smart-analysis'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'brand': brand,
          'model': model,
          'year': year,
          'mileage': mileage,
          'fuel': fuel,
          // 옵션
          'has_sunroof': hasSunroof,
          'has_navigation': hasNavigation,
          'has_leather_seat': hasLeatherSeat,
          'has_smart_key': hasSmartKey,
          'has_rear_camera': hasRearCamera,
          'has_heated_seat': hasHeatedSeat,
          'has_ventilated_seat': hasVentilatedSeat,
          'has_led_lamp': hasLedLamp,
          'is_accident_free': isAccidentFree,
          if (salePrice != null) 'sale_price': salePrice,
          if (dealerDescription != null) 'dealer_description': dealerDescription,
        }),
      ).timeout(_timeout);

      if (response.statusCode == 200) {
        return SmartAnalysisResult.fromJson(jsonDecode(response.body));
      } else {
        final error = _parseError(response);
        throw ApiException('통합 분석 실패: $error');
      }
    } on http.ClientException catch (e) {
      throw ApiException('서버 연결 실패: ${e.message}');
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('네트워크 오류: $e');
    }
  }

  /// 비슷한 차량 분포
  Future<SimilarResult> getSimilar({
    required String brand,
    required String model,
    required int year,
    required int mileage,
    required double predictedPrice,
  }) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/similar'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'brand': brand,
        'model': model,
        'year': year,
        'mileage': mileage,
        'predicted_price': predictedPrice,
      }),
    );

    if (response.statusCode == 200) {
      return SimilarResult.fromJson(jsonDecode(response.body));
    } else {
      throw ApiException('비슷한 차량 조회 실패');
    }
  }

  /// 인기 차량
  Future<List<PopularCar>> getPopular({
    String category = 'all',
    int limit = 5,
  }) async {
    final response = await http.get(
      Uri.parse('$_baseUrl/popular?category=$category&limit=$limit'),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return (data['models'] as List)
          .map((e) => PopularCar.fromJson(e))
          .toList();
    } else {
      throw ApiException('인기 차량 조회 실패');
    }
  }

  /// 브랜드 목록
  Future<List<String>> getBrands() async {
    final response = await http.get(Uri.parse('$_baseUrl/brands'));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return List<String>.from(data['brands']);
    } else {
      throw ApiException('브랜드 목록 조회 실패');
    }
  }

  /// 모델 목록
  Future<List<String>> getModels(String brand) async {
    final response = await http.get(Uri.parse('$_baseUrl/models/$brand'));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return List<String>.from(data['models']);
    } else {
      throw ApiException('모델 목록 조회 실패');
    }
  }

  /// 검색 이력
  Future<List<SearchHistory>> getHistory({int limit = 10}) async {
    final response = await http.get(
      Uri.parse('$_baseUrl/history?limit=$limit'),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return (data['history'] as List)
          .map((e) => SearchHistory.fromJson(e))
          .toList();
    } else {
      throw ApiException('검색 이력 조회 실패');
    }
  }

  /// 추천 차량 목록
  Future<List<RecommendedCar>> getRecommendations({
    String category = 'all',
    int? budgetMin,
    int? budgetMax,
    int limit = 10,
  }) async {
    var url = '$_baseUrl/recommendations?category=$category&limit=$limit';
    if (budgetMin != null) url += '&budget_min=$budgetMin';
    if (budgetMax != null) url += '&budget_max=$budgetMax';
    
    final response = await http.get(Uri.parse(url)).timeout(_timeout);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return (data['recommendations'] as List)
          .map((e) => RecommendedCar.fromJson(e))
          .toList();
    } else {
      throw ApiException('추천 차량 조회 실패');
    }
  }

  /// 가성비 좋은 차량
  Future<List<RecommendedCar>> getGoodDeals({
    String category = 'all',
    int limit = 10,
  }) async {
    final response = await http.get(
      Uri.parse('$_baseUrl/good-deals?category=$category&limit=$limit'),
    ).timeout(_timeout);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return (data['deals'] as List)
          .map((e) => RecommendedCar.fromJson(e))
          .toList();
    } else {
      throw ApiException('가성비 차량 조회 실패');
    }
  }

  /// 트렌딩 모델
  Future<List<Map<String, dynamic>>> getTrending({int days = 7, int limit = 10}) async {
    final response = await http.get(
      Uri.parse('$_baseUrl/trending?days=$days&limit=$limit'),
    ).timeout(_timeout);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return List<Map<String, dynamic>>.from(data['trending'] ?? []);
    } else {
      throw ApiException('트렌딩 조회 실패');
    }
  }

  // ========== 즐겨찾기 API ==========

  /// 즐겨찾기 목록 조회
  Future<List<Favorite>> getFavorites() async {
    final response = await http.get(
      Uri.parse('$_baseUrl/favorites'),
    ).timeout(_timeout);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return (data['favorites'] as List)
          .map((e) => Favorite.fromJson(e))
          .toList();
    } else {
      throw ApiException('즐겨찾기 조회 실패');
    }
  }

  /// 즐겨찾기 추가
  Future<Map<String, dynamic>> addFavorite({
    required String brand,
    required String model,
    required int year,
    required int mileage,
    double? predictedPrice,
  }) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/favorites'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'brand': brand,
        'model': model,
        'year': year,
        'mileage': mileage,
        'predicted_price': predictedPrice,
      }),
    ).timeout(_timeout);

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw ApiException('즐겨찾기 추가 실패');
    }
  }

  /// 즐겨찾기 삭제
  Future<bool> removeFavorite(int favoriteId) async {
    final response = await http.delete(
      Uri.parse('$_baseUrl/favorites/$favoriteId'),
    ).timeout(_timeout);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['success'] ?? false;
    } else {
      throw ApiException('즐겨찾기 삭제 실패');
    }
  }

  // ========== 가격 알림 API ==========

  /// 알림 목록 조회
  Future<List<PriceAlert>> getAlerts() async {
    final response = await http.get(
      Uri.parse('$_baseUrl/alerts'),
    ).timeout(_timeout);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return (data['alerts'] as List)
          .map((e) => PriceAlert.fromJson(e))
          .toList();
    } else {
      throw ApiException('알림 조회 실패');
    }
  }

  /// 알림 추가
  Future<Map<String, dynamic>> addAlert({
    required String brand,
    required String model,
    required int year,
    required double targetPrice,
  }) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/alerts'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'brand': brand,
        'model': model,
        'year': year,
        'target_price': targetPrice,
      }),
    ).timeout(_timeout);

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw ApiException('알림 추가 실패');
    }
  }

  /// 알림 토글
  Future<Map<String, dynamic>> toggleAlert(int alertId) async {
    final response = await http.put(
      Uri.parse('$_baseUrl/alerts/$alertId/toggle'),
    ).timeout(_timeout);

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw ApiException('알림 토글 실패');
    }
  }

  /// 알림 삭제
  Future<bool> removeAlert(int alertId) async {
    final response = await http.delete(
      Uri.parse('$_baseUrl/alerts/$alertId'),
    ).timeout(_timeout);

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['success'] ?? false;
    } else {
      throw ApiException('알림 삭제 실패');
    }
  }

  /// 검색 이력 저장
  Future<void> saveSearchHistory({
    required String brand,
    required String model,
    required int year,
    required int mileage,
    double? predictedPrice,
  }) async {
    try {
      await http.post(
        Uri.parse('$_baseUrl/history'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'brand': brand,
          'model': model,
          'year': year,
          'mileage': mileage,
          'predicted_price': predictedPrice,
        }),
      ).timeout(_timeout);
    } catch (e) {
      // 이력 저장 실패해도 무시 (크리티컬하지 않음)
    }
  }

  /// 헬스체크 (연결 상태 확인)
  Future<bool> healthCheck() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/health'),
      ).timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
  
  /// 연결 상태 상세 정보
  Future<Map<String, dynamic>> getConnectionStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/health'),
      ).timeout(const Duration(seconds: 5));
      
      if (response.statusCode == 200) {
        return {
          'connected': true,
          'baseUrl': _baseUrl,
          'data': jsonDecode(response.body),
        };
      }
      return {
        'connected': false,
        'baseUrl': _baseUrl,
        'error': 'Status: ${response.statusCode}',
      };
    } catch (e) {
      return {
        'connected': false,
        'baseUrl': _baseUrl,
        'error': e.toString(),
      };
    }
  }
  
  /// 에러 메시지 파싱
  String _parseError(http.Response response) {
    try {
      final data = jsonDecode(response.body);
      return data['detail'] ?? data['message'] ?? 'Unknown error';
    } catch (_) {
      return 'Status ${response.statusCode}';
    }
  }
}

// ========== Data Models ==========

class PredictionResult {
  final double predictedPrice;
  final List<double> priceRange;
  final double confidence;

  PredictionResult({
    required this.predictedPrice,
    required this.priceRange,
    required this.confidence,
  });

  factory PredictionResult.fromJson(Map<String, dynamic> json) {
    return PredictionResult(
      predictedPrice: (json['predicted_price'] as num).toDouble(),
      priceRange: (json['price_range'] as List).map((e) => (e as num).toDouble()).toList(),
      confidence: (json['confidence'] as num).toDouble(),
    );
  }

  String get formattedPrice => '${predictedPrice.toStringAsFixed(0)}만원';
  String get formattedRange => 
      '${priceRange[0].toStringAsFixed(0)} ~ ${priceRange[1].toStringAsFixed(0)}만원';
}

class TimingResult {
  final double timingScore;
  final String decision;
  final String color;
  final Map<String, double> breakdown;
  final List<String> reasons;

  TimingResult({
    required this.timingScore,
    required this.decision,
    required this.color,
    required this.breakdown,
    required this.reasons,
  });

  factory TimingResult.fromJson(Map<String, dynamic> json) {
    return TimingResult(
      timingScore: (json['timing_score'] as num).toDouble(),
      decision: json['decision'] as String,
      color: json['color'] as String,
      breakdown: Map<String, double>.from(
        (json['breakdown'] as Map).map((k, v) => MapEntry(k, (v as num).toDouble())),
      ),
      reasons: List<String>.from(json['reasons']),
    );
  }

  bool get isGoodTime => timingScore >= 70;
}

class SmartAnalysisResult {
  final PredictionResult prediction;
  final TimingResult timing;
  final Map<String, dynamic>? groqAnalysis;

  SmartAnalysisResult({
    required this.prediction,
    required this.timing,
    this.groqAnalysis,
  });

  factory SmartAnalysisResult.fromJson(Map<String, dynamic> json) {
    return SmartAnalysisResult(
      prediction: PredictionResult.fromJson(json['prediction']),
      timing: TimingResult.fromJson(json['timing']),
      groqAnalysis: json['groq_analysis'] as Map<String, dynamic>?,
    );
  }

  // AI 신호 (매수/관망/회피)
  String? get signal => groqAnalysis?['signal']?['signal'];
  String? get signalEmoji => groqAnalysis?['signal']?['emoji'];
  
  // 허위매물 의심도
  int? get fraudScore => groqAnalysis?['fraud_check']?['fraud_score'];
  
  // 네고 대본
  String? get messageScript => groqAnalysis?['negotiation']?['message_script'];
  String? get phoneScript => groqAnalysis?['negotiation']?['phone_script'];
}

class SimilarResult {
  final int similarCount;
  final Map<String, dynamic>? priceDistribution;
  final List<Map<String, dynamic>> histogram;
  final String yourPosition;
  final String positionColor;

  SimilarResult({
    required this.similarCount,
    this.priceDistribution,
    required this.histogram,
    required this.yourPosition,
    required this.positionColor,
  });

  factory SimilarResult.fromJson(Map<String, dynamic> json) {
    return SimilarResult(
      similarCount: json['similar_count'] as int,
      priceDistribution: json['price_distribution'] as Map<String, dynamic>?,
      histogram: List<Map<String, dynamic>>.from(json['histogram'] ?? []),
      yourPosition: json['your_position'] as String,
      positionColor: json['position_color'] as String,
    );
  }
}

class PopularCar {
  final String brand;
  final String model;
  final int listings;  // 엔카 등록 대수
  final int avgPrice;
  final int medianPrice;
  final String? type;  // domestic/imported

  PopularCar({
    required this.brand,
    required this.model,
    required this.listings,
    required this.avgPrice,
    required this.medianPrice,
    this.type,
  });

  factory PopularCar.fromJson(Map<String, dynamic> json) {
    return PopularCar(
      brand: json['brand'] as String,
      model: json['model'] as String,
      listings: json['listings'] ?? json['searches'] ?? 0,
      avgPrice: json['avg_price'] ?? 0,
      medianPrice: json['median_price'] ?? json['avg_price'] ?? 0,
      type: json['type'],
    );
  }
}

/// 추천 차량
class RecommendedCar {
  final String brand;
  final String model;
  final int year;
  final int mileage;
  final String fuel;
  final int actualPrice;
  final int predictedPrice;
  final int priceDiff;
  final bool isGoodDeal;
  final double score;
  final String type;

  RecommendedCar({
    required this.brand,
    required this.model,
    required this.year,
    required this.mileage,
    required this.fuel,
    required this.actualPrice,
    required this.predictedPrice,
    required this.priceDiff,
    required this.isGoodDeal,
    required this.score,
    required this.type,
  });

  factory RecommendedCar.fromJson(Map<String, dynamic> json) {
    return RecommendedCar(
      brand: json['brand'] ?? '',
      model: json['model'] ?? '',
      year: json['year'] ?? 0,
      mileage: json['mileage'] ?? 0,
      fuel: json['fuel'] ?? '가솔린',
      actualPrice: json['actual_price'] ?? 0,
      predictedPrice: json['predicted_price'] ?? 0,
      priceDiff: json['price_diff'] ?? 0,
      isGoodDeal: json['is_good_deal'] ?? false,
      score: (json['score'] ?? 0).toDouble(),
      type: json['type'] ?? 'domestic',
    );
  }
  
  String get formattedMileage => '${(mileage / 10000).toStringAsFixed(1)}만 km';
  String get priceTag => isGoodDeal ? '🔥 가성비' : '';
}

class SearchHistory {
  final int? id;
  final String? timestamp;
  final String brand;
  final String model;
  final int year;
  final int mileage;
  final String? fuel;
  final double? predictedPrice;
  final String? lastSearched;

  SearchHistory({
    this.id,
    this.timestamp,
    required this.brand,
    required this.model,
    required this.year,
    required this.mileage,
    this.fuel,
    this.predictedPrice,
    this.lastSearched,
  });

  factory SearchHistory.fromJson(Map<String, dynamic> json) {
    return SearchHistory(
      id: json['id'],
      timestamp: json['timestamp'] ?? json['searched_at'],
      brand: json['brand'] ?? '',
      model: json['model'] ?? '',
      year: json['year'] ?? 0,
      mileage: json['mileage'] ?? 0,
      fuel: json['fuel'],
      predictedPrice: json['predicted_price']?.toDouble(),
      lastSearched: json['last_searched'],
    );
  }
}

/// 즐겨찾기 모델
class Favorite {
  final int id;
  final String brand;
  final String model;
  final int year;
  final int mileage;
  final String? fuel;
  final double? predictedPrice;
  final String? memo;
  final String? createdAt;

  Favorite({
    required this.id,
    required this.brand,
    required this.model,
    required this.year,
    required this.mileage,
    this.fuel,
    this.predictedPrice,
    this.memo,
    this.createdAt,
  });

  factory Favorite.fromJson(Map<String, dynamic> json) {
    return Favorite(
      id: json['id'] ?? 0,
      brand: json['brand'] ?? '',
      model: json['model'] ?? '',
      year: json['year'] ?? 0,
      mileage: json['mileage'] ?? 0,
      fuel: json['fuel'],
      predictedPrice: json['predicted_price']?.toDouble(),
      memo: json['memo'],
      createdAt: json['created_at'],
    );
  }
}

/// 가격 알림 모델
class PriceAlert {
  final int id;
  final String brand;
  final String model;
  final int year;
  final double targetPrice;
  final bool isActive;
  final String? createdAt;

  PriceAlert({
    required this.id,
    required this.brand,
    required this.model,
    required this.year,
    required this.targetPrice,
    required this.isActive,
    this.createdAt,
  });

  factory PriceAlert.fromJson(Map<String, dynamic> json) {
    return PriceAlert(
      id: json['id'] ?? 0,
      brand: json['brand'] ?? '',
      model: json['model'] ?? '',
      year: json['year'] ?? 0,
      targetPrice: (json['target_price'] ?? 0).toDouble(),
      isActive: json['is_active'] ?? false,
      createdAt: json['created_at'],
    );
  }
}

class ApiException implements Exception {
  final String message;
  ApiException(this.message);

  @override
  String toString() => message;
}
