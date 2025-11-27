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

  static Color _getRandomColor() {
    final colors = [
      const Color(0xFF0066FF),
      const Color(0xFF00C853),
      const Color(0xFFFF6D00),
      const Color(0xFFAA00FF),
      const Color(0xFFFF1744),
    ];
    return colors[DateTime.now().millisecond % colors.length];
  }

  /// 가격을 숫자로 변환 (비교용)
  double get priceValue {
    return double.tryParse(price.replaceAll(RegExp(r'[^0-9.]'), '')) ?? 0;
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is CarData && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}
