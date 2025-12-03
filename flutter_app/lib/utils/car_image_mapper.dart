import '../config/environment.dart';

/// 차량 모델 이미지 매핑 유틸리티
/// ML 서버에서 이미지 제공 (APK 크기 최소화 + 실제 차량 이미지 사용)
/// 
/// ⚠️ 매핑 규칙: 이미지 파일명과 모델명이 정확히 일치하는 경우만 매핑
/// 대체 매핑 없음 - 이미지가 없으면 null 반환

class CarImageMapper {
  // ML 서버 이미지 베이스 URL (환경 설정에서 가져옴)
  static String get _baseUrl => Environment.imageServiceUrl;

  // 실제 존재하는 이미지 파일 목록 (113개 - 2024.12.02 기준)
  // 파일명과 정확히 일치하는 경우만 매핑됨
  static const Set<String> _existingImages = {
    // 기아
    'K3', 'K5', 'K7', 'K8', 'K9',
    'EV3', 'EV4', 'EV5', 'EV6', 'EV9', 'PV5',
    '모닝', '레이', '니로', '셀토스', '쏘렌토', '스토닉', '쏘울', '스팅어',
    '포르테', '카렌스', '프라이드', '스펙트라', '엔터프라이즈', '타스만',
    '카스타', '엘란', '비스토', '캐피탈',
    '그랜드 카니발', '카니발 II',
    // 현대
    '그랜저', '쏘나타', '아반떼', '투싼', '싼타페', '스타리아', '스타렉스',
    '아이오닉', '베리타스', '슈퍼살롱',
    '뉴 다마스', '다마스 II', '라보', '포텐샤', '에스페로', '스테이츠맨',
    // 제네시스
    'G70', 'G80', 'G90', 'G2X', 'GV60', 'GV70', 'GV80',
    // 르노코리아
    'SM3', 'SM5', 'SM6', 'SM7', 'QM3', 'QM5', 'QM6', 'XM3',
    '클리오', '조에', '캡처', '마스터', '그랑 콜레오스', '아르카나',
    // 쉐보레/GM
    '스파크', '크루즈', '말리부', '임팔라', '트랙스', '이쿼녹스',
    '트래버스', '볼트', '캡티바', '울란도', '토스카', '콜로라도',
    '타호', '아카디아', '카마로', '라세티 프리미어', '젠트라', '알페온',
    '마티즈 클래식', '아베오 세단', '아베오 해치백', '윈스톰', '크레도스', '리갈',
    // 쌍용/KG
    '티볼리', '토레스', '모하비', '액티언',
    '더 뉴 티볼리', '더 뉴 토레스', '티볼리 에어',
    '코란도 C', '뷰티풀 코란도', '더 뉴 코란도 스포츠',
    '렉스턴 II', '더 뉴 렉스턴 스포츠', '렉스턴 스포츠 칸',
    '뉴무쏘', '뉴체어맨', '로디우스 유로', '이스타나',
    // 기타
    '로체', '티코', '프레지오', '파크타운',
  };

  // 부분 매칭 키워드 → 이미지 파일명 매핑
  // (예: "그랜저 IG" → "그랜저", "더 뉴 K5" → "K5")
  // 이미지가 없는 모델은 같은 계열의 대표 사진으로 매핑
  static const Map<String, String> _partialToImage = {
    // 현대 (대표 사진 매핑 포함)
    '그랜저': '그랜저',
    '쏘나타': '쏘나타',
    '아반떼': '아반떼',
    '투싼': '투싼',
    '싼타페': '싼타페',
    '팰리세이드': '싼타페',  // 대형 SUV → 싼타페로 대표
    '코나': '투싼',  // 소형 SUV → 투싼으로 대표
    '캐스퍼': '모닝',  // 경차 → 모닝으로 대표
    '베뉴': '투싼',  // 소형 SUV → 투싼으로 대표
    '스타리아': '스타리아',
    '스타렉스': '스타렉스',
    '아이오닉': '아이오닉',
    '아이오닉5': '아이오닉',  // 전기차 → 아이오닉으로 대표
    '아이오닉6': '아이오닉',  // 전기차 → 아이오닉으로 대표
    '베리타스': '베리타스',
    '슈퍼살롱': '슈퍼살롱',
    '다마스': '뉴 다마스',
    '라보': '라보',
    '포텐샤': '포텐샤',
    // 기아 (대표 사진 매핑 포함)
    '쏘렌토': '쏘렌토',
    '카니발': '그랜드 카니발',  // 카니발 계열 → 그랜드 카니발로 대표
    '스포티지': '셀토스',  // 중형 SUV → 셀토스로 대표
    '모닝': '모닝',
    '레이': '레이',
    '니로': '니로',
    '셀토스': '셀토스',
    '스팅어': '스팅어',
    '스토닉': '스토닉',
    '쏘울': '쏘울',
    '포르테': '포르테',
    '카렌스': '카렌스',
    '프라이드': '프라이드',
    '타스만': '타스만',
    '엔터프라이즈': '엔터프라이즈',
    'K3': 'K3', 'K5': 'K5', 'K7': 'K7', 'K8': 'K8', 'K9': 'K9',
    'EV3': 'EV3', 'EV4': 'EV4', 'EV5': 'EV5', 'EV6': 'EV6', 'EV9': 'EV9', 'PV5': 'PV5',
    // 제네시스
    'G70': 'G70', 'G80': 'G80', 'G90': 'G90', 'G2X': 'G2X',
    'GV60': 'GV60', 'GV70': 'GV70', 'GV80': 'GV80',
    // 르노
    'SM3': 'SM3', 'SM5': 'SM5', 'SM6': 'SM6', 'SM7': 'SM7',
    'QM3': 'QM3', 'QM5': 'QM5', 'QM6': 'QM6', 'XM3': 'XM3',
    '클리오': '클리오', '조에': '조에', '캡처': '캡처', '마스터': '마스터',
    '아르카나': '아르카나', '콜레오스': '그랑 콜레오스',
    // 쉐보레
    '스파크': '스파크', '크루즈': '크루즈', '말리부': '말리부',
    '임팔라': '임팔라', '트랙스': '트랙스', '이쿼녹스': '이쿼녹스',
    '트래버스': '트래버스', '볼트': '볼트', '캡티바': '캡티바',
    '올란도': '울란도', '토스카': '토스카', '콜로라도': '콜로라도', '타호': '타호',
    '라세티': '라세티 프리미어', '젠트라': '젠트라', '알페온': '알페온',
    '마티즈': '마티즈 클래식', '아베오': '아베오 세단', '윈스톰': '윈스톰', '카마로': '카마로',
    // 쌍용/KG
    '티볼리': '티볼리', '토레스': '토레스', '모하비': '모하비', '액티언': '액티언',
    '코란도': '뷰티풀 코란도', '렉스턴': '렉스턴 II',
    '무쏘': '뉴무쏘', '체어맨': '뉴체어맨', '로디우스': '로디우스 유로', '이스타나': '이스타나',
    // 기타
    '로체': '로체', '티코': '티코', '프레지오': '프레지오',
    // BMW (대표 사진 없음 → null 반환)
    // 벤츠 (대표 사진 없음 → null 반환)
    // 아우디 (대표 사진 없음 → null 반환)
  };

