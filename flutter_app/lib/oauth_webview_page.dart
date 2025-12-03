import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'services/auth_service.dart';

/// OAuth 소셜 로그인용 WebView 페이지
class OAuthWebViewPage extends StatefulWidget {
  final String provider; // naver, kakao, google

  const OAuthWebViewPage({super.key, required this.provider});

  @override
  State<OAuthWebViewPage> createState() => _OAuthWebViewPageState();
}

class _OAuthWebViewPageState extends State<OAuthWebViewPage> {
  late final WebViewController _controller;
  bool _isLoading = true;
  final AuthService _authService = AuthService();

  @override
  void initState() {
    super.initState();
    _initWebView();
  }

  void _initWebView() {
    final url = _authService.getSocialLoginUrl(widget.provider);
    debugPrint('🔑 OAuth URL: $url');

    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageStarted: (String url) {
            debugPrint('📍 페이지 시작: $url');
            setState(() => _isLoading = true);
          },
          onPageFinished: (String url) {
            debugPrint('✅ 페이지 완료: $url');
            setState(() => _isLoading = false);
          },
          onNavigationRequest: (NavigationRequest request) async {
            debugPrint('🔄 네비게이션: ${request.url}');

            // OAuth 콜백 처리 (성공 시 JWT 토큰이 URL에 포함됨)
            final handled = await _handleOAuthCallback(request.url);
            if (handled) {
              return NavigationDecision.prevent;
            }

            return NavigationDecision.navigate;
          },
          onWebResourceError: (WebResourceError error) {
            debugPrint('❌ 웹 오류: ${error.description}');

            // 10.0.2.2 연결 실패 시 에러 처리
            if (error.description.contains('net::ERR')) {
              _showError('서버에 연결할 수 없습니다.\n백엔드 서버가 실행 중인지 확인하세요.');
            }
          },
        ),
      )
      ..loadRequest(Uri.parse(url));
  }

  /// OAuth 콜백 URL 처리
  Future<bool> _handleOAuthCallback(String url) async {
    final uri = Uri.parse(url);

    // 1. 기존 사용자 로그인 성공: /oauth2/redirect?token=...
    if (url.contains('/oauth2/redirect')) {
      final token = uri.queryParameters['token'];
      final email = uri.queryParameters['email'];
      final error = uri.queryParameters['error'];
      final provider = uri.queryParameters['provider'];

      if (error != null) {
        _showError('로그인 실패: $error');
        Navigator.pop(context, {'success': false, 'error': error});
        return true;
      }

      if (token != null) {
        await _authService.handleOAuthCallback(
            token, email ?? '', provider ?? widget.provider);
        if (!mounted) return true;
        Navigator.pop(context, {
          'success': true,
          'token': token,
          'email': email,
          'provider': provider ?? widget.provider,
          'isExistingUser': true, // 기존 사용자 표시
        });
        return true;
      }
    }

    // 2. 신규 사용자 회원가입 필요: /signup?oauth=true&...
    if (url.contains('/signup') && url.contains('oauth=true')) {
      final email = uri.queryParameters['email'];
      final provider = uri.queryParameters['provider'];
      final providerId = uri.queryParameters['providerId'];
      final imageUrl = uri.queryParameters['imageUrl'];

      debugPrint('📝 신규 OAuth 사용자 - 회원가입 필요: $email ($provider)');

      Navigator.pop(context, {
        'success': false, // 로그인은 아직 완료되지 않음
        'needsSignup': true, // 회원가입 필요 플래그
        'email': email,
        'provider': provider ?? widget.provider,
        'providerId': providerId,
        'imageUrl': imageUrl,
      });
      return true;
    }

    // 3. 에러 콜백
    if (url.contains('error=')) {
      final error = uri.queryParameters['error_description'] ??
          uri.queryParameters['error'] ??
          '로그인 실패';
      _showError(error);
      Navigator.pop(context, {'success': false, 'error': error});
      return true;
    }

    return false;
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  String _getProviderName() {
    switch (widget.provider.toLowerCase()) {
      case 'naver':
        return '네이버';
      case 'kakao':
        return '카카오';
      case 'google':
        return 'Google';
      default:
        return widget.provider;
    }
  }

  Color _getProviderColor() {
    switch (widget.provider.toLowerCase()) {
      case 'naver':
        return const Color(0xFF03C75A);
      case 'kakao':
        return const Color(0xFFFEE500);
      case 'google':
        return Colors.white;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: _getProviderColor(),
        leading: IconButton(
          icon: Icon(
            Icons.close,
            color: widget.provider == 'kakao'
                ? Colors.black
                : widget.provider == 'google'
                    ? Colors.black
                    : Colors.white,
          ),
          onPressed: () => Navigator.pop(context, {'success': false}),
        ),
        title: Text(
          '${_getProviderName()} 로그인',
          style: TextStyle(
            color: widget.provider == 'kakao'
                ? Colors.black
                : widget.provider == 'google'
                    ? Colors.black
                    : Colors.white,
          ),
        ),
        elevation: 0,
      ),
      body: Stack(
        children: [
          WebViewWidget(controller: _controller),
          if (_isLoading)
            const Center(
              child: CircularProgressIndicator(),
            ),
        ],
      ),
    );
  }
}
