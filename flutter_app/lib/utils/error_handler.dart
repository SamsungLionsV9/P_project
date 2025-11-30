import 'dart:io';
import 'package:flutter/material.dart';

/// API 예외 클래스
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final String? errorCode;
  
  ApiException(this.message, {this.statusCode, this.errorCode});
  
  @override
  String toString() => message;
  
  /// 사용자 친화적 메시지 변환
  String get userMessage {
    switch (statusCode) {
      case 400:
        return '잘못된 요청입니다. 입력값을 확인해주세요.';
      case 401:
        return '로그인이 필요합니다.';
      case 403:
        return '접근 권한이 없습니다.';
      case 404:
        return '요청하신 정보를 찾을 수 없습니다.';
      case 500:
        return '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
      case 503:
        return '서비스 점검 중입니다. 잠시 후 다시 시도해주세요.';
      default:
        return message;
    }
  }
}

/// 네트워크 예외 클래스
class NetworkException implements Exception {
  final String message;
  
  NetworkException([this.message = '네트워크 연결을 확인해주세요.']);
  
  @override
  String toString() => message;
}

/// 에러 핸들러 유틸리티
class ErrorHandler {
  /// Exception을 사용자 메시지로 변환
  static String getMessage(dynamic error) {
    if (error is ApiException) {
      return error.userMessage;
    } else if (error is NetworkException) {
      return error.message;
    } else if (error is SocketException) {
      return '서버에 연결할 수 없습니다. 네트워크를 확인해주세요.';
    } else if (error is FormatException) {
      return '데이터 형식 오류가 발생했습니다.';
    } else {
      return '알 수 없는 오류가 발생했습니다.';
    }
  }
  
  /// 스낵바로 에러 표시
  static void showError(BuildContext context, dynamic error) {
    final message = getMessage(error);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red.shade700,
        behavior: SnackBarBehavior.floating,
        action: SnackBarAction(
          label: '확인',
          textColor: Colors.white,
          onPressed: () {},
        ),
      ),
    );
  }
  
  /// 다이얼로그로 에러 표시
  static Future<void> showErrorDialog(
    BuildContext context,
    dynamic error, {
    String? title,
    VoidCallback? onRetry,
  }) async {
    final message = getMessage(error);
    await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title ?? '오류'),
        content: Text(message),
        actions: [
          if (onRetry != null)
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                onRetry();
              },
              child: const Text('다시 시도'),
            ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('확인'),
          ),
        ],
      ),
    );
  }
}
