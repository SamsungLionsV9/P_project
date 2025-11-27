import 'dart:async';
import 'package:flutter/material.dart';
import 'services/auth_service.dart';

/// 전문적인 회원가입 페이지 (이메일 인증 포함)
class SignupPage extends StatefulWidget {
  const SignupPage({super.key});

  @override
  State<SignupPage> createState() => _SignupPageState();
}

class _SignupPageState extends State<SignupPage> {
  final AuthService _authService = AuthService();
  final _formKey = GlobalKey<FormState>();
  
  // Controllers
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _verificationCodeController = TextEditingController();
  
  // State
  int _currentStep = 0;  // 0: 정보입력, 1: 이메일인증, 2: 완료
  bool _isLoading = false;
  bool _isEmailVerified = false;
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  int _resendCountdown = 0;
  Timer? _countdownTimer;

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _verificationCodeController.dispose();
    _countdownTimer?.cancel();
    super.dispose();
  }

  /// 이메일 형식 검증
  bool _isValidEmail(String email) {
    return RegExp(r'^[A-Za-z0-9+_.-]+@(.+)$').hasMatch(email);
  }

  /// 비밀번호 강도 검증 (백엔드 규칙과 일치)
  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return '비밀번호를 입력하세요';
    }
    if (value.length < 8) {
      return '8자 이상 입력하세요';
    }
    if (!RegExp(r'[A-Za-z]').hasMatch(value)) {
      return '영문을 포함해야 합니다';
    }
    if (!RegExp(r'[0-9]').hasMatch(value)) {
      return '숫자를 포함해야 합니다';
    }
    // 백엔드 규칙: 특수문자도 포함해야 함
    if (!RegExp(r'[@$!%*#?&]').hasMatch(value)) {
      return '특수문자(@\$!%*#?&)를 포함해야 합니다';
    }
    return null;
  }

  /// Step 1 → Step 2: 이메일 인증 코드 발송
  Future<void> _sendVerificationCode() async {
    if (!_formKey.currentState!.validate()) return;
    
    setState(() => _isLoading = true);
    
    final result = await _authService.sendVerificationCode(_emailController.text.trim());
    
    setState(() => _isLoading = false);
    
    if (result['success'] == true) {
      setState(() {
        _currentStep = 1;
        _startResendCountdown();
      });
      _showMessage('인증 코드가 발송되었습니다');
    } else {
      _showMessage(result['message'] ?? '인증 코드 발송 실패', isError: true);
    }
  }

  /// 인증 코드 재발송 타이머
  void _startResendCountdown() {
    _resendCountdown = 60;
    _countdownTimer?.cancel();
    _countdownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_resendCountdown > 0) {
        setState(() => _resendCountdown--);
      } else {
        timer.cancel();
      }
    });
  }

  /// 인증 코드 재발송
  Future<void> _resendCode() async {
    if (_resendCountdown > 0) return;
    
    setState(() => _isLoading = true);
    
    final result = await _authService.sendVerificationCode(_emailController.text.trim());
    
    setState(() => _isLoading = false);
    
    if (result['success'] == true) {
      _startResendCountdown();
      _showMessage('인증 코드가 재발송되었습니다');
    } else {
      _showMessage(result['message'] ?? '발송 실패', isError: true);
    }
  }

  /// 인증 코드 확인
  Future<void> _verifyCode() async {
    if (_verificationCodeController.text.length != 6) {
      _showMessage('6자리 인증 코드를 입력하세요', isError: true);
      return;
    }
    
    setState(() => _isLoading = true);
    
    final result = await _authService.verifyCode(
      _emailController.text.trim(),
      _verificationCodeController.text.trim(),
    );
    
    setState(() => _isLoading = false);
    
    if (result['success'] == true) {
      setState(() {
        _isEmailVerified = true;
      });
      _showMessage('이메일 인증 완료!');
      
      // 인증 성공 후 약간의 딜레이를 주고 회원가입 진행
      await Future.delayed(const Duration(milliseconds: 500));
      await _completeSignup();
    } else {
      _showMessage(result['message'] ?? '인증 실패', isError: true);
    }
  }

  /// 회원가입 완료
  Future<void> _completeSignup() async {
    setState(() => _isLoading = true);
    
    try {
      final result = await _authService.signup(
        _emailController.text.trim(),
        _passwordController.text,
        _nameController.text.trim(),
      );
      
      setState(() => _isLoading = false);
      
      if (result['success'] == true) {
        setState(() => _currentStep = 2);
        _showMessage('회원가입이 완료되었습니다!');
      } else {
        // 회원가입 실패 시 에러 메시지 표시
        final errorMessage = result['message'] ?? '회원가입 실패';
        _showMessage(errorMessage, isError: true);
        debugPrint('회원가입 실패: $errorMessage');
      }
    } catch (e) {
      setState(() => _isLoading = false);
      _showMessage('회원가입 중 오류가 발생했습니다: $e', isError: true);
      debugPrint('회원가입 예외: $e');
    }
  }

  void _showMessage(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red : Colors.green,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Scaffold(
      backgroundColor: isDark ? const Color(0xFF121212) : Colors.grey[50],
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: isDark ? Colors.white : Colors.black),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          '회원가입',
          style: TextStyle(color: isDark ? Colors.white : Colors.black),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              // Progress Indicator
              _buildProgressIndicator(),
              const SizedBox(height: 32),
              
              // Content based on step
              if (_currentStep == 0) _buildInfoInputStep(isDark),
              if (_currentStep == 1) _buildVerificationStep(isDark),
              if (_currentStep == 2) _buildCompletionStep(isDark),
            ],
          ),
        ),
      ),
    );
  }

  /// 진행 상태 표시
  Widget _buildProgressIndicator() {
    return Row(
      children: [
        _buildStepCircle(0, '정보입력'),
        Expanded(child: _buildStepLine(0)),
        _buildStepCircle(1, '이메일인증'),
        Expanded(child: _buildStepLine(1)),
        _buildStepCircle(2, '완료'),
      ],
    );
  }

  Widget _buildStepCircle(int step, String label) {
    final isActive = _currentStep >= step;
    return Column(
      children: [
        Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: isActive ? const Color(0xFF0066FF) : Colors.grey[300],
          ),
          child: Center(
            child: isActive && _currentStep > step
              ? const Icon(Icons.check, color: Colors.white, size: 20)
              : Text(
                  '${step + 1}',
                  style: TextStyle(
                    color: isActive ? Colors.white : Colors.grey[600],
                    fontWeight: FontWeight.bold,
                  ),
                ),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: isActive ? const Color(0xFF0066FF) : Colors.grey,
          ),
        ),
      ],
    );
  }

  Widget _buildStepLine(int afterStep) {
    final isActive = _currentStep > afterStep;
    return Container(
      height: 2,
      margin: const EdgeInsets.only(bottom: 20),
      color: isActive ? const Color(0xFF0066FF) : Colors.grey[300],
    );
  }

  /// Step 0: 정보 입력
  Widget _buildInfoInputStep(bool isDark) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '가입 정보를 입력하세요',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: isDark ? Colors.white : Colors.black87,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '중고차 시세 예측 서비스를 이용하기 위한\n회원 정보를 입력해주세요.',
            style: TextStyle(color: Colors.grey[600], height: 1.5),
          ),
          const SizedBox(height: 32),
          
          // 이름
          _buildTextField(
            controller: _nameController,
            label: '이름',
            hint: '홍길동',
            icon: Icons.person_outline,
            isDark: isDark,
            validator: (v) => v?.isEmpty == true ? '이름을 입력하세요' : null,
          ),
          const SizedBox(height: 16),
          
          // 이메일
          _buildTextField(
            controller: _emailController,
            label: '이메일',
            hint: 'example@email.com',
            icon: Icons.email_outlined,
            isDark: isDark,
            keyboardType: TextInputType.emailAddress,
            validator: (v) {
              if (v?.isEmpty == true) return '이메일을 입력하세요';
              if (!_isValidEmail(v!)) return '올바른 이메일 형식이 아닙니다';
              return null;
            },
          ),
          const SizedBox(height: 16),
          
          // 비밀번호
          _buildTextField(
            controller: _passwordController,
            label: '비밀번호',
            hint: '8자 이상, 영문+숫자+특수문자',
            icon: Icons.lock_outline,
            isDark: isDark,
            obscureText: _obscurePassword,
            suffixIcon: IconButton(
              icon: Icon(_obscurePassword ? Icons.visibility_off : Icons.visibility),
              onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
            ),
            validator: _validatePassword,
          ),
          const SizedBox(height: 16),
          
          // 비밀번호 확인
          _buildTextField(
            controller: _confirmPasswordController,
            label: '비밀번호 확인',
            hint: '비밀번호를 다시 입력하세요',
            icon: Icons.lock_outline,
            isDark: isDark,
            obscureText: _obscureConfirmPassword,
            suffixIcon: IconButton(
              icon: Icon(_obscureConfirmPassword ? Icons.visibility_off : Icons.visibility),
              onPressed: () => setState(() => _obscureConfirmPassword = !_obscureConfirmPassword),
            ),
            validator: (v) {
              if (v != _passwordController.text) return '비밀번호가 일치하지 않습니다';
              return null;
            },
          ),
          const SizedBox(height: 32),
          
          // 다음 버튼
          SizedBox(
            width: double.infinity,
            height: 56,
            child: ElevatedButton(
              onPressed: _isLoading ? null : _sendVerificationCode,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0066FF),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: _isLoading
                ? const SizedBox(
                    width: 24, height: 24,
                    child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                  )
                : const Text(
                    '인증 코드 발송',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
            ),
          ),
        ],
      ),
    );
  }

  /// Step 1: 이메일 인증
  Widget _buildVerificationStep(bool isDark) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '이메일 인증',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: isDark ? Colors.white : Colors.black87,
          ),
        ),
        const SizedBox(height: 8),
        RichText(
          text: TextSpan(
            style: TextStyle(color: Colors.grey[600], height: 1.5),
            children: [
              const TextSpan(text: '인증 코드가 '),
              TextSpan(
                text: _emailController.text,
                style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF0066FF)),
              ),
              const TextSpan(text: '\n으로 발송되었습니다.'),
            ],
          ),
        ),
        const SizedBox(height: 32),
        
        // 인증 코드 입력
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          decoration: BoxDecoration(
            color: isDark ? const Color(0xFF1E1E1E) : Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFF0066FF), width: 2),
          ),
          child: TextField(
            controller: _verificationCodeController,
            keyboardType: TextInputType.number,
            maxLength: 6,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 32,
              fontWeight: FontWeight.bold,
              letterSpacing: 16,
            ),
            decoration: const InputDecoration(
              border: InputBorder.none,
              counterText: '',
              hintText: '000000',
              hintStyle: TextStyle(color: Colors.grey),
            ),
          ),
        ),
        const SizedBox(height: 16),
        
        // 타이머 및 재발송
        Center(
          child: _resendCountdown > 0
            ? Text(
                '재발송 가능: ${_resendCountdown}초',
                style: TextStyle(color: Colors.grey[600]),
              )
            : TextButton(
                onPressed: _resendCode,
                child: const Text('인증 코드 재발송'),
              ),
        ),
        const SizedBox(height: 32),
        
        // 인증 버튼
        SizedBox(
          width: double.infinity,
          height: 56,
          child: ElevatedButton(
            onPressed: _isLoading ? null : _verifyCode,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0066FF),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: _isLoading
              ? const SizedBox(
                  width: 24, height: 24,
                  child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                )
              : const Text(
                  '인증 확인',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                ),
          ),
        ),
        const SizedBox(height: 16),
        
        // 이전 단계
        Center(
          child: TextButton(
            onPressed: () => setState(() => _currentStep = 0),
            child: const Text('이전 단계로'),
          ),
        ),
      ],
    );
  }

  /// Step 2: 완료
  Widget _buildCompletionStep(bool isDark) {
    return Column(
      children: [
        const SizedBox(height: 40),
        Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: Colors.green.withOpacity(0.1),
          ),
          child: const Icon(Icons.check_circle, size: 60, color: Colors.green),
        ),
        const SizedBox(height: 24),
        Text(
          '회원가입 완료!',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: isDark ? Colors.white : Colors.black87,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          '${_nameController.text}님, 환영합니다!\n이제 로그인하여 서비스를 이용하세요.',
          textAlign: TextAlign.center,
          style: TextStyle(color: Colors.grey[600], height: 1.5),
        ),
        const SizedBox(height: 40),
        SizedBox(
          width: double.infinity,
          height: 56,
          child: ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0066FF),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: const Text(
              '로그인하러 가기',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
            ),
          ),
        ),
      ],
    );
  }

  /// 공통 텍스트 필드
  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required String hint,
    required IconData icon,
    required bool isDark,
    bool obscureText = false,
    TextInputType? keyboardType,
    Widget? suffixIcon,
    String? Function(String?)? validator,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontWeight: FontWeight.w600,
            color: isDark ? Colors.white : Colors.black87,
          ),
        ),
        const SizedBox(height: 8),
        TextFormField(
          controller: controller,
          obscureText: obscureText,
          keyboardType: keyboardType,
          validator: validator,
          decoration: InputDecoration(
            hintText: hint,
            prefixIcon: Icon(icon, color: Colors.grey),
            suffixIcon: suffixIcon,
            filled: true,
            fillColor: isDark ? const Color(0xFF1E1E1E) : Colors.white,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(color: Colors.grey[300]!),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF0066FF), width: 2),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Colors.red),
            ),
          ),
        ),
      ],
    );
  }
}
