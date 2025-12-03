import 'package:flutter/material.dart';

/// 매물 분석 관련 모델 클래스들
/// 
/// 분리된 위치: lib/models/deal.dart
/// 원본: lib/services/api_service.dart

/// 개별 매물 분석 결과
class DealAnalysis {
  final String brand;
  final String model;
  final int year;
  final int mileage;
  final String fuel;
  final PriceFairness priceFairness;
  final FraudRisk fraudRisk;
  final List<String> negoPoints;
  final DealSummary summary;

  DealAnalysis({
    required this.brand,
    required this.model,
    required this.year,
    required this.mileage,
    required this.fuel,
    required this.priceFairness,
    required this.fraudRisk,
    required this.negoPoints,
    required this.summary,
  });

  factory DealAnalysis.fromJson(Map<String, dynamic> json) {
    return DealAnalysis(
      brand: json['brand'] ?? '',
      model: json['model'] ?? '',
      year: json['year'] ?? 0,
      mileage: json['mileage'] ?? 0,
      fuel: json['fuel'] ?? '가솔린',
      priceFairness: PriceFairness.fromJson(json['price_fairness'] ?? {}),
      fraudRisk: FraudRisk.fromJson(json['fraud_risk'] ?? {}),
      negoPoints: List<String>.from(json['nego_points'] ?? []),
      summary: DealSummary.fromJson(json['summary'] ?? {}),
    );
  }
}

/// 가격 적정성
class PriceFairness {
  final int score;
  final String label;
  final int percentile;
  final String description;

  PriceFairness({
    required this.score,
    required this.label,
    required this.percentile,
    required this.description,
  });

  factory PriceFairness.fromJson(Map<String, dynamic> json) {
    return PriceFairness(
      score: json['score'] ?? 50,
      label: json['label'] ?? '판단불가',
      percentile: json['percentile'] ?? 50,
      description: json['description'] ?? '',
    );
  }
}

/// 허위매물 위험도
class FraudRisk {
  final int score;
  final String level;  // low, medium, high
  final List<FraudFactor> factors;

  FraudRisk({
    required this.score,
    required this.level,
    required this.factors,
  });

  factory FraudRisk.fromJson(Map<String, dynamic> json) {
    return FraudRisk(
      score: json['score'] ?? 0,
      level: json['level'] ?? 'low',
      factors: (json['factors'] as List? ?? [])
          .map((e) => FraudFactor.fromJson(e))
          .toList(),
    );
  }
  
  Color get levelColor {
    switch (level) {
      case 'high': return const Color(0xFFE53935);
      case 'medium': return const Color(0xFFFFA726);
      default: return const Color(0xFF66BB6A);
    }
  }
  
  String get levelText {
    switch (level) {
      case 'high': return '높음';
      case 'medium': return '보통';
      default: return '낮음';
    }
  }
}

/// 허위매물 체크 요소
class FraudFactor {
  final String check;
  final String status;  // pass, warn, fail, info
  final String msg;

  FraudFactor({
    required this.check,
    required this.status,
    required this.msg,
  });

  factory FraudFactor.fromJson(Map<String, dynamic> json) {
    return FraudFactor(
      check: json['check'] ?? '',
      status: json['status'] ?? 'info',
      msg: json['msg'] ?? '',
    );
  }
  
  Color get statusColor {
    switch (status) {
      case 'pass': return const Color(0xFF66BB6A);
      case 'warn': return const Color(0xFFFFA726);
      case 'fail': return const Color(0xFFE53935);
      default: return Colors.grey;
    }
  }
  
  IconData get statusIcon {
    switch (status) {
      case 'pass': return Icons.check_circle;
      case 'warn': return Icons.warning;
      case 'fail': return Icons.cancel;
      default: return Icons.info;
    }
  }
}

/// 분석 요약
class DealSummary {
  final int actualPrice;
  final int predictedPrice;
  final int priceDiff;
  final double priceDiffPct;
  final bool isGoodDeal;
  final String verdict;

  DealSummary({
    required this.actualPrice,
    required this.predictedPrice,
    required this.priceDiff,
    required this.priceDiffPct,
    required this.isGoodDeal,
    required this.verdict,
  });

  factory DealSummary.fromJson(Map<String, dynamic> json) {
    return DealSummary(
      actualPrice: json['actual_price'] ?? 0,
      predictedPrice: json['predicted_price'] ?? 0,
      priceDiff: json['price_diff'] ?? 0,
      priceDiffPct: (json['price_diff_pct'] ?? 0).toDouble(),
      isGoodDeal: json['is_good_deal'] ?? false,
      verdict: json['verdict'] ?? '',
    );
  }
}
