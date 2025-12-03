/// 차량 관련 모델 클래스들
/// 
/// 분리된 위치: lib/models/car.dart
/// 원본: lib/services/api_service.dart
library;

/// 차량 옵션 정보
class CarOptions {
  final bool isAccidentFree;
  final String inspectionGrade;
  final bool hasSunroof;
  final bool hasNavigation;
  final bool hasLeatherSeat;
  final bool hasSmartKey;
  final bool hasRearCamera;
  final bool hasHeatedSeat;
  final bool hasVentilatedSeat;

  CarOptions({
    this.isAccidentFree = false,
    this.inspectionGrade = '',
    this.hasSunroof = false,
    this.hasNavigation = false,
    this.hasLeatherSeat = false,
    this.hasSmartKey = false,
    this.hasRearCamera = false,
    this.hasHeatedSeat = false,
    this.hasVentilatedSeat = false,
  });

  factory CarOptions.fromJson(Map<String, dynamic>? json) {
    if (json == null) return CarOptions();
    return CarOptions(
      isAccidentFree: json['is_accident_free'] ?? false,
      inspectionGrade: json['inspection_grade'] ?? '',
      hasSunroof: json['has_sunroof'] ?? false,
      hasNavigation: json['has_navigation'] ?? false,
      hasLeatherSeat: json['has_leather_seat'] ?? false,
      hasSmartKey: json['has_smart_key'] ?? false,
      hasRearCamera: json['has_rear_camera'] ?? false,
      hasHeatedSeat: json['has_heated_seat'] ?? false,
      hasVentilatedSeat: json['has_ventilated_seat'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'is_accident_free': isAccidentFree,
      'inspection_grade': inspectionGrade,
      'has_sunroof': hasSunroof,
      'has_navigation': hasNavigation,
      'has_leather_seat': hasLeatherSeat,
      'has_smart_key': hasSmartKey,
      'has_rear_camera': hasRearCamera,
      'has_heated_seat': hasHeatedSeat,
      'has_ventilated_seat': hasVentilatedSeat,
    };
  }
  
  /// 옵션 목록 (있는 것만)
  List<String> get optionList {
    final list = <String>[];
    if (isAccidentFree) list.add('무사고');
    if (hasSunroof) list.add('선루프');
    if (hasNavigation) list.add('내비게이션');
    if (hasLeatherSeat) list.add('가죽시트');
    if (hasSmartKey) list.add('스마트키');
    if (hasRearCamera) list.add('후방카메라');
    if (hasHeatedSeat) list.add('열선시트');
    if (hasVentilatedSeat) list.add('통풍시트');
    return list;
  }
  
  /// 성능점검 등급 텍스트
  String get inspectionText {
    switch (inspectionGrade) {
      case 'excellent': return '★★★★★';
      case 'good': return '★★★★';
      case 'normal': return '★★★';
      case 'average': return '★★★';
      case 'poor': return '★★';
      default: return '';
    }
  }
}

/// 추천/실매물 차량 정보
class RecommendedCar {
  final String? carId;      // 엔카 차량 고유 ID (핵심 식별자)
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
  final String? detailUrl;
  final String? imageUrl;
  final String source;      // 'analysis' 또는 'recommendation'
  final CarOptions? options;

  RecommendedCar({
    this.carId,
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
    this.detailUrl,
    this.imageUrl,
    this.source = 'recommendation',
    this.options,
  });

  factory RecommendedCar.fromJson(Map<String, dynamic> json) {
    return RecommendedCar(
      carId: json['car_id']?.toString() ?? json['carId']?.toString(),
      brand: json['brand'] ?? '',
      model: json['model'] ?? '',
      year: json['year'] ?? 0,
      mileage: json['mileage'] ?? 0,
      fuel: json['fuel'] ?? '가솔린',
      actualPrice: json['actual_price'] ?? json['actualPrice'] ?? 0,
      predictedPrice: json['predicted_price'] ?? json['predictedPrice'] ?? 0,
      priceDiff: json['price_diff'] ?? json['priceDiff'] ?? 0,
      isGoodDeal: json['is_good_deal'] ?? json['isGoodDeal'] ?? false,
      score: (json['score'] ?? json['value_score'] ?? 0).toDouble(),
      type: json['type'] ?? 'domestic',
      detailUrl: json['detail_url'] ?? json['detailUrl'] ?? json['url'],
      imageUrl: json['image_url'] ?? json['imageUrl'],
      source: json['source'] ?? 'recommendation',
      options: json['options'] != null ? CarOptions.fromJson(json['options']) : null,
    );
  }
  
  String get formattedMileage => '${(mileage / 10000).toStringAsFixed(1)}만 km';
  String get priceTag => isGoodDeal ? '🔥 가성비' : '';
  
  /// source 및 options 변경을 위한 copyWith
  RecommendedCar copyWith({String? source, CarOptions? options}) {
    return RecommendedCar(
      carId: carId,
      brand: brand,
      model: model,
      year: year,
      mileage: mileage,
      fuel: fuel,
      actualPrice: actualPrice,
      predictedPrice: predictedPrice,
      priceDiff: priceDiff,
      isGoodDeal: isGoodDeal,
      score: score,
      type: type,
      detailUrl: detailUrl,
      imageUrl: imageUrl,
      source: source ?? this.source,
      options: options ?? this.options,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'car_id': carId,
      'brand': brand,
      'model': model,
      'year': year,
      'mileage': mileage,
      'fuel': fuel,
      'actual_price': actualPrice,
      'predicted_price': predictedPrice,
      'price_diff': priceDiff,
      'is_good_deal': isGoodDeal,
      'score': score,
      'type': type,
      'detail_url': detailUrl,
      'image_url': imageUrl,
      'source': source,
      'options': options?.toJson(),
    };
  }
}

/// 인기 차량 정보
class PopularCar {
  final String brand;
  final String model;
  final int listings;
  final int avgPrice;
  final int medianPrice;
  final String? type;

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
  
  Map<String, dynamic> toJson() {
    return {
      'brand': brand,
      'model': model,
      'listings': listings,
      'avg_price': avgPrice,
      'median_price': medianPrice,
      'type': type,
    };
  }
}
