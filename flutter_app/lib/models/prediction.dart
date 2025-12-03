/// 가격 예측 관련 모델 클래스들
/// 
/// 분리된 위치: lib/models/prediction.dart
/// 원본: lib/services/api_service.dart
library;

/// 가격 예측 결과
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

/// 구매 타이밍 분석 결과
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

/// 통합 분석 결과 (예측 + 타이밍 + AI)
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

/// 유사 차량 분포 결과
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
