/// 차량 모델명 매핑 유틸리티
/// 
/// 사용자에게 보여주는 간단한 모델명을 백엔드에서 사용하는 
/// 정확한 모델명으로 변환합니다.
/// 
/// 예: 그랜저 (2024년) → 그랜저 (GN7)
///     E-클래스 (2020년) → E-클래스 W213
library;

/// 브랜드별 사용자용 모델 목록
const Map<String, List<String>> brandModels = {
  '현대': ['아반떼', '쏘나타', '그랜저', '투싼', '싼타페', '팰리세이드', '스타리아'],
  '기아': ['모닝', '레이', 'K3', 'K5', 'K8', 'K9', '셀토스', '스포티지', '쏘렌토', '카니발', 'EV6', 'EV9'],
  '제네시스': ['G70', 'G80', 'G90', 'GV60', 'GV70', 'GV80'],
  'BMW': ['3시리즈', '5시리즈', '7시리즈', 'X3', 'X5', 'X7'],
  '벤츠': ['C-클래스', 'E-클래스', 'S-클래스', 'GLC', 'GLE', 'GLS'],
  '아우디': ['A4', 'A6', 'A8', 'Q3', 'Q5', 'Q7', 'Q8'],
};

/// 연식에 따른 백엔드 모델명 변환
/// 
/// [brand] 브랜드명
/// [model] 사용자용 간단 모델명
/// [year] 연식
/// 
/// Returns: 백엔드에서 사용하는 정확한 모델명
String getBackendModelName(String brand, String model, int year) {
  // 현대
  if (brand == '현대') {
    return _getHyundaiModel(model, year);
  }
  // 기아
  if (brand == '기아') {
    return _getKiaModel(model, year);
  }
  // 제네시스
  if (brand == '제네시스') {
    return _getGenesisModel(model, year);
  }
  // BMW
  if (brand == 'BMW') {
    return _getBmwModel(model, year);
  }
  // 벤츠
  if (brand == '벤츠') {
    return _getMercedesModel(model, year);
  }
  // 아우디
  if (brand == '아우디') {
    return _getAudiModel(model, year);
  }
  // 기본: 모델명 그대로 반환
  return model;
}

String _getHyundaiModel(String model, int year) {
  switch (model) {
    case '아반떼':
      if (year >= 2021) return '아반떼 (CN7)';
      if (year >= 2016) return '아반떼 AD';
      return '아반떼 MD';
    case '쏘나타':
      if (year >= 2024) return '쏘나타 디 엣지(DN8)';
      if (year >= 2020) return '쏘나타 (DN8)';
      if (year >= 2015) return 'LF 쏘나타';
      return 'YF 쏘나타';
    case '그랜저':
      if (year >= 2023) return '그랜저 (GN7)';
      if (year >= 2020) return '더 뉴 그랜저 IG';
      if (year >= 2017) return '그랜저 IG';
      return '그랜저 HG';
    case '투싼':
      if (year >= 2024) return '더 뉴 투싼 (NX4)';
      if (year >= 2021) return '투싼 (NX4)';
      return '올 뉴 투싼';
    case '싼타페':
      if (year >= 2024) return '싼타페 (MX5)';
      if (year >= 2019) return '싼타페 TM';
      return '싼타페 DM';
    case '팰리세이드':
      if (year >= 2023) return '더 뉴 팰리세이드';
      return '팰리세이드';
    case '스타리아':
      return '스타리아';
    default:
      return model;
  }
}

String _getKiaModel(String model, int year) {
  switch (model) {
    case 'K5':
      if (year >= 2024) return '더 뉴 K5 (DL3)';
      if (year >= 2020) return 'K5 (DL3)';
      return 'K5';
    case '스포티지':
      if (year >= 2024) return '더 뉴 스포티지 (NQ5)';
      if (year >= 2022) return '스포티지 (NQ5)';
      return '스포티지';
    case '쏘렌토':
      if (year >= 2024) return '더 뉴 쏘렌토 (MQ4)';
      if (year >= 2020) return '쏘렌토 (MQ4)';
      return '쏘렌토';
    case '카니발':
      if (year >= 2024) return '더 뉴 카니발 (KA4)';
      if (year >= 2021) return '카니발 (KA4)';
      return '카니발';
    case 'K9':
      if (year >= 2022) return '더 뉴 K9 2세대';
      if (year >= 2018) return '더 K9';
      return 'K9';
    case 'K8':
      if (year >= 2024) return '더 뉴 K8';
      return 'K8';
    case 'K3':
      if (year >= 2022) return '더 뉴 K3 (BD)';
      if (year >= 2019) return 'K3 (BD)';
      return 'K3';
    case 'EV6':
      return 'EV6';
    case 'EV9':
      return 'EV9';
    case '셀토스':
      if (year >= 2023) return '더 뉴 셀토스';
      return '셀토스';
    case '모닝':
      if (year >= 2020) return '더 뉴 모닝';
      return '올 뉴 모닝';
    case '레이':
      if (year >= 2022) return '더 뉴 레이';
      return '레이';
    default:
      return model;
  }
}

