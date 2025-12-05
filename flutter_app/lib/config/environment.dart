import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';

/// 환경 설정 관리
/// --dart-define으로 빌드 시 환경 주입 가능
///
/// 예시:
/// flutter run --dart-define=ENV=production
/// flutter build apk --dart-define=ENV=production --dart-define=ML_URL=https://api.car-sentix.com

class Environment {
  static const String env =
      String.fromEnvironment('ENV', defaultValue: 'development');

  /// 로컬 호스트 주소 (플랫폼별)
  /// - Android 에뮬레이터: 10.0.2.2 (호스트 PC 접근용)
  /// - iOS 시뮬레이터/Web/Desktop: localhost
  static String get _localHost {
    try {
      if (Platform.isAndroid) {
        return '10.0.2.2'; // Android 에뮬레이터 → 호스트 PC
      }
    } catch (_) {
      // Web에서는 Platform 체크 불가, localhost 사용
    }
    return 'localhost';
  }

  /// ML Service URL
  static String get mlServiceUrl {
    const customUrl = String.fromEnvironment('ML_URL', defaultValue: '');
    if (customUrl.isNotEmpty) return customUrl;

    switch (env) {
      case 'production':
        return 'https://api.car-sentix.com';
      case 'staging':
        return 'https://staging-api.car-sentix.com';
      default:
        return 'http://$_localHost:8000';
    }
  }

  /// User Service URL
  static String get userServiceUrl {
    const customUrl = String.fromEnvironment('USER_URL', defaultValue: '');
    if (customUrl.isNotEmpty) return customUrl;

    switch (env) {
      case 'production':
        return 'https://auth.car-sentix.com';
      case 'staging':
        return 'https://staging-auth.car-sentix.com';
      default:
        return 'http://$_localHost:8080';
    }
  }

  /// 이미지 서비스 URL
  static String get imageServiceUrl => '$mlServiceUrl/car-images';

  /// 디버그 모드 여부
  static bool get isDebug => env == 'development';

  /// API 타임아웃 (초)
  static Duration get apiTimeout {
    switch (env) {
      case 'production':
        return const Duration(seconds: 30);
      default:
        return const Duration(seconds: 60);
    }
  }

  /// 환경 정보 출력
  static void printInfo() {
    if (isDebug) {
      debugPrint('=== Environment ===');
      debugPrint('ENV: $env');
      debugPrint('ML Service: $mlServiceUrl');
      debugPrint('User Service: $userServiceUrl');
      debugPrint('==================');
    }
  }
}
