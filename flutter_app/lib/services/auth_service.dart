import 'dart:convert';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

/// 인증 서비스 - 로그인/로그아웃 및 소셜 로그인 관리
/// 토큰 영속성 지원 (SharedPreferences)
class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  /// 로컬 호스트 주소 (플랫폼별)
  /// - Android 에뮬레이터: 10.0.2.2 (호스트 PC 접근용)
  /// - iOS 시뮬레이터/Web/Desktop: localhost
  static String get _localHost {
    if (kIsWeb) return 'localhost';
    try {
      if (Platform.isAndroid) {
        return '10.0.2.2';  // Android 에뮬레이터 → 호스트 PC
      }
    } catch (_) {}
    return 'localhost';
  }

  // 백엔드 URL (Spring Boot)
  static String get _baseUrl {
    return 'http://$_localHost:8080/api';
  }

  // SharedPreferences 키
  static const String _tokenKey = 'auth_token';
  static const String _emailKey = 'auth_email';
  static const String _providerKey = 'auth_provider';
  static const String _userIdKey = 'auth_user_id';

  // 현재 로그인 상태
  String? _token;
  String? _userEmail;
  String? _provider;
  String? _userId;

  bool get isLoggedIn => _token != null;
  String? get userEmail => _userEmail;
  String? get provider => _provider;
  String? get token => _token;
  String? get userId => _userId;

  /// 앱 시작 시 저장된 토큰 로드
  Future<void> loadSavedToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _token = prefs.getString(_tokenKey);
      _userEmail = prefs.getString(_emailKey);
      _provider = prefs.getString(_providerKey);
      _userId = prefs.getString(_userIdKey);
      
      if (_token != null) {
        debugPrint('🔑 저장된 토큰 로드 완료: $_userEmail');
      }
    } catch (e) {
      debugPrint('토큰 로드 에러: $e');
    }
  }

  /// 토큰 저장
  Future<void> _saveToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      if (_token != null) {
        await prefs.setString(_tokenKey, _token!);
      }
      if (_userEmail != null) {
        await prefs.setString(_emailKey, _userEmail!);
      }
      if (_provider != null) {
        await prefs.setString(_providerKey, _provider!);
      }
      if (_userId != null) {
        await prefs.setString(_userIdKey, _userId!);
      }
    } catch (e) {
      debugPrint('토큰 저장 에러: $e');
    }
  }

  /// 토큰 삭제
  Future<void> _clearToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_tokenKey);
      await prefs.remove(_emailKey);
      await prefs.remove(_providerKey);
      await prefs.remove(_userIdKey);
    } catch (e) {
      debugPrint('토큰 삭제 에러: $e');
    }
  }

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
        _userId = data['user']?['id']?.toString();
        await _saveToken();  // 토큰 저장
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
          'phoneNumber': null,  // 선택적 필드
        }),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['success'] == true) {
        return {'success': true, 'message': '회원가입 성공'};
      }
      
      return {'success': false, 'message': data['message'] ?? '회원가입 실패'};
    } catch (e) {
      debugPrint('회원가입 에러: $e');
      return {'success': false, 'message': '서버 연결 실패: $e'};
    }
  }

  /// OAuth 회원가입 (이메일 인증 불필요)
  Future<Map<String, dynamic>> oauthSignup(
    String email,
    String name,
    String provider,
    String providerId,
    String? profileImageUrl,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/oauth/signup'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'username': name,
          'provider': provider.toUpperCase(),
          'providerId': providerId,
          'profileImageUrl': profileImageUrl,
          'phoneNumber': null,  // 선택적 필드
        }),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      
      if (response.statusCode == 200 && data['success'] == true) {
        // OAuth 회원가입 성공 시 JWT 토큰 생성하여 반환
        // 백엔드에서 토큰을 생성하여 반환하도록 수정 필요
        return {
          'success': true,
          'message': '회원가입 성공',
          'token': data['token'],  // 백엔드에서 토큰 반환 시
        };
      }
      
      return {'success': false, 'message': data['message'] ?? '회원가입 실패'};
    } catch (e) {
      debugPrint('OAuth 회원가입 에러: $e');
      return {'success': false, 'message': '서버 연결 실패: $e'};
    }
  }

  /// 소셜 로그인 URL 생성
  String getSocialLoginUrl(String provider) {
    // 플랫폼별 호스트 주소 사용
    final host = _localHost;

    // Spring Boot OAuth2는 기본 리디렉션 URI를 사용하므로
    // redirect_uri 파라미터를 전달하지 않음
    // 기본 경로: {baseUrl}/login/oauth2/code/{registrationId}
    final baseUrl = 'http://$host:8080/oauth2/authorization/${provider.toLowerCase()}';
    
    return baseUrl;
  }

  /// 소셜 로그인 콜백 처리 (토큰 저장)
  Future<void> handleOAuthCallback(String token, String email, String providerName) async {
    _token = token;
    _userEmail = email;
    _provider = providerName;
    await _saveToken();  // 토큰 저장
    debugPrint('소셜 로그인 성공: $email ($providerName)');
  }

  /// 로그아웃
  Future<void> logout() async {
    _token = null;
    _userEmail = null;
    _provider = null;
    _userId = null;
    await _clearToken();  // 저장된 토큰 삭제
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

  /// 비밀번호 찾기 - 이메일 인증 코드 발송
  Future<Map<String, dynamic>> forgotPassword(String email) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/password/forgot'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email}),
      ).timeout(const Duration(seconds: 30));

      final data = jsonDecode(response.body);
      return {
        'success': data['success'] ?? false,
        'message': data['message'] ?? '인증 코드 발송 실패',
      };
    } catch (e) {
      debugPrint('비밀번호 찾기 에러: $e');
      return {'success': false, 'message': '서버 연결 실패'};
    }
  }

  /// 비밀번호 재설정
  Future<Map<String, dynamic>> resetPassword(
    String email,
    String code,
    String newPassword,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/password/reset'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'code': code,
          'newPassword': newPassword,
        }),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      return {
        'success': data['success'] ?? false,
        'message': data['message'] ?? '비밀번호 재설정 실패',
      };
    } catch (e) {
      debugPrint('비밀번호 재설정 에러: $e');
      return {'success': false, 'message': '서버 연결 실패'};
    }
  }
}
