import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'services/api_service.dart';

class NegotiationPage extends StatefulWidget {
  final int initialTabIndex; // 0: 문자 전송, 1: 전화 통화
  final String? carName;
  final String? price;
  final String? info;
  // 고도화: 정확한 가격 정보
  final int? actualPrice; // 실제 판매가
  final int? predictedPrice; // AI 예측가
  final int? year; // 연식
  final int? mileage; // 주행거리

  const NegotiationPage({
    super.key,
    this.initialTabIndex = 0,
    this.carName,
    this.price,
    this.info,
    this.actualPrice,
    this.predictedPrice,
    this.year,
    this.mileage,
  });

  @override
  State<NegotiationPage> createState() => _NegotiationPageState();
}

class _NegotiationPageState extends State<NegotiationPage> {
  final ApiService _apiService = ApiService();
  late int _currentTabIndex;

  // 체크리스트 상태
  bool _checkTire = true;
  bool _checkPrice = true;
  bool _checkCoolDeal = false;

  // AI 생성 대본 상태
  bool _isGenerating = false;
  String? _generatedMessage;
  List<String>? _generatedPhoneScripts;
  String? _generatedTip;

  @override
  void initState() {
    super.initState();
    _currentTabIndex = widget.initialTabIndex;
  }

  /// 선택된 체크포인트 리스트
  List<String> get _selectedCheckpoints {
    final List<String> points = [];
    if (_checkTire) points.add("타이어 마모 상태");
    if (_checkPrice) points.add("동급 매물 대비 높은 가격");
    if (_checkCoolDeal) points.add("쿨거래 의사");
    return points;
  }

