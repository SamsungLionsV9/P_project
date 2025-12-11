import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';
import 'theme/theme_provider.dart';
import 'services/api_service.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({super.key});

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  static const String _adminEmail = 'admin@carsentix.com';
  static const String _prefKeyFraudAlert = 'notification_fraud_alert';
  
  final ApiService _api = ApiService();
  AiStatus? _aiStatus;
  bool _isLoadingAiStatus = true;
  bool _fraudAlertEnabled = true;

  @override
  void initState() {
    super.initState();
    _loadAiStatus();
    _loadNotificationSettings();
  }
  
  Future<void> _loadNotificationSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _fraudAlertEnabled = prefs.getBool(_prefKeyFraudAlert) ?? true;
    });
  }
  
  Future<void> _setFraudAlertEnabled(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_prefKeyFraudAlert, value);
    setState(() => _fraudAlertEnabled = value);
  }
  
  Future<void> _openEmailApp() async {
    // mailto URI 직접 생성 (queryParameters 인코딩 문제 방지)
    final String emailUrl = 'mailto:$_adminEmail?subject=${Uri.encodeComponent('[CarSentix] 문의사항')}&body=${Uri.encodeComponent('문의 내용을 작성해주세요.\n\n---\n앱 버전: v1.0.0')}';
    final Uri emailUri = Uri.parse(emailUrl);
    
    try {
      final launched = await launchUrl(
        emailUri,
        mode: LaunchMode.externalApplication,
      );
      if (!launched && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('이메일 앱을 열 수 없습니다. 직접 admin@carsentix.com으로 문의해주세요.')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('이메일 앱 오류: $e')),
        );
      }
    }
  }
  
  void _showNotificationSettings(bool isDark, Color cardColor, Color textColor, Color? subTextColor) {
    showModalBottomSheet(
      context: context,
      backgroundColor: cardColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => StatefulBuilder(
        builder: (context, setModalState) => Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                '🔔 알림 설정',
                style: TextStyle(
                  color: textColor,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 24),
              _buildNotificationOption(
                title: '허위매물 경고',
                subtitle: '고위험 매물 감지 시 알림',
                value: _fraudAlertEnabled,
                onChanged: (value) {
                  _setFraudAlertEnabled(value);
                  setModalState(() {});
                },
                textColor: textColor,
                subTextColor: subTextColor,
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: isDark ? Colors.blue.withOpacity(0.1) : Colors.blue.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info_outline, color: Colors.blue[400], size: 20),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        '허위매물 경고는 분석 시 자동으로 확인됩니다',
                        style: TextStyle(color: subTextColor, fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildNotificationOption({
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
    required Color textColor,
    Color? subTextColor,
  }) {
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: TextStyle(
                  color: textColor,
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                subtitle,
                style: TextStyle(color: subTextColor, fontSize: 13),
              ),
            ],
          ),
        ),
        Switch(
          value: value,
          onChanged: onChanged,
          activeColor: const Color(0xFF0066FF),
        ),
      ],
    );
  }

  Future<void> _loadAiStatus() async {
    setState(() => _isLoadingAiStatus = true);
    final status = await _api.getAiStatus();
    if (mounted) {
      setState(() {
        _aiStatus = status;
        _isLoadingAiStatus = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ThemeProvider>(
      builder: (context, themeProvider, child) {
        // 다크 모드에 따른 색상 정의
        final isDark = themeProvider.isDarkMode;
        final bgColor = isDark ? const Color(0xFF121212) : const Color(0xFFF5F7FA);
        final cardColor = isDark ? const Color(0xFF1E1E1E) : Colors.white;
        final textColor = isDark ? Colors.white : Colors.black;
        final subTextColor = isDark ? Colors.grey[400] : Colors.grey[600];
        final iconColor = isDark ? Colors.white70 : Colors.black87;

    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        backgroundColor: bgColor,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios, color: textColor),
          onPressed: () {
             // 메인 탭 구조상 뒤로가기 동작 정의 필요 시 구현
          },
        ),
        title: Text(
          "설정",
          style: TextStyle(
            color: textColor,
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildSectionHeader("일반", subTextColor),
            const SizedBox(height: 12),
            Container(
              decoration: BoxDecoration(
                color: cardColor,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                children: [
                  _buildSwitchTile(
                    title: "다크 모드",
                    value: themeProvider.isDarkMode,
                    onChanged: (value) => themeProvider.setDarkMode(value),
                    textColor: textColor,
                    activeColor: const Color(0xFF0066FF),
                  ),
                  _buildDivider(isDark),
                  _buildListTile(
                    title: "알림 설정",
                    subtitle: _fraudAlertEnabled ? "허위매물 경고 켜짐" : "알림 꺼짐",
                    onTap: () => _showNotificationSettings(isDark, cardColor, textColor, subTextColor),
                    textColor: textColor,
                    subTextColor: subTextColor,
                    iconColor: iconColor,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),

            _buildSectionHeader("AI 엔진", subTextColor),
            const SizedBox(height: 12),
            Container(
              decoration: BoxDecoration(
                color: cardColor,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                children: [
                  // Groq API 연결 상태 표시
                  _buildAiStatusTile(textColor, subTextColor),
                  _buildDivider(isDark),
                  _buildListTile(
                    title: "API 키 설정 (선택)",
                    subtitle: "기본 엔진 사용 중",
                    onTap: () {},
                    textColor: textColor,
                    subTextColor: subTextColor,
                    iconColor: iconColor,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),

            _buildSectionHeader("지원 및 정보", subTextColor),
            const SizedBox(height: 12),
            Container(
              decoration: BoxDecoration(
                color: cardColor,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                children: [
                  _buildListTile(
                    title: "기록 삭제",
                    onTap: () {},
                    textColor: textColor,
                    iconColor: iconColor,
                    isDestructive: true,
                  ),
                  _buildDivider(isDark),
                  _buildListTile(
                    title: "문의하기",
                    subtitle: _adminEmail,
                    onTap: _openEmailApp,
                    textColor: textColor,
                    subTextColor: subTextColor,
                    iconColor: iconColor,
                  ),
                  _buildDivider(isDark),
                  _buildListTile(
                    title: "버전 정보",
                    trailingText: "v1.0.0",
                    onTap: null, // 클릭 불가
                    textColor: textColor,
                    subTextColor: subTextColor,
                    iconColor: iconColor,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
      },
    );
  }

  Widget _buildSectionHeader(String title, Color? color) {
    return Padding(
      padding: const EdgeInsets.only(left: 4, bottom: 4),
      child: Text(
        title,
        style: TextStyle(
          color: color,
          fontSize: 14,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  Widget _buildSwitchTile({
    required String title,
    required bool value,
    required ValueChanged<bool> onChanged,
    required Color textColor,
    required Color activeColor,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            title,
            style: TextStyle(
              color: textColor,
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
          Switch(
            value: value,
            onChanged: onChanged,
            activeColor: activeColor,
            activeTrackColor: activeColor.withOpacity(0.2),
          ),
        ],
      ),
    );
  }

  Widget _buildListTile({
    required String title,
    String? subtitle,
    String? trailingText,
    required VoidCallback? onTap,
    required Color textColor,
    Color? subTextColor,
    required Color iconColor,
    bool isDestructive = false,
  }) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      color: isDestructive ? Colors.red : textColor,
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  if (subtitle != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: TextStyle(
                        color: subTextColor,
                        fontSize: 13,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            if (isDestructive)
              const Icon(Icons.delete_outline, color: Colors.red, size: 20)
            else if (trailingText != null)
              Text(
                trailingText,
                style: TextStyle(
                  color: subTextColor,
                  fontSize: 14,
                ),
              )
            else
              Icon(Icons.arrow_forward_ios, color: iconColor.withOpacity(0.3), size: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildDivider(bool isDark) {
    return Divider(
      height: 1,
      thickness: 1,
      color: isDark ? Colors.grey[800] : Colors.grey[100],
    );
  }

  /// Groq API 연결 상태 표시 위젯
  Widget _buildAiStatusTile(Color textColor, Color? subTextColor) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "Groq AI 연결 상태",
                  style: TextStyle(
                    color: textColor,
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                if (_isLoadingAiStatus)
                  Text(
                    "확인 중...",
                    style: TextStyle(color: subTextColor, fontSize: 13),
                  )
                else
                  Text(
                    _aiStatus?.isConnected == true
                        ? "Llama 3.3 70B 연결됨"
                        : "연결 안됨 (템플릿 모드)",
                    style: TextStyle(color: subTextColor, fontSize: 13),
                  ),
              ],
            ),
          ),
          // 연결 상태 인디케이터
          if (_isLoadingAiStatus)
            const SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          else
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: _aiStatus?.isConnected == true
                    ? Colors.green.withOpacity(0.15)
                    : Colors.orange.withOpacity(0.15),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    _aiStatus?.isConnected == true
                        ? Icons.check_circle
                        : Icons.warning_rounded,
                    color: _aiStatus?.isConnected == true
                        ? Colors.green
                        : Colors.orange,
                    size: 16,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    _aiStatus?.isConnected == true ? "연결됨" : "기본",
                    style: TextStyle(
                      color: _aiStatus?.isConnected == true
                          ? Colors.green
                          : Colors.orange,
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}