String _getGenesisModel(String model, int year) {
  switch (model) {
    case 'G70':
      if (year >= 2024) return 'G70 (IK F/L)';
      return 'G70 (IK)';
    case 'G80':
      if (year >= 2024) return 'G80 (RG3 F/L)';
      if (year >= 2020) return 'G80 (RG3)';
      return 'EQ900';
    case 'G90':
      if (year >= 2022) return 'G90 (RS4)';
      return 'EQ900';
    case 'GV60':
      return 'GV60';
    case 'GV70':
      if (year >= 2024) return 'GV70 (JK1 F/L)';
      return 'GV70 (JK1)';
    case 'GV80':
      if (year >= 2024) return 'GV80 (JX1 F/L)';
      return 'GV80 (JX1)';
    default:
      return model;
  }
}

String _getBmwModel(String model, int year) {
  switch (model) {
    case '3시리즈':
      if (year >= 2019) return '3시리즈 (G20)';
      if (year >= 2012) return '3시리즈 (F30)';
      return '3시리즈 (E90)';
    case '5시리즈':
      if (year >= 2024) return '5시리즈 (G60)';
      if (year >= 2017) return '5시리즈 (G30)';
      if (year >= 2010) return '5시리즈 (F10)';
      return '5시리즈 (E60)';
    case '7시리즈':
      if (year >= 2023) return '7시리즈 (G70)';
      if (year >= 2016) return '7시리즈 (G11)';
      return '7시리즈 (F01)';
    case 'X3':
      if (year >= 2018) return 'X3 (G01)';
      return 'X3 (F25)';
    case 'X5':
      if (year >= 2019) return 'X5 (G05)';
      if (year >= 2014) return 'X5 (F15)';
      return 'X5';
    case 'X7':
      return 'X7 (G07)';
    default:
      return model;
  }
}

String _getMercedesModel(String model, int year) {
  switch (model) {
    case 'C-클래스':
      if (year >= 2022) return 'C-클래스 W206';
      if (year >= 2014) return 'C-클래스 W205';
      return 'C-클래스 W204';
    case 'E-클래스':
      if (year >= 2024) return 'E-클래스 W214';
      if (year >= 2016) return 'E-클래스 W213';
      if (year >= 2010) return 'E-클래스 W212';
      return 'E-클래스 W211';
    case 'S-클래스':
      if (year >= 2021) return 'S-클래스 W223';
      if (year >= 2014) return 'S-클래스 W222';
      return 'S-클래스 W221';
    case 'GLC':
      if (year >= 2023) return 'GLC-클래스 X254';
      return 'GLC-클래스 X253';
    case 'GLE':
      if (year >= 2019) return 'GLE-클래스 V167';
      return 'GLE-클래스 W166';
    case 'GLS':
      if (year >= 2020) return 'GLS-클래스 X167';
      return 'GLS-클래스 X166';
    default:
      return model;
  }
}

String _getAudiModel(String model, int year) {
  switch (model) {
    case 'A4':
      if (year >= 2020) return '뉴 A4';
      return 'A4 (B9)';
    case 'A6':
      if (year >= 2019) return '뉴 A6';
      return 'A6 (C8)';
    case 'A8':
      if (year >= 2018) return '뉴 A8';
      return 'A8 (D5)';
    case 'Q3':
      if (year >= 2019) return '뉴 Q3';
      return 'Q3';
    case 'Q5':
      if (year >= 2021) return '뉴 Q5';
      return 'Q5 (FY)';
    case 'Q7':
      if (year >= 2020) return '뉴 Q7';
      return 'Q7 (4M)';
    case 'Q8':
      return 'Q8';
    default:
      return model;
  }
}