  /// 모델명으로 이미지 URL 반환 (서버에서 제공)
  /// 
  /// 매핑 순서:
  /// 1. 정확한 파일명 일치 확인
  /// 2. 부분 매칭으로 이미지 찾기
  /// 3. 없으면 null 반환 (placeholder 표시)
  static String? getImageUrl(String model) {
    // 괄호 제거 및 정규화 (예: "그랜저 (GN7)" → "그랜저")
    final cleanModel = model.replaceAll(RegExp(r'\s*\([^)]*\)'), '').trim();
    
    String? imageName;
    String matchType = '';
    
    // 1. 정확한 파일명 일치 확인
    if (_existingImages.contains(cleanModel)) {
      imageName = cleanModel;
      matchType = 'exact';
    }
    // 2. 원본 모델명으로 확인
    else if (_existingImages.contains(model)) {
      imageName = model;
      matchType = 'exact-original';
    }
    // 3. 부분 매칭
    else {
      for (final entry in _partialToImage.entries) {
        if (cleanModel.contains(entry.key) || model.contains(entry.key)) {
          // 매핑된 이미지가 실제 존재하는지 확인
          if (_existingImages.contains(entry.value)) {
            imageName = entry.value;
            matchType = 'partial:${entry.key}';
            break;
          }
        }
      }
    }

    // 이미지가 없으면 null 반환
    if (imageName == null) {
      if (Environment.isDebug) {
        print('[CarImageMapper] ❌ model="$model" → clean="$cleanModel" → NO IMAGE');
      }
      return null;
    }
    
    final resultUrl = '$_baseUrl/${Uri.encodeComponent(imageName)}.png';
    
    // 디버그 로그 (개발 환경에서만)
    if (Environment.isDebug) {
      print('[CarImageMapper] ✅ model="$model" → clean="$cleanModel" → $matchType → $imageName');
    }
    
    return resultUrl;
  }

  /// 브랜드와 모델명으로 이미지 URL 반환
  static String? getImageUrlByBrandModel(String brand, String model) {
    return getImageUrl(model);
  }

  /// 이미지가 있는지 확인
  static bool hasImage(String model) {
    final cleanModel = model.replaceAll(RegExp(r'\s*\([^)]*\)'), '').trim();
    
    // 정확한 매칭
    if (_existingImages.contains(cleanModel) || _existingImages.contains(model)) {
      return true;
    }
    
    // 부분 매칭
    for (final entry in _partialToImage.entries) {
      if ((cleanModel.contains(entry.key) || model.contains(entry.key)) &&
          _existingImages.contains(entry.value)) {
        return true;
      }
    }
    
    return false;
  }

  /// 이미지 없는 모델 목록 반환 (디버그용)
  /// 대표 사진으로 매핑된 모델은 제외
  static List<String> getMissingImageModels() {
    return [
      // 외제차 (대표 사진 없음)
      // BMW
      '3시리즈', '5시리즈', '7시리즈', 'X3', 'X5', 'X7',
      // 벤츠
      'A-클래스', 'C-클래스', 'E-클래스', 'S-클래스', 'GLC', 'GLE', 'GLS',
      // 아우디
      'A4', 'A6', 'A8', 'Q3', 'Q5', 'Q7', 'Q8',
    ];
  }
}
