import 'package:flutter/material.dart';

/// 차량 비교용 데이터 모델
class CarData {
  final String id;
  final String name;
  final String price;
  final String info;
  final String date;
  final Color color;
  final String? imageUrl;
  final String? detailUrl;  // 엔카/케이카 상세페이지 URL
  final Map<String, dynamic>? analysisResult;  // 분석 결과
  bool isLiked;
  bool isNotificationOn;

  CarData({
    required this.id,
    required this.name,
    required this.price,
    required this.info,
    required this.date,
    required this.color,
    this.imageUrl,
    this.detailUrl,
    this.analysisResult,
    this.isLiked = false,
    this.isNotificationOn = false,
  });

  /// API 응답에서 CarData 생성
  factory CarData.fromAnalysis(Map<String, dynamic> analysis, {Color? color}) {
    final prediction = analysis['prediction'] ?? {};
    final request = analysis['request'] ?? {};
    
    return CarData(
      id: analysis['id']?.toString() ?? DateTime.now().millisecondsSinceEpoch.toString(),
      name: '${request['brand'] ?? ''} ${request['model'] ?? ''}'.trim(),
      price: '${(prediction['predicted_price'] ?? 0).toStringAsFixed(0)}만원',
      info: '${request['year'] ?? ''}년식 / ${_formatMileage(request['mileage'])}',
      date: _formatDate(analysis['created_at'] ?? DateTime.now().toIso8601String()),
      color: color ?? _getRandomColor(),
      detailUrl: request['detail_url'],
      analysisResult: analysis,
      isLiked: analysis['is_favorite'] ?? false,
    );
  }

  /// 추천 매물에서 CarData 생성
  factory CarData.fromRecommendation(Map<String, dynamic> rec, {Color? color}) {
    return CarData(
      id: rec['id']?.toString() ?? DateTime.now().millisecondsSinceEpoch.toString(),
      name: '${rec['brand'] ?? ''} ${rec['model'] ?? ''}'.trim(),
      price: '${rec['price'] ?? 0}만원',
      info: '${rec['year'] ?? ''}년식 / ${_formatMileage(rec['mileage'])}',
      date: '',
      color: color ?? _getRandomColor(),
      imageUrl: rec['image_url'],
      detailUrl: rec['detail_url'] ?? rec['url'],
    );
  }

  /// 찜한 차량에서 CarData 생성
  factory CarData.fromFavorite(Map<String, dynamic> fav, {Color? color}) {
    return CarData(
      id: fav['id']?.toString() ?? '',
      name: '${fav['brand'] ?? ''} ${fav['model'] ?? ''}'.trim(),
      price: '${fav['predicted_price'] ?? 0}만원',
      info: '${fav['year'] ?? ''}년식 / ${_formatMileage(fav['mileage'])}',
      date: _formatDate(fav['created_at'] ?? ''),
      color: color ?? _getRandomColor(),
      detailUrl: fav['detail_url'],
      isLiked: true,
    );
  }

  static String _formatMileage(dynamic mileage) {
    if (mileage == null) return '0km';
    final km = mileage is int ? mileage : int.tryParse(mileage.toString()) ?? 0;
    if (km >= 10000) {
      return '${(km / 10000).toStringAsFixed(1)}만km';
    }
    return '${km}km';
  }

  static String _formatDate(String isoDate) {
    try {
      final date = DateTime.parse(isoDate);
      return '${date.year}.${date.month.toString().padLeft(2, '0')}.${date.day.toString().padLeft(2, '0')}';
    } catch (_) {
      return '';
    }
  }

  /// 인덱스 기반 색상 (비교 차트에서 고유 색상 보장)
  static Color getColorByIndex(int index) {
    const colors = [
      Color(0xFF0066FF),  // 파랑
      Color(0xFF00C853),  // 초록
      Color(0xFFFF6D00),  // 주황
      Color(0xFFAA00FF),  // 보라
      Color(0xFFFF1744),  // 빨강
      Color(0xFF00BCD4),  // 청록
      Color(0xFFFFEB3B),  // 노랑
      Color(0xFFE91E63),  // 분홍
    ];
    return colors[index % colors.length];
  }

  static Color _getRandomColor() {
    // ID 기반 해시를 사용하여 일관된 색상 할당
    final colors = [
      const Color(0xFF0066FF),
      const Color(0xFF00C853),
      const Color(0xFFFF6D00),
      const Color(0xFFAA00FF),
      const Color(0xFFFF1744),
    ];
    return colors[DateTime.now().microsecondsSinceEpoch % colors.length];
  }

  /// 가격을 숫자로 변환 (비교용)
  double get priceValue {
    return double.tryParse(price.replaceAll(RegExp(r'[^0-9.]'), '')) ?? 0;
  }

  /// JSON에서 CarData 생성 (로컬 캐시용)
  factory CarData.fromJson(Map<String, dynamic> json) {
    return CarData(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      price: json['price'] ?? '0만원',
      info: json['info'] ?? '',
      date: json['date'] ?? '',
      color: Color(json['color'] ?? 0xFF0066FF),
      imageUrl: json['imageUrl'],
      detailUrl: json['detailUrl'],
      isLiked: json['isLiked'] ?? false,
      isNotificationOn: json['isNotificationOn'] ?? false,
    );
  }

  /// CarData를 JSON으로 변환 (로컬 캐시용)
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'price': price,
      'info': info,
      'date': date,
      'color': color.value,
      'imageUrl': imageUrl,
      'detailUrl': detailUrl,
      'isLiked': isLiked,
      'isNotificationOn': isNotificationOn,
    };
  }

  /// CarData 복사 (수정용)
  CarData copyWith({
    String? id,
    String? name,
    String? price,
    String? info,
    String? date,
    Color? color,
    String? imageUrl,
    String? detailUrl,
    Map<String, dynamic>? analysisResult,
    bool? isLiked,
    bool? isNotificationOn,
  }) {
    return CarData(
      id: id ?? this.id,
      name: name ?? this.name,
      price: price ?? this.price,
      info: info ?? this.info,
      date: date ?? this.date,
      color: color ?? this.color,
      imageUrl: imageUrl ?? this.imageUrl,
      detailUrl: detailUrl ?? this.detailUrl,
      analysisResult: analysisResult ?? this.analysisResult,
      isLiked: isLiked ?? this.isLiked,
      isNotificationOn: isNotificationOn ?? this.isNotificationOn,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is CarData && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}
