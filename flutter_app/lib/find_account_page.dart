import 'package:flutter/material.dart';
import 'services/auth_service.dart';

/// 아이디/비밀번호 찾기 페이지
class FindAccountPage extends StatefulWidget {
  const FindAccountPage({super.key});

  @override
  State<FindAccountPage> createState() => _FindAccountPageState();
}

class _FindAccountPageState extends State<FindAccountPage> {
  final AuthService _authService = AuthService();
  final PageController _pageController = PageController();

  // 비밀번호 찾기
  final TextEditingController _emailController = TextEditingController();
  bool _isLoadingEmail = false;

  // 비밀번호 재설정
  final TextEditingController _codeController = TextEditingController();
  final TextEditingController _newPasswordController = TextEditingController();
  final TextEditingController _confirmPasswordController = TextEditingController();
  bool _isLoadingReset = false;
  bool _obscureNewPassword = true;
  bool _obscureConfirmPassword = true;

  @override
  void dispose() {
    _pageController.dispose();
    _emailController.dispose();
    _codeController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  /// 이메일 인증 코드 발송
  Future<void> _sendVerificationCode() async {
    if (_emailController.text.isEmpty) {
      _showMessage('이메일을 입력해주세요', isError: true);
      return;
    }

    if (!_isValidEmail(_emailController.text)) {
      _showMessage('올바른 이메일 형식이 아닙니다', isError: true);
      return;
    }

    setState(() => _isLoadingEmail = true);

    final result = await _authService.forgotPassword(_emailController.text.trim());

    setState(() => _isLoadingEmail = false);

    if (result['success'] == true) {
      _showMessage('인증 코드가 발송되었습니다\n이메일을 확인해주세요');
      // 다음 페이지로 이동
      Future.delayed(const Duration(milliseconds: 500), () {
        _pageController.nextPage(
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeInOut,
        );
      });
    } else {
      _showMessage(result['message'] ?? '인증 코드 발송 실패', isError: true);
    }
  }

  /// 비밀번호 재설정
  Future<void> _resetPassword() async {
    if (_codeController.text.isEmpty) {
      _showMessage('인증 코드를 입력해주세요', isError: true);
      return;
    }

    if (_newPasswordController.text.isEmpty) {
      _showMessage('새 비밀번호를 입력해주세요', isError: true);
      return;
    }

    if (_newPasswordController.text.length < 8) {
      _showMessage('비밀번호는 8자 이상이어야 합니다', isError: true);
      return;
    }

    if (_newPasswordController.text != _confirmPasswordController.text) {
      _showMessage('비밀번호가 일치하지 않습니다', isError: true);
      return;
    }

    setState(() => _isLoadingReset = true);

    final result = await _authService.resetPassword(
      _emailController.text.trim(),
      _codeController.text.trim(),
      _newPasswordController.text,
    );

    setState(() => _isLoadingReset = false);

    if (result['success'] == true) {
      _showMessage('비밀번호가 재설정되었습니다');
      // 로그인 페이지로 돌아가기
      Future.delayed(const Duration(seconds: 1), () {
        if (mounted) {
          Navigator.pop(context, true);
        }
      });
    } else {
      _showMessage(result['message'] ?? '비밀번호 재설정 실패', isError: true);
    }
  }

  bool _isValidEmail(String email) {
    return RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(email);
  }

  void _showMessage(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red : Colors.green,
        duration: const Duration(seconds: 3),
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
          '비밀번호 찾기',
          style: TextStyle(
            color: textColor,
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: PageView(
          controller: _pageController,
          physics: const NeverScrollableScrollPhysics(), // 스와이프 비활성화
          children: [
            // 1단계: 이메일 입력 및 인증 코드 발송
            _buildEmailStep(isDark, textColor),
            // 2단계: 인증 코드 확인 및 비밀번호 재설정
            _buildResetStep(isDark, textColor),
          ],
        ),
      ),
    );
  }

