/// 모델 클래스 통합 export
/// 
/// 사용법:
/// ```dart
/// import 'package:flutter_app/models/index.dart';
/// ```
/// 
/// 또는 개별 import:
/// ```dart
/// import 'package:flutter_app/models/car.dart';
/// import 'package:flutter_app/models/prediction.dart';
/// ```
library;

// 차량 관련 모델
export 'car.dart';

// 가격 예측 관련 모델
export 'prediction.dart';

// 매물 분석 관련 모델
export 'deal.dart';

// 사용자 관련 모델
export 'user.dart';

// AI 관련 모델
export 'ai.dart';

// 기존 car_data.dart 호환
export 'car_data.dart';
