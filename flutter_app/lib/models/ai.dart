/// AI 관련 모델 클래스들
/// 
/// 분리된 위치: lib/models/ai.dart
/// 원본: lib/services/api_service.dart
library;

/// AI 생성 네고 대본 모델
class NegotiationScript {
  final String messageScript;      // 문자용 대본
  final List<String> phoneScript;  // 전화용 단계별 대본
  final String tip;                // 협상 팁
  final List<String> checkpoints;  // 체크포인트

  NegotiationScript({
    required this.messageScript,
    required this.phoneScript,
    required this.tip,
    required this.checkpoints,
  });

  factory NegotiationScript.fromJson(Map<String, dynamic> json) {
    return NegotiationScript(
      messageScript: json['message_script'] ?? '',
      phoneScript: List<String>.from(json['phone_script'] ?? []),
      tip: json['tip'] ?? '',
      checkpoints: List<String>.from(json['checkpoints'] ?? []),
    );
  }
}

/// AI 상태 모델
class AiStatus {
  final bool isConnected;
  final String? model;
  final String status;

  AiStatus({
    required this.isConnected,
    this.model,
    required this.status,
  });

  factory AiStatus.fromJson(Map<String, dynamic> json) {
    return AiStatus(
      isConnected: json['groq_available'] ?? false,
      model: json['model'],
      status: json['status'] ?? 'unknown',
    );
  }
}

/// API 예외 클래스
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final String? endpoint;

  ApiException(this.message, {this.statusCode, this.endpoint});

  @override
  String toString() => message;
}
