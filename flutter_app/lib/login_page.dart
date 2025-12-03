import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'services/auth_service.dart';
import 'signup_page.dart';
import 'oauth_webview_page.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final AuthService _authService = AuthService();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  bool _isLoading = false;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  /// 이메일/비밀번호 로그인
  Future<void> _login() async {
    if (_emailController.text.isEmpty || _passwordController.text.isEmpty) {
      _showMessage('이메일과 비밀번호를 입력하세요', isError: true);
      return;
    }

    setState(() => _isLoading = true);

    final result = await _authService.login(
      _emailController.text.trim(),
      _passwordController.text,
    );

    setState(() => _isLoading = false);

    if (result['success'] == true) {
      _showMessage('로그인 성공!');
      if (mounted) {
        Navigator.pop(context, true); // 로그인 성공 시 true 반환
      }
    } else {
      _showMessage(result['message'] ?? '로그인 실패', isError: true);
    }
  }

  /// 소셜 로그인
  Future<void> _socialLogin(String provider) async {
    // 네이버는 WebView를 차단하므로 외부 브라우저 사용
    if (provider == 'naver') {
      final url = _authService.getSocialLoginUrl(provider);
      _showMessage('네이버 로그인은 외부 브라우저에서 진행됩니다.\n(에뮬레이터에서는 제한될 수 있습니다)');

      try {
        final uri = Uri.parse(url);
        if (await canLaunchUrl(uri)) {
          await launchUrl(uri, mode: LaunchMode.externalApplication);
        } else {
          _showMessage('브라우저를 열 수 없습니다', isError: true);
        }
      } catch (e) {
        _showMessage('네이버 로그인 오류: $e', isError: true);
      }
      return;
    }

    // 카카오, 구글은 WebView 사용
    final result = await Navigator.push<Map<String, dynamic>>(
      context,
      MaterialPageRoute(
        builder: (context) => OAuthWebViewPage(provider: provider),
      ),
    );

    if (result != null && result['success'] == true) {
      _showMessage('${_getProviderName(provider)} 로그인 성공!');
      if (mounted) {
        Navigator.pop(context, true);
      }
    }
  }

  String _getProviderName(String provider) {
    switch (provider) {
      case 'naver':
        return '네이버';
      case 'kakao':
        return '카카오';
      case 'google':
        return 'Google';
      default:
        return provider;
    }
  }

  /// 회원가입 페이지로 이동
  void _navigateToSignup() async {
    final result = await Navigator.push<bool>(
      context,
      MaterialPageRoute(builder: (context) => const SignupPage()),
    );

    if (result == true) {
      _showMessage('회원가입이 완료되었습니다. 로그인하세요!');
    }
  }

  void _showMessage(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red : Colors.green,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor = isDark ? const Color(0xFF121212) : Colors.white;
    final textColor = isDark ? Colors.white : Colors.black87;

    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        backgroundColor: bgColor,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios_new, color: textColor),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          '로그인',
          style: TextStyle(
            color: textColor,
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 20),
              Row(
                children: [
                  const Text(
                    '👋',
                    style: TextStyle(fontSize: 28),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '반가워요!',
                    style: TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      color: textColor,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                '가장 합리적인 거래를 도와드릴게요.',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey[500],
                ),
              ),
              const SizedBox(height: 40),

              // 이메일 입력
              _buildTextField(
                controller: _emailController,
                hintText: "이메일 또는 아이디",
                isDark: isDark,
              ),
              const SizedBox(height: 12),

              // 비밀번호 입력
              _buildTextField(
                controller: _passwordController,
                hintText: "비밀번호",
                obscureText: true,
                isDark: isDark,
              ),
              const SizedBox(height: 24),

              // 로그인 버튼
              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _login,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF0066FF),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    elevation: 0,
                  ),
                  child: _isLoading
                      ? const SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(
                              color: Colors.white, strokeWidth: 2),
                        )
                      : const Text(
                          "로그인",
                          style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Colors.white),
                        ),
                ),
              ),
              const SizedBox(height: 20),

              // 아이디/비밀번호 찾기 | 회원가입
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  TextButton(
                    onPressed: () {
                      // TODO: 아이디/비밀번호 찾기 구현
                      _showMessage('준비 중인 기능입니다.');
                    },
                    child: Text(
                      '아이디/비밀번호 찾기',
                      style: TextStyle(color: Colors.grey[500], fontSize: 13),
                    ),
                  ),
                  Container(
                    width: 1,
                    height: 12,
                    color: Colors.grey[300],
                    margin: const EdgeInsets.symmetric(horizontal: 12),
                  ),
                  TextButton(
                    onPressed: _navigateToSignup,
                    child: const Text(
                      '회원가입',
                      style: TextStyle(
                        color: Color(0xFF0066FF),
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                      ),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 60),

              // 소셜 로그인 구분선
              Row(
                children: [
                  Expanded(child: Divider(color: Colors.grey[300])),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: Text(
                      '또는 3초 만에 시작하기',
                      style: TextStyle(color: Colors.grey[500], fontSize: 13),
                    ),
                  ),
                  Expanded(child: Divider(color: Colors.grey[300])),
                ],
              ),
              const SizedBox(height: 24),

              // 소셜 로그인 버튼들
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _buildSocialButton("K", const Color(0xFFFEE500),
                      const Color(0xFF3C1E1E), 'kakao'),
                  const SizedBox(width: 20),
                  _buildSocialButton(
                      "N", const Color(0xFF03C75A), Colors.white, 'naver'),
                  const SizedBox(width: 20),
                  _buildSocialButton("G", Colors.white, Colors.grey, 'google',
                      isBorder: true),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Helper Widget: 텍스트 필드
  Widget _buildTextField({
    required String hintText,
    bool obscureText = false,
    required bool isDark,
    TextEditingController? controller,
  }) {
    return Container(
      height: 52,
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF2C2C2C) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
            color: isDark ? Colors.grey[700]! : const Color(0xFFE5E7EB)),
      ),
      child: TextField(
        controller: controller,
        obscureText: obscureText,
        style: TextStyle(color: isDark ? Colors.white : Colors.black),
        decoration: InputDecoration(
          hintText: hintText,
          hintStyle: TextStyle(color: Colors.grey[400], fontSize: 15),
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(horizontal: 16),
        ),
      ),
    );
  }

  // Helper Widget: 소셜 로그인 버튼
  Widget _buildSocialButton(
      String text, Color bgColor, Color textColor, String provider,
      {bool isBorder = false}) {
    return GestureDetector(
      onTap: () => _socialLogin(provider),
      child: Container(
        width: 52,
        height: 52,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: bgColor,
          border: isBorder ? Border.all(color: Colors.grey[300]!) : null,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Center(
          child: provider == 'google'
              ? Image.asset(
                  'assets/images/google_logo.png', // 구글 로고 이미지 필요 시
                  width: 24,
                  height: 24,
                  errorBuilder: (context, error, stackTrace) => Text(
                    text,
                    style: TextStyle(
                      color: textColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 20,
                    ),
                  ),
                )
              : Text(
                  text,
                  style: TextStyle(
                    color: textColor,
                    fontWeight: FontWeight.bold,
                    fontSize: 20,
                  ),
                ),
        ),
      ),
    );
  }
}
