import 'package:flutter/material.dart';
import 'result_page.dart';
import 'services/api_service.dart';

class CarInfoInputPage extends StatefulWidget {
  const CarInfoInputPage({super.key});

  @override
  State<CarInfoInputPage> createState() => _CarInfoInputPageState();
}

class _CarInfoInputPageState extends State<CarInfoInputPage> {
  // API 서비스
  final ApiService _apiService = ApiService();
  
  // 상태 변수들
  String? _selectedBrand;
  String? _selectedModel;
  String? _selectedYear;
  String? _selectedRegion;
  final TextEditingController _mileageController = TextEditingController();
  String _selectedFuel = '가솔린';
  int _performanceRating = 4;
  bool _isAccidentFree = false;
  
  // 로딩 상태
  bool _isLoading = false;
  String? _errorMessage;

  // 옵션 상태
  bool _hasSunroof = false;
  bool _hasNavigation = false;
  bool _hasLeatherSeats = false;
  bool _hasSmartKey = false;
  bool _hasRearCamera = false;
  
  // 사용자에게 보여줄 간단한 모델 목록
  final Map<String, List<String>> _brandModels = {
    '현대': ['아반떼', '쏘나타', '그랜저', '투싼', '싼타페', '팰리세이드', '스타리아'],
    '기아': ['모닝', '레이', 'K3', 'K5', 'K8', 'K9', '셀토스', '스포티지', '쏘렌토', '카니발', 'EV6', 'EV9'],
    '제네시스': ['G70', 'G80', 'G90', 'GV60', 'GV70', 'GV80'],
    'BMW': ['3시리즈', '5시리즈', '7시리즈', 'X3', 'X5', 'X7'],
    '벤츠': ['C-클래스', 'E-클래스', 'S-클래스', 'GLC', 'GLE', 'GLS'],
    '아우디': ['A4', 'A6', 'A8', 'Q3', 'Q5', 'Q7', 'Q8'],
  };

