/// 사용자 관련 모델 클래스들
/// 
/// 분리된 위치: lib/models/user.dart
/// 원본: lib/services/api_service.dart
library;

import 'car.dart';  // RecommendedCar 사용

/// 검색 기록
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
  final int? actualPrice;      // 실제 가격 (고유 구별용)
  final String? detailUrl;     // 상세 URL (고유 구별용)
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
    this.actualPrice,
    this.detailUrl,
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
      actualPrice: json['actual_price'],
      detailUrl: json['detail_url'],
      memo: json['memo'],
      createdAt: json['created_at'],
    );
  }
  
  /// 같은 매물인지 확인 (detailUrl 또는 actualPrice+mileage 조합으로 구별)
  bool isSameDeal(RecommendedCar car) {
    // detailUrl이 있으면 우선 사용
    if (detailUrl != null && car.detailUrl != null) {
      return detailUrl == car.detailUrl;
    }
    // 없으면 브랜드+모델+연식+가격+주행거리로 구별
    return brand == car.brand && 
           model == car.model && 
           year == car.year &&
           actualPrice == car.actualPrice &&
           mileage == car.mileage;
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
      isActive: json['is_active'] ?? true,
      createdAt: json['created_at'],
    );
  }
}
