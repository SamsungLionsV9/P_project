import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

/// 인증 서비스 - 로그인/로그아웃 및 소셜 로그인 관리
class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  // 백엔드 URL (Spring Boot)
  static String get _baseUrl {
    if (!kIsWeb && Platform.isAndroid) {
      return 'http://10.0.2.2:8080/api';
    }
    return 'http://localhost:8080/api';
  }

  // 현재 로그인 상태
  String? _token;
  String? _userEmail;
  String? _provider;

  bool get isLoggedIn => _token != null;
  String? get userEmail => _userEmail;
  String? get provider => _provider;
  String? get token => _token;

  /// 이메일/비밀번호 로그인
  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['success'] == true) {
        _token = data['token'];
        _userEmail = email;
        _provider = 'email';
        return {'success': true, 'message': '로그인 성공'};
      }
      
      return {'success': false, 'message': data['message'] ?? '로그인 실패'};
    } catch (e) {
      debugPrint('로그인 에러: $e');
      return {'success': false, 'message': '서버 연결 실패'};
    }
  }

  /// 이메일 인증 코드 발송
  Future<Map<String, dynamic>> sendVerificationCode(String email) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/email/send-code'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email}),
      ).timeout(const Duration(seconds: 30));

      final data = jsonDecode(response.body);
      return {
        'success': data['success'] ?? false,
        'message': data['message'] ?? '인증 코드 발송 실패',
      };
    } catch (e) {
      debugPrint('인증 코드 발송 에러: $e');
      return {'success': false, 'message': '서버 연결 실패'};
    }
  }

  /// 이메일 인증 코드 확인
  Future<Map<String, dynamic>> verifyCode(String email, String code) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/email/verify-code'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'code': code}),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      return {
        'success': data['success'] ?? false,
        'message': data['message'] ?? '인증 실패',
      };
    } catch (e) {
      debugPrint('인증 코드 확인 에러: $e');
      return {'success': false, 'message': '서버 연결 실패'};
    }
  }

  /// 회원가입 (이메일 인증 필수)
  Future<Map<String, dynamic>> signup(String email, String password, String name) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/signup'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
          'username': name,  // 백엔드는 username 필드를 기대
        }),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['success'] == true) {
        return {'success': true, 'message': '회원가입 성공'};
      }
      
      return {'success': false, 'message': data['message'] ?? '회원가입 실패'};
    } catch (e) {
      debugPrint('회원가입 에러: $e');
      return {'success': false, 'message': '서버 연결 실패'};
    }
  }

  /// 소셜 로그인 URL 생성
  String getSocialLoginUrl(String provider) {
    // Android 에뮬레이터에서는 10.0.2.2 사용
    final host = !kIsWeb && Platform.isAndroid ? '10.0.2.2' : 'localhost';
    
    switch (provider.toLowerCase()) {
      case 'naver':
        return 'http://$host:8080/oauth2/authorization/naver';
      case 'kakao':
        return 'http://$host:8080/oauth2/authorization/kakao';
      case 'google':
        return 'http://$host:8080/oauth2/authorization/google';
      default:
        throw ArgumentError('Unknown provider: $provider');
    }
  }

  /// 소셜 로그인 콜백 처리 (토큰 저장)
  void handleOAuthCallback(String token, String email, String providerName) {
    _token = token;
    _userEmail = email;
    _provider = providerName;
    debugPrint('소셜 로그인 성공: $email ($providerName)');
  }

  /// 로그아웃
  void logout() {
    _token = null;
    _userEmail = null;
    _provider = null;
    debugPrint('로그아웃 완료');
  }

  /// 현재 사용자 정보 조회
  Future<Map<String, dynamic>?> getCurrentUser() async {
    if (_token == null) return null;

    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/auth/me'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $_token',
        },
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return null;
    } catch (e) {
      debugPrint('사용자 정보 조회 에러: $e');
      return null;
    }
  }
}