  // 연식에 따른 실제 백엔드 모델명 매핑
  String _getBackendModelName(String brand, String model, int year) {
    // 현대
    if (brand == '현대') {
      if (model == '아반떼') {
        if (year >= 2021) return '아반떼 (CN7)';
        if (year >= 2016) return '아반떼 AD';
        return '아반떼 MD';
      }
      if (model == '쏘나타') {
        if (year >= 2024) return '쏘나타 디 엣지(DN8)';
        if (year >= 2020) return '쏘나타 (DN8)';
        if (year >= 2015) return 'LF 쏘나타';
        return 'YF 쏘나타';
      }
      if (model == '그랜저') {
        if (year >= 2023) return '그랜저 (GN7)';
        if (year >= 2020) return '더 뉴 그랜저 IG';
        if (year >= 2017) return '그랜저 IG';
        return '그랜저 HG';
      }
      if (model == '투싼') {
        if (year >= 2024) return '더 뉴 투싼 (NX4)';
        if (year >= 2021) return '투싼 (NX4)';
        return '올 뉴 투싼';
      }
      if (model == '싼타페') {
        if (year >= 2024) return '싼타페 (MX5)';
        if (year >= 2019) return '싼타페 TM';
        return '싼타페 DM';
      }
      if (model == '팰리세이드') {
        if (year >= 2023) return '더 뉴 팰리세이드';
        return '팰리세이드';
      }
    }
    // 기아
    if (brand == '기아') {
      if (model == 'K5') {
        if (year >= 2024) return '더 뉴 K5 (DL3)';
        if (year >= 2020) return 'K5 (DL3)';
        return 'K5';
      }
      if (model == '스포티지') {
        if (year >= 2024) return '더 뉴 스포티지 (NQ5)';
        if (year >= 2022) return '스포티지 (NQ5)';
        return '스포티지';
      }
      if (model == '쏘렌토') {
        if (year >= 2024) return '더 뉴 쏘렌토 (MQ4)';
        if (year >= 2020) return '쏘렌토 (MQ4)';
        return '쏘렌토';
      }
      if (model == '카니발') {
        if (year >= 2024) return '더 뉴 카니발 (KA4)';
        if (year >= 2021) return '카니발 (KA4)';
        return '카니발';
      }
      if (model == 'K9') {
        if (year >= 2022) return '더 뉴 K9 2세대';
        if (year >= 2018) return '더 K9';
        return 'K9';
      }
      if (model == 'K8') {
        if (year >= 2024) return '더 뉴 K8';
        if (year >= 2021) return 'K8';
        return 'K8';
      }
      if (model == 'K3') {
        if (year >= 2022) return '더 뉴 K3 (BD)';
        if (year >= 2019) return 'K3 (BD)';
        return 'K3';
      }
      if (model == 'EV6') {
        return 'EV6';
      }
      if (model == 'EV9') {
        return 'EV9';
      }
      if (model == '셀토스') {
        if (year >= 2023) return '더 뉴 셀토스';
        return '셀토스';
      }
      if (model == '모닝') {
        if (year >= 2020) return '더 뉴 모닝';
        return '올 뉴 모닝';
      }
      if (model == '레이') {
        if (year >= 2022) return '더 뉴 레이';
        return '레이';
      }
    }
    // 제네시스
    if (brand == '제네시스') {
      if (model == 'G80' && year >= 2020) return 'G80 (RG3)';
      if (model == 'G90' && year >= 2022) return 'G90 (RS4)';
    }
    // 기본: 모델명 그대로 반환
    return model;
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardColor = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final textColor = isDark ? Colors.white : Colors.black;
    final subTextColor = isDark ? Colors.grey[400] : Colors.grey[600];
    final borderColor = isDark ? Colors.grey[700]! : Colors.grey[200]!;

    return Scaffold(
      // backgroundColor uses theme default
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios, color: textColor),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          "차량 정보 입력",
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
              // 1. 기본 정보 카드
              Container(
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
                    // 브랜드 / 모델 선택 (Row)
                    Row(
                      children: [
                        Expanded(
                          child: _buildDropdown(
                            hint: "브랜드 선택",
                            value: _selectedBrand,
                            items: _brandModels.keys.toList(),
                            onChanged: (val) {
                              setState(() {
                                _selectedBrand = val;
                                _selectedModel = null; // 브랜드 변경 시 모델 초기화
                              });
                            },
                            isDark: isDark,
                            textColor: textColor,
                            borderColor: borderColor,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _buildDropdown(
                            hint: "모델 선택",
                            value: _selectedModel,
                            items: _selectedBrand != null 
                                ? _brandModels[_selectedBrand] ?? []
                                : [],
                            onChanged: (val) => setState(() => _selectedModel = val),
                            isDark: isDark,
                            textColor: textColor,
                            borderColor: borderColor,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),

                    // 연식 선택
                    _buildDropdown(
                      hint: "2024년",
                      value: _selectedYear,
                      items: List.generate(10, (index) => "${2024 - index}년"),
                      onChanged: (val) => setState(() => _selectedYear = val),
                      isDark: isDark,
                      textColor: textColor,
                      borderColor: borderColor,
                    ),
                    const SizedBox(height: 16),

                    // 주행거리 입력
                    Container(
                      decoration: BoxDecoration(
                        border: Border.all(color: borderColor),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Row(
                        children: [
                          Expanded(
                            child: TextField(
                              controller: _mileageController,
                              keyboardType: TextInputType.number,
                              style: TextStyle(color: textColor),
                              decoration: const InputDecoration(
                                hintText: "35000",
                                border: InputBorder.none,
                                hintStyle: TextStyle(color: Colors.grey),
                              ),
                            ),
                          ),
                          const Text("km", style: TextStyle(color: Colors.grey)),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),

                    // 연료 타입
                    const Text("연료", style: TextStyle(color: Colors.grey, fontSize: 12)),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        _buildChoiceChip("가솔린", isDark),
                        _buildChoiceChip("디젤", isDark),
                        _buildChoiceChip("LPG", isDark),
                        _buildChoiceChip("전기/하이브리드", isDark),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // 2. 상세 옵션 카드
              Container(
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
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          "상세 옵션 (선택)",
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: textColor,
                          ),
                        ),
                        Icon(Icons.keyboard_arrow_up, color: Colors.grey[600]),
                      ],
                    ),
                    const SizedBox(height: 20),

                    // 성능 점검 (별점)
                    const Text("성능 점검", style: TextStyle(color: Colors.grey, fontSize: 12)),
                    const SizedBox(height: 8),
                    Row(
                      children: List.generate(5, (index) {
                        return GestureDetector(
                          onTap: () => setState(() => _performanceRating = index + 1),
                          child: Icon(
                            Icons.star_rounded,
                            color: index < _performanceRating ? const Color(0xFFFFC107) : (isDark ? Colors.grey[700] : Colors.grey[200]),
                            size: 32,
                          ),
                        );
                      }),
                    ),
                    const SizedBox(height: 16),

                    // 무사고 여부
                    _buildCheckboxRow("무사고 여부", _isAccidentFree, (val) {
                      setState(() => _isAccidentFree = val ?? false);
                    }, textColor, borderColor),
                    const SizedBox(height: 16),

                    // 옵션 그리드
                    const Text("옵션", style: TextStyle(color: Colors.grey, fontSize: 12)),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Expanded(
                          child: Column(
                            children: [
                              _buildCheckboxRow("선루프", _hasSunroof, (v) => setState(() => _hasSunroof = v!), textColor, borderColor),
                              _buildCheckboxRow("가죽시트", _hasLeatherSeats, (v) => setState(() => _hasLeatherSeats = v!), textColor, borderColor),
                              _buildCheckboxRow("후방카메라", _hasRearCamera, (v) => setState(() => _hasRearCamera = v!), textColor, borderColor),
                            ],
                          ),
                        ),
                        Expanded(
                          child: Column(
                            children: [
                              _buildCheckboxRow("내비게이션", _hasNavigation, (v) => setState(() => _hasNavigation = v!), textColor, borderColor),
                              _buildCheckboxRow("스마트키", _hasSmartKey, (v) => setState(() => _hasSmartKey = v!), textColor, borderColor),
                              const SizedBox(height: 40), // Grid 높이 맞추기용
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),

                    // 지역 선택
                    const Text("지역", style: TextStyle(color: Colors.grey, fontSize: 12)),
                    const SizedBox(height: 8),
                    _buildDropdown(
                      hint: "서울/경기",
                      value: _selectedRegion,
                      items: ["서울/경기", "강원", "충청", "전라", "경상", "제주"],
                      onChanged: (val) => setState(() => _selectedRegion = val),
                      isDark: isDark,
                      textColor: textColor,
                      borderColor: borderColor,
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 32),

              // 검색하기 버튼
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _performSearch,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF0066FF),
                    disabledBackgroundColor: Colors.grey[400],
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    elevation: 0,
                  ),
                  child: _isLoading
                      ? const SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(
                            color: Colors.white,
                            strokeWidth: 2,
                          ),
                        )
                      : const Text(
                          "검색하기",
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                ),
              ),
              const SizedBox(height: 16),
              
              // 초기화 버튼
              Center(
                child: TextButton(
                  onPressed: () {
                    setState(() {
                      _selectedBrand = null;
                      _selectedModel = null;
                      _selectedYear = null;
                      _mileageController.clear();
                      _selectedFuel = '가솔린';
                      _performanceRating = 0;
                      _isAccidentFree = false;
                      _hasSunroof = false;
                      _hasNavigation = false;
                      _hasLeatherSeats = false;
                      _hasSmartKey = false;
                      _hasRearCamera = false;
                      _selectedRegion = null;
                    });
                  },
                  child: Text(
                    "초기화",
                    style: TextStyle(
                      color: textColor,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDropdown({
    required String hint,
    required String? value,
    required List<String> items,
    required Function(String?) onChanged,
    required bool isDark,
    required Color textColor,
    required Color borderColor,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        border: Border.all(color: borderColor),
        borderRadius: BorderRadius.circular(12),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: value,
          hint: Text(hint, style: TextStyle(color: Colors.grey[400], fontSize: 14)),
          isExpanded: true,
          icon: Icon(Icons.keyboard_arrow_down, color: Colors.grey[400]),
          dropdownColor: isDark ? const Color(0xFF2C2C2C) : Colors.white,
          style: TextStyle(color: textColor),
          items: items.map((String item) {
            return DropdownMenuItem<String>(
              value: item,
              child: Text(item),
            );
          }).toList(),
          onChanged: onChanged,
        ),
      ),
    );
  }

  Widget _buildChoiceChip(String label, bool isDark) {
    bool isSelected = _selectedFuel == label;
    // 다크모드일 때 선택되지 않은 칩의 배경색 조정
    Color unselectedColor = isDark ? const Color(0xFF2C2C2C) : const Color(0xFFEAF2FF);
    
    return GestureDetector(
      onTap: () => setState(() => _selectedFuel = label),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF0066FF) : unselectedColor,
          borderRadius: BorderRadius.circular(24),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: isSelected ? Colors.white : const Color(0xFF0066FF),
            fontWeight: FontWeight.bold,
            fontSize: 14,
          ),
        ),
      ),
    );
  }

  Widget _buildCheckboxRow(String label, bool value, Function(bool?) onChanged, Color textColor, Color borderColor) {
    return Row(
      children: [
        SizedBox(
          width: 24,
          height: 24,
          child: Checkbox(
            value: value,
            onChanged: onChanged,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
            activeColor: const Color(0xFF0066FF),
            side: BorderSide(color: Colors.grey[400]!),
          ),
        ),
        const SizedBox(width: 8),
        Text(label, style: TextStyle(fontSize: 14, color: textColor)),
      ],
    );
  }
  
  /// API 호출 및 검색 실행
  Future<void> _performSearch() async {
    // 유효성 검사
    if (_selectedBrand == null || _selectedModel == null) {
      _showError('브랜드와 모델을 선택해주세요');
      return;
    }
    
    final mileage = int.tryParse(_mileageController.text.replaceAll(',', ''));
    if (mileage == null || mileage < 0) {
      _showError('주행거리를 올바르게 입력해주세요');
      return;
    }
    
    // 연식 파싱
    int year = 2024;
    if (_selectedYear != null) {
      year = int.tryParse(_selectedYear!.replaceAll('년', '')) ?? 2024;
    }
    
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    
    try {
      // 연식에 따른 정확한 모델명 변환
      final backendModel = _getBackendModelName(_selectedBrand!, _selectedModel!, year);
      
      // 디버그: API 호출 전 파라미터 출력
      debugPrint('🚗 API 호출: brand=$_selectedBrand, model=$_selectedModel → $backendModel, year=$year, mileage=$mileage, fuel=$_selectedFuel');
      debugPrint('⚙️ 옵션: 선루프=$_hasSunroof, 내비=$_hasNavigation, 가죽시트=$_hasLeatherSeats, 스마트키=$_hasSmartKey, 후방카메라=$_hasRearCamera');
      debugPrint('🌐 API URL: ${_apiService.currentBaseUrl}');
      
      // 통합 분석 API 호출 (변환된 모델명 + 옵션 포함)
      final result = await _apiService.smartAnalysis(
        brand: _selectedBrand!,
        model: backendModel,  // 연식 기반 변환된 모델명
        year: year,
        mileage: mileage,
        fuel: _selectedFuel,
        // 옵션 전달
        hasSunroof: _hasSunroof,
        hasNavigation: _hasNavigation,
        hasLeatherSeat: _hasLeatherSeats,
        hasSmartKey: _hasSmartKey,
        hasRearCamera: _hasRearCamera,
      );
      
      // 디버그: API 응답 출력
      debugPrint('✅ API 응답: 예측가격=${result.prediction.predictedPrice}, 신뢰도=${result.prediction.confidence}');
      
      // 검색 이력 저장 (백그라운드)
      _apiService.saveSearchHistory(
        brand: _selectedBrand!,
        model: backendModel,
        year: year,
        mileage: mileage,
        predictedPrice: result.prediction.predictedPrice,
      );
      
      if (!mounted) return;
      
      // 결과 페이지로 이동
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => ResultPage(
            analysisResult: result,
            brand: _selectedBrand!,
            model: _selectedModel!,
            year: year,
            mileage: mileage,
            fuel: _selectedFuel,
          ),
        ),
      );
    } on ApiException catch (e) {
      _showError(e.message);
    } catch (e) {
      _showError('예상치 못한 오류가 발생했습니다');
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }
  
  /// 에러 메시지 표시
  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red[400],
        behavior: SnackBarBehavior.floating,
        action: SnackBarAction(
          label: '확인',
          textColor: Colors.white,
          onPressed: () {},
        ),
      ),
    );
  }
}