  /// 1단계: 이메일 입력
  Widget _buildEmailStep(bool isDark, Color textColor) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 20),
          Row(
            children: [
              const Text(
                '🔐',
                style: TextStyle(fontSize: 28),
              ),
              const SizedBox(width: 8),
              Text(
                '비밀번호 찾기',
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
            '가입하신 이메일로 인증 코드를 발송해드립니다.',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey[500],
            ),
          ),
          const SizedBox(height: 40),

          // 이메일 입력
          _buildTextField(
            controller: _emailController,
            hintText: "이메일",
            keyboardType: TextInputType.emailAddress,
            isDark: isDark,
          ),
          const SizedBox(height: 24),

          // 인증 코드 발송 버튼
          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton(
              onPressed: _isLoadingEmail ? null : _sendVerificationCode,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0066FF),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                elevation: 0,
              ),
              child: _isLoadingEmail
                  ? const SizedBox(
                      width: 24,
                      height: 24,
                      child: CircularProgressIndicator(
                        color: Colors.white,
                        strokeWidth: 2,
                      ),
                    )
                  : const Text(
                      "인증 코드 발송",
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
            ),
          ),
          const SizedBox(height: 20),

          // 안내 문구
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF2C2C2C) : Colors.grey[100],
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.info_outline, size: 20, color: Colors.blue[300]),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    '소셜 로그인 계정은 비밀번호 찾기가 불가능합니다.\n이메일로 가입한 계정만 비밀번호를 재설정할 수 있습니다.',
                    style: TextStyle(
                      fontSize: 13,
                      color: Colors.grey[600],
                      height: 1.4,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// 2단계: 인증 코드 확인 및 비밀번호 재설정
  Widget _buildResetStep(bool isDark, Color textColor) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 20),
          Row(
            children: [
              const Text(
                '✏️',
                style: TextStyle(fontSize: 28),
              ),
              const SizedBox(width: 8),
              Text(
                '비밀번호 재설정',
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
            '${_emailController.text}로 발송된 인증 코드를 입력하고\n새 비밀번호를 설정해주세요.',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey[500],
            ),
          ),
          const SizedBox(height: 40),

          // 인증 코드 입력
          _buildTextField(
            controller: _codeController,
            hintText: "인증 코드",
            keyboardType: TextInputType.number,
            isDark: isDark,
          ),
          const SizedBox(height: 12),

          // 새 비밀번호 입력
          _buildTextField(
            controller: _newPasswordController,
            hintText: "새 비밀번호 (8자 이상)",
            obscureText: _obscureNewPassword,
            isDark: isDark,
            suffixIcon: IconButton(
              icon: Icon(
                _obscureNewPassword ? Icons.visibility : Icons.visibility_off,
                color: Colors.grey[400],
              ),
              onPressed: () {
                setState(() => _obscureNewPassword = !_obscureNewPassword);
              },
            ),
          ),
          const SizedBox(height: 12),

          // 비밀번호 확인 입력
          _buildTextField(
            controller: _confirmPasswordController,
            hintText: "비밀번호 확인",
            obscureText: _obscureConfirmPassword,
            isDark: isDark,
            suffixIcon: IconButton(
              icon: Icon(
                _obscureConfirmPassword ? Icons.visibility : Icons.visibility_off,
                color: Colors.grey[400],
              ),
              onPressed: () {
                setState(() => _obscureConfirmPassword = !_obscureConfirmPassword);
              },
            ),
          ),
          const SizedBox(height: 24),

          // 비밀번호 재설정 버튼
          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton(
              onPressed: _isLoadingReset ? null : _resetPassword,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0066FF),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                elevation: 0,
              ),
              child: _isLoadingReset
                  ? const SizedBox(
                      width: 24,
                      height: 24,
                      child: CircularProgressIndicator(
                        color: Colors.white,
                        strokeWidth: 2,
                      ),
                    )
                  : const Text(
                      "비밀번호 재설정",
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
            ),
          ),
          const SizedBox(height: 20),

          // 다시 발송 버튼
          Center(
            child: TextButton(
              onPressed: _isLoadingEmail ? null : _sendVerificationCode,
              child: Text(
                '인증 코드를 받지 못하셨나요? 다시 발송',
                style: TextStyle(
                  color: Colors.blue[600],
                  fontSize: 14,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // Helper Widget: 텍스트 필드
  Widget _buildTextField({
    required String hintText,
    bool obscureText = false,
    required bool isDark,
    TextEditingController? controller,
    TextInputType? keyboardType,
    Widget? suffixIcon,
  }) {
    return Container(
      height: 52,
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF2C2C2C) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isDark ? Colors.grey[700]! : const Color(0xFFE5E7EB),
        ),
      ),
      child: TextField(
        controller: controller,
        obscureText: obscureText,
        keyboardType: keyboardType,
        style: TextStyle(color: isDark ? Colors.white : Colors.black),
        decoration: InputDecoration(
          hintText: hintText,
          hintStyle: TextStyle(color: Colors.grey[400], fontSize: 15),
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(horizontal: 16),
          suffixIcon: suffixIcon,
        ),
      ),
    );
  }
}