  /// AI 대본 생성
  Future<void> _generateScript() async {
    setState(() => _isGenerating = true);

    try {
      final script = await _apiService.generateNegotiationScript(
        carName: widget.carName ?? '차량',
        price: widget.price ?? '0만원',
        info: widget.info ?? '',
        checkpoints: _selectedCheckpoints,
        // 정확한 가격 정보 전달
        actualPrice: widget.actualPrice,
        predictedPrice: widget.predictedPrice,
        year: widget.year,
        mileage: widget.mileage,
      );

      setState(() {
        _generatedMessage = script.messageScript;
        _generatedPhoneScripts = script.phoneScript;
        _generatedTip = script.tip;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✨ AI 대본이 생성되었습니다!'),
            backgroundColor: Color(0xFF0066FF),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('대본 생성 실패: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isGenerating = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardColor = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final textColor = isDark ? Colors.white : Colors.black;

    final borderColor = isDark ? Colors.grey[800]! : const Color(0xFFBBDEFB);

    return Scaffold(
      // backgroundColor uses theme default
      appBar: AppBar(
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios, color: textColor),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          "네고 도우미",
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
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              // 1. 협상 포인트 점검 카드
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: cardColor,
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "협상 포인트 점검",
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: textColor,
                      ),
                    ),
                    const SizedBox(height: 20),
                    _buildCheckboxItem(
                        "타이어 마모 상태 (교체 필요 어필)",
                        _checkTire,
                        (v) => setState(() => _checkTire = v!),
                        textColor,
                        isDark),
                    _buildCheckboxItem(
                        "동급 매물 대비 높은 가격",
                        _checkPrice,
                        (v) => setState(() => _checkPrice = v!),
                        textColor,
                        isDark),
                    _buildCheckboxItem(
                        "쿨거래 의사 표현 (계약금 즉시 입금)",
                        _checkCoolDeal,
                        (v) => setState(() => _checkCoolDeal = v!),
                        textColor,
                        isDark),
                    const SizedBox(height: 16),
                    // AI 대본 생성 버튼
                    SizedBox(
                      width: double.infinity,
                      height: 48,
                      child: ElevatedButton.icon(
                        onPressed: _isGenerating ? null : _generateScript,
                        icon: _isGenerating
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                    color: Colors.white, strokeWidth: 2),
                              )
                            : const Icon(Icons.auto_awesome, size: 20),
                        label: Text(
                          _isGenerating ? "생성 중..." : "🤖 AI 대본 생성",
                          style: const TextStyle(
                              fontSize: 14, fontWeight: FontWeight.bold),
                        ),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF9C27B0),
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          elevation: 0,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // 2. 탭 버튼 (Segmented Control 스타일)
              Container(
                decoration: BoxDecoration(
                  color: cardColor,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Row(
                  children: [
                    _buildTabButton(
                        "문자 전송", Icons.chat_bubble_outline, 0, isDark),
                    _buildTabButton("전화 통화", Icons.phone_in_talk, 1, isDark),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // 3. 탭 컨텐츠
              if (_currentTabIndex == 0)
                _buildTextMessageView(isDark, cardColor, textColor)
              else
                _buildPhoneCallView(isDark, cardColor, textColor, borderColor),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCheckboxItem(String text, bool value, Function(bool?) onChanged,
      Color textColor, bool isDark) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          SizedBox(
            width: 24,
            height: 24,
            child: Checkbox(
              value: value,
              onChanged: onChanged,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(6)),
              activeColor: isDark ? Colors.grey[700] : Colors.black,
              checkColor: Colors.white,
              side:
                  BorderSide(color: isDark ? Colors.grey[500]! : Colors.black),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              text,
              style: TextStyle(fontSize: 14, color: textColor),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTabButton(String text, IconData icon, int index, bool isDark) {
    bool isSelected = _currentTabIndex == index;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _currentTabIndex = index),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            color: isSelected ? const Color(0xFF0066FF) : Colors.transparent,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                color: isSelected ? Colors.white : Colors.grey,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                text,
                style: TextStyle(
                  color: isSelected ? Colors.white : Colors.grey,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // 문자 전송 뷰
  Widget _buildTextMessageView(bool isDark, Color cardColor, Color textColor) {
    const String defaultMessage = """안녕하세요, 엔카 보고 연락드립니다.

차량 상태는 마음에 드는데, AI 분석 결과와 타이어 상태를 보니 가격 조정이 조금 필요해 보입니다.

타이어 교체 비용도 고려하면 협상 가능하실까요?

빠른 거래 원하시면 계약금 바로 준비하겠습니다.""";

    final String message = _generatedMessage ?? defaultMessage;
    final bool isAiGenerated = _generatedMessage != null;

    return Column(
      children: [
        if (isAiGenerated)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            margin: const EdgeInsets.only(bottom: 12),
            decoration: BoxDecoration(
              color: const Color(0xFF9C27B0).withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
              border:
                  Border.all(color: const Color(0xFF9C27B0).withOpacity(0.3)),
            ),
            child: const Row(
              children: [
                Icon(Icons.auto_awesome, color: Color(0xFF9C27B0), size: 16),
                SizedBox(width: 8),
                Text(
                  'AI가 생성한 맞춤 대본입니다',
                  style: TextStyle(
                      color: Color(0xFF9C27B0),
                      fontSize: 12,
                      fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: isDark ? const Color(0xFF2C2C2C) : const Color(0xFFEDF2F7),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Text(
            message,
            style: TextStyle(
              fontSize: 14,
              height: 1.6,
              color: textColor,
            ),
          ),
        ),
        const SizedBox(height: 24),
        SizedBox(
          width: double.infinity,
          height: 56,
          child: ElevatedButton.icon(
            onPressed: () {
              Clipboard.setData(ClipboardData(text: message));
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text("문자 내용이 복사되었습니다.")),
              );
            },
            icon: const Icon(Icons.copy, size: 20),
            label: const Text(
              "문자 내용 복사하기",
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0066FF),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              elevation: 0,
            ),
          ),
        ),
      ],
    );
  }

  // 전화 통화 뷰
  Widget _buildPhoneCallView(
      bool isDark, Color cardColor, Color textColor, Color borderColor) {
    final bool isAiGenerated =
        _generatedPhoneScripts != null && _generatedPhoneScripts!.isNotEmpty;
    final String tip = _generatedTip ?? "자신감 있는 목소리로, 하지만 정중하게 협상하세요";

    // 기본 스크립트
    final defaultScripts = [
      {
        "step": 1,
        "title": "1단계: 인사 & 매물 확인",
        "content": "\"사장님 안녕하세요, OO차량 아직 있나요?\""
      },
      {
        "step": 2,
        "title": "2단계: 네고 시도",
        "content": "\"차는 좋은데, 예산이 조금 초과돼서요. 30만원만 빼주시면 지금 바로 갈게요.\""
      },
      {"step": 3, "title": "3단계: 마무리", "content": "\"감사합니다. 문자로 주소 찍어주세요.\""},
    ];

    return Column(
      children: [
        Row(
          children: [
            Text(
              "단계별 통화 대본",
              style: TextStyle(
                  fontSize: 16, fontWeight: FontWeight.bold, color: textColor),
            ),
            if (isAiGenerated) ...[
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: const Color(0xFF9C27B0).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Text(
                  'AI 생성',
                  style: TextStyle(
                      color: Color(0xFF9C27B0),
                      fontSize: 10,
                      fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ],
        ),
        const SizedBox(height: 16),

        // 스크립트 카드들
        if (isAiGenerated)
          ...List.generate(_generatedPhoneScripts!.length, (index) {
            final script = _generatedPhoneScripts![index];
            return _buildScriptCard(index + 1, "단계 ${index + 1}", script,
                cardColor, textColor, isDark);
          })
        else
          ...defaultScripts.map((s) => _buildScriptCard(
                s['step'] as int,
                s['title'] as String,
                s['content'] as String,
                cardColor,
                textColor,
                isDark,
              )),

        const SizedBox(height: 24),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: isDark
                ? const Color(0xFF1A237E).withOpacity(0.3)
                : const Color(0xFFE3F2FD),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: borderColor),
          ),
          child: Row(
            children: [
              const Icon(Icons.lightbulb, color: Color(0xFF0066FF), size: 20),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  "Tip: $tip",
                  style: const TextStyle(
                    color: Color(0xFF0066FF),
                    fontWeight: FontWeight.bold,
                    fontSize: 13,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildScriptCard(int step, String title, String content,
      Color cardColor, Color textColor, bool isDark) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
            color: isDark ? Colors.grey[700]! : const Color(0xFF0066FF)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 28,
            height: 28,
            decoration: const BoxDecoration(
              color: Color(0xFF0066FF),
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text(
                step.toString(),
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: Color(0xFF0066FF),
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  content,
                  style: TextStyle(
                    color: textColor,
                    fontSize: 14,
                    height: 1.5,
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
