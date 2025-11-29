import 'package:flutter/material.dart';
import '../../services/api_service.dart';

/// 차량 옵션 배지 공통 위젯
/// 
/// 사용처:
/// - result_page.dart (실매물 카드)
/// - model_deals_modal.dart (모델별 매물)
/// - deal_analysis_modal.dart (매물 상세)
/// - mypage.dart (최근 분석)
class OptionBadges extends StatelessWidget {
  final CarOptions options;
  final bool compact;  // 축약 모드 (최대 3~4개만 표시)
  final bool showAll;  // 전체 옵션 표시

  const OptionBadges({
    super.key,
    required this.options,
    this.compact = true,
    this.showAll = false,
  });

  @override
  Widget build(BuildContext context) {
    final badges = _buildBadgeList();
    if (badges.isEmpty) return const SizedBox.shrink();

    return Wrap(
      spacing: 4,
      runSpacing: 4,
      children: badges,
    );
  }

  List<Widget> _buildBadgeList() {
    final badges = <Widget>[];
    
    // 1. 무사고 (높은 우선순위)
    if (options.isAccidentFree) {
      badges.add(const _Badge(text: '무사고', color: Colors.green, priority: 1));
    }
    
    // 2. 성능점검 등급
    if (options.inspectionText.isNotEmpty) {
      badges.add(_Badge(text: options.inspectionText, color: Colors.orange, priority: 2));
    }
    
    // 3. 주요 옵션들
    final optionItems = [
      if (options.hasSunroof) const _Badge(text: '선루프', color: Colors.blue, priority: 3),
      if (options.hasNavigation) const _Badge(text: '내비', color: Colors.blue, priority: 4),
      if (options.hasLeatherSeat) const _Badge(text: '가죽', color: Colors.blue, priority: 5),
      if (options.hasSmartKey) const _Badge(text: '스마트키', color: Colors.blue, priority: 6),
      if (options.hasRearCamera) const _Badge(text: '후방캠', color: Colors.blue, priority: 7),
      if (options.hasHeatedSeat) const _Badge(text: '열선', color: Colors.blue, priority: 8),
      if (options.hasVentilatedSeat) const _Badge(text: '통풍', color: Colors.blue, priority: 9),
    ];
    
    if (compact && !showAll) {
      // compact 모드: 무사고, 성능점검 + 옵션 최대 3개
      final maxOptions = badges.length >= 2 ? 2 : (4 - badges.length);
      badges.addAll(optionItems.take(maxOptions));
    } else {
      badges.addAll(optionItems);
    }
    
    return badges;
  }
}

/// 개별 배지 위젯
class _Badge extends StatelessWidget {
  final String text;
  final Color color;
  final int priority;

  const _Badge({
    required this.text,
    required this.color,
    this.priority = 99,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color.withOpacity(0.3), width: 0.5),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: color,
          fontSize: 9,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}

/// 옵션 상세 정보 섹션 (deal_analysis_modal용)
class OptionDetailSection extends StatelessWidget {
  final CarOptions options;
  final bool isDark;

  const OptionDetailSection({
    super.key,
    required this.options,
    required this.isDark,
  });

  @override
  Widget build(BuildContext context) {
    final textColor = isDark ? Colors.white : Colors.black87;
    final cardColor = isDark ? const Color(0xFF2A2A2A) : Colors.grey[50];
    
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.settings_suggest_outlined, size: 20, color: textColor),
              const SizedBox(width: 8),
              Text(
                "차량 옵션",
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: textColor,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // 무사고 / 성능점검
          _buildInfoRow(
            icon: Icons.verified_user,
            label: '무사고',
            value: options.isAccidentFree ? '확인' : '미확인',
            isPositive: options.isAccidentFree,
            textColor: textColor,
          ),
          const SizedBox(height: 8),
          if (options.inspectionGrade.isNotEmpty)
            _buildInfoRow(
              icon: Icons.fact_check,
              label: '성능점검',
              value: options.inspectionText.isNotEmpty ? options.inspectionText : '-',
              isPositive: options.inspectionGrade == 'excellent' || options.inspectionGrade == 'good',
              textColor: textColor,
            ),
          
          const SizedBox(height: 16),
          const Divider(height: 1),
          const SizedBox(height: 16),
          
          // 옵션 그리드
          _buildOptionGrid(textColor),
        ],
      ),
    );
  }

  Widget _buildInfoRow({
    required IconData icon,
    required String label,
    required String value,
    required bool isPositive,
    required Color textColor,
  }) {
    return Row(
      children: [
        Icon(icon, size: 18, color: isPositive ? Colors.green : Colors.grey),
        const SizedBox(width: 8),
        Text(label, style: TextStyle(color: Colors.grey[600], fontSize: 13)),
        const Spacer(),
        Text(
          value,
          style: TextStyle(
            color: isPositive ? Colors.green : textColor,
            fontWeight: FontWeight.w600,
            fontSize: 13,
          ),
        ),
      ],
    );
  }

  Widget _buildOptionGrid(Color textColor) {
    final allOptions = [
      _OptionItem('선루프', options.hasSunroof, Icons.wb_sunny_outlined),
      _OptionItem('내비게이션', options.hasNavigation, Icons.navigation_outlined),
      _OptionItem('가죽시트', options.hasLeatherSeat, Icons.airline_seat_recline_normal),
      _OptionItem('스마트키', options.hasSmartKey, Icons.key),
      _OptionItem('후방카메라', options.hasRearCamera, Icons.camera_rear),
      _OptionItem('열선시트', options.hasHeatedSeat, Icons.whatshot_outlined),
      _OptionItem('통풍시트', options.hasVentilatedSeat, Icons.air),
    ];

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 4,
        crossAxisSpacing: 8,
        mainAxisSpacing: 8,
      ),
      itemCount: allOptions.length,
      itemBuilder: (context, index) {
        final opt = allOptions[index];
        return Row(
          children: [
            Icon(
              opt.hasOption ? Icons.check_circle : Icons.cancel_outlined,
              size: 16,
              color: opt.hasOption ? Colors.green : Colors.grey[400],
            ),
            const SizedBox(width: 6),
            Expanded(
              child: Text(
                opt.label,
                style: TextStyle(
                  color: opt.hasOption ? textColor : Colors.grey[500],
                  fontSize: 12,
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        );
      },
    );
  }
}

class _OptionItem {
  final String label;
  final bool hasOption;
  final IconData icon;

  const _OptionItem(this.label, this.hasOption, this.icon);
}
