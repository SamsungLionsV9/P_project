import 'package:flutter/material.dart';
import '../config/environment.dart';

/// 차량 모델 이미지 매핑 유틸리티
/// ML 서버에서 이미지 제공 (APK 크기 최소화 + 실제 차량 이미지 사용)
/// 
/// ⚠️ 매핑 규칙: 이미지 파일명과 모델명이 정확히 일치하는 경우만 매핑
/// 대체 매핑 없음 - 이미지가 없으면 null 반환

class CarImageMapper {
  // ML 서버 이미지 베이스 URL (환경 설정에서 가져옴)
  static String get _baseUrl => Environment.imageServiceUrl;

  // 실제 존재하는 이미지 파일 목록 (237개 - 2024.12.03 기준)
  // 파일명과 정확히 일치하는 경우만 매핑됨
  // Map<파일명(확장자 제외), 확장자>
  static const Map<String, String> _existingImages = {
    // === 국산차 (PNG) ===
    // 기아
    'K3': 'png', 'K5': 'png', 'K7': 'png', 'K8': 'png', 'K9': 'png',
    'EV3': 'png', 'EV4': 'png', 'EV5': 'png', 'EV6': 'png', 'EV9': 'png', 'PV5': 'png',
    '모닝': 'png', '레이': 'png', '니로': 'png', '셀토스': 'png', '쏘렌토': 'png', '스토닉': 'png', '쏘울': 'png', '스팅어': 'png',
    '포르테': 'png', '카렌스': 'png', '프라이드': 'png', '스펙트라': 'png', '엔터프라이즈': 'png', '타스만': 'png',
    '카스타': 'png', '엘란': 'png', '비스토': 'png', '캐피탈': 'png',
    '그랜드 카니발': 'png', '카니발 II': 'png',
    // 현대
    '그랜저': 'png', '쏘나타': 'png', '아반떼': 'png', '투싼': 'png', '싼타페': 'png', '스타리아': 'png', '스타렉스': 'png',
    '아이오닉': 'png', '베리타스': 'png', '슈퍼살롱': 'png',
    '뉴 다마스': 'png', '다마스 II': 'png', '라보': 'png', '포텐샤': 'png', '에스페로': 'png', '스테이츠맨': 'png',
    // 제네시스
    'G70': 'png', 'G80': 'png', 'G90': 'png', 'G2X': 'png', 'GV60': 'png', 'GV70': 'png', 'GV80': 'png',
    // 르노코리아
    'SM3': 'png', 'SM5': 'png', 'SM6': 'png', 'SM7': 'png', 'QM3': 'png', 'QM5': 'png', 'QM6': 'png', 'XM3': 'png',
    '클리오': 'png', '조에': 'png', '캡처': 'png', '마스터': 'png', '그랑 콜레오스': 'png', '아르카나': 'png',
    // 쉐보레/GM
    '스파크': 'png', '크루즈': 'png', '말리부': 'png', '임팔라': 'png', '트랙스': 'png', '이쿼녹스': 'png',
    '트래버스': 'png', '볼트': 'png', '캡티바': 'png', '울란도': 'png', '토스카': 'png', '콜로라도': 'png',
    '타호': 'png', '아카디아': 'png', '카마로': 'png', '라세티 프리미어': 'png', '젠트라': 'png', '알페온': 'png',
    '마티즈 클래식': 'png', '아베오 세단': 'png', '아베오 해치백': 'png', '윈스톰': 'png', '크레도스': 'png', '리갈': 'png',
    // 쌍용/KG
    '티볼리': 'png', '토레스': 'png', '모하비': 'png', '액티언': 'png',
    '더 뉴 티볼리': 'png', '더 뉴 토레스': 'png', '티볼리 에어': 'png',
    '코란도 C': 'png', '뷰티풀 코란도': 'png', '더 뉴 코란도 스포츠': 'png',
    '렉스턴 II': 'png', '더 뉴 렉스턴 스포츠': 'png', '렉스턴 스포츠 칸': 'png',
    '뉴무쏘': 'png', '뉴체어맨': 'png', '로디우스 유로': 'png', '이스타나': 'png',
    // 기타 국산
    '로체': 'png', '티코': 'png', '프레지오': 'png', '파크타운': 'png',

    // === 외제차 (PNG) ===
    // 포르쉐
    '911': 'png', '박스터': 'png', '카이맨': 'png', '카이엔': 'png', '마칸': 'png', '파나메라': 'png', '타이칸': 'png',
    // 메르세데스-벤츠
    'A-클래스': 'png', 'C-클래스': 'png', 'E-클래스': 'png', 'S-클래스': 'png',
    'GLC': 'png', 'GLE': 'png', 'GLS': 'png', 'AMG GT': 'png',
    // BMW
    'BMW 3시리즈': 'png', 'BMW 5시리즈': 'png', 'BMW 7시리즈': 'png',
    'X3': 'png', 'X5': 'png', 'X6': 'png', 'X7': 'png',
    'i3': 'png', 'i4': 'png', 'i5': 'png', 'i7': 'png', 'iX1': 'png', 'iX3': 'png',
    // 아우디
    'A4': 'png', 'A6': 'png', 'A7': 'png', 'A8': 'png',
    'Q5': 'png', 'Q7': 'png', 'Q8': 'png', 'E-트론': 'png',
    // 렉서스
    'ES': 'png', 'LM': 'png', 'NX': 'png', 'RX': 'png', 'UX': 'png',
    // 재규어
    'F-PACE': 'png', 'F-TYPE': 'png', 'XE': 'png', 'XF': 'png', 'XJ': 'png',
    // 랜드로버
    '디스커버리': 'png', '디펜더': 'png', '레인지로버': 'png', '벨라': 'png', '이보크': 'png',
    // 볼보
    'S90': 'png', 'V60': 'png', 'XC40': 'png', 'XC60': 'png', 'XC90': 'png',
    // 폭스바겐
    '골프': 'png', '아테온': 'png', '제타': 'png', '티구안': 'png', '파사트': 'png', 'ID': 'png',
    // 토요타
    '캠리': 'png', '프리우스': 'png', '시에나': 'png', '알파드': 'png', 'RAV4': 'png',
    // 혼다
    '시빅': 'png', '어코드': 'png', '오딧세이': 'png', 'CR-V': 'png', '파일럿': 'png',
    // 닛산
    '알티마': 'png', '맥시마': 'png', '무라노': 'png', '패스파인더': 'png',
    // 인피니티
    'Q30': 'png', 'Q50': 'png', 'QX60': 'png',
    // 미니
    '미니쿠퍼': 'png',

    // === 럭셔리 브랜드 (JPG) ===
    // 람보르기니
    '람보르기니 아벤타도르': 'jpg', '람보르기니 우라칸': 'jpg', '람보르기니 우루스': 'jpg',
    // 롤스로이스
    '롤스로이스 고스트': 'jpg', '롤스로이스 컬리넌': 'jpg', '롤스로이스 팬텀': 'jpg',
    // 링컨
    '링컨 네비게이터': 'jpg', '링컨 노틸러스': 'jpg', '링컨 에비에이터': 'jpg',
    // 마세라티
    '마세라티 기블리': 'jpg', '마세라티 르반떼': 'jpg', '마세라티 콰트로포르테': 'jpg',
    // 벤틀리
    '벤틀리 벤테이가': 'jpg', '벤틀리 컨티넨탈 GT': 'jpg', '벤틀리 플라잉스퍼': 'jpg',
    // 지프
    '지프 그랜드 체로키': 'jpg', '지프 랭글러': 'jpg', '지프 레니게이드': 'jpg', '지프 체로키': 'jpg',
    // 캐딜락
    '캐딜락 CT6': 'jpg', '캐딜락 XT5': 'jpg', '캐딜락 에스컬레이드': 'jpg',
    // 테슬라
    '테슬라 모델3': 'jpg', '테슬라 모델S': 'jpg', '테슬라 모델X': 'jpg', '테슬라 모델Y': 'png',
    // 페라리
    '페라리 296': 'jpg', '페라리 488': 'jpg', '페라리 F8': 'jpg', '페라리 SF90': 'jpg', '페라리 로마': 'jpg',
    // 포드
    '포드 F150': 'jpg', '포드 머스탱': 'jpg', '포드 브롱코': 'jpg', '포드 익스플로러': 'jpg',
    // 폴스타
    '폴스타2': 'jpg', '폴스타4': 'jpg',
    // 푸조
    '푸조 208': 'jpg', '푸조 3008': 'jpg', '푸조 5008': 'jpg', '푸조 508': 'jpg',
    // 피아트
    '피아트 500': 'jpg',
  };

  // 부분 매칭 키워드 → 이미지 파일명 매핑
  // (예: "그랜저 IG" → "그랜저", "더 뉴 K5" → "K5")
  // 이미지가 없는 모델은 같은 계열의 대표 사진으로 매핑
  static const Map<String, String> _partialToImage = {
    // === 국산차 ===
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
    // 기타 국산
    '로체': '로체', '티코': '티코', '프레지오': '프레지오',

    // === 외제차 ===
    // 포르쉐
    '911': '911', '박스터': '박스터', '카이맨': '카이맨', '카이엔': '카이엔',
    '마칸': '마칸', '파나메라': '파나메라', '타이칸': '타이칸',
    // 메르세데스-벤츠
    'A클래스': 'A-클래스', 'C클래스': 'C-클래스', 'E클래스': 'E-클래스', 'S클래스': 'S-클래스',
    'A-클래스': 'A-클래스', 'C-클래스': 'C-클래스', 'E-클래스': 'E-클래스', 'S-클래스': 'S-클래스',
    'GLC': 'GLC', 'GLE': 'GLE', 'GLS': 'GLS', 'AMG': 'AMG GT',
    // BMW
    '3시리즈': 'BMW 3시리즈', '5시리즈': 'BMW 5시리즈', '7시리즈': 'BMW 7시리즈',
    'X3': 'X3', 'X5': 'X5', 'X6': 'X6', 'X7': 'X7',
    'i3': 'i3', 'i4': 'i4', 'i5': 'i5', 'i7': 'i7', 'iX1': 'iX1', 'iX3': 'iX3', 'iX': 'iX3',
    // 아우디
    'A4': 'A4', 'A6': 'A6', 'A7': 'A7', 'A8': 'A8',
    'Q5': 'Q5', 'Q7': 'Q7', 'Q8': 'Q8', 'e-tron': 'E-트론', 'E-트론': 'E-트론', 'e트론': 'E-트론',
    // 렉서스
    'ES': 'ES', 'LM': 'LM', 'NX': 'NX', 'RX': 'RX', 'UX': 'UX',
    'LS': 'ES', 'IS': 'ES', 'LC': 'ES', 'RC': 'ES', // 렉서스 세단 계열 → ES로 대표
    // 재규어
    'F-PACE': 'F-PACE', 'F-TYPE': 'F-TYPE', 'XE': 'XE', 'XF': 'XF', 'XJ': 'XJ',
    // 랜드로버
    '디스커버리': '디스커버리', '디펜더': '디펜더', '레인지로버': '레인지로버',
    '벨라': '벨라', '이보크': '이보크', '베라': '벨라',
    // 볼보
    'S90': 'S90', 'V60': 'V60', 'XC40': 'XC40', 'XC60': 'XC60', 'XC90': 'XC90',
    'S60': 'S90', 'V90': 'V60', // 볼보 세단/왜건 계열 대표
    // 폭스바겐
    '골프': '골프', '아테온': '아테온', '제타': '제타', '티구안': '티구안', '파사트': '파사트',
    'ID.4': 'ID', 'ID.3': 'ID', 'ID': 'ID',
    // 토요타
    '캠리': '캠리', '프리우스': '프리우스', '시에나': '시에나', '알파드': '알파드', 'RAV4': 'RAV4',
    '라브4': 'RAV4', '하이랜더': '시에나', // 토요타 대형 → 시에나로 대표
    // 혼다
    '시빅': '시빅', '어코드': '어코드', '오딧세이': '오딧세이', 'CR-V': 'CR-V', '파일럿': '파일럿',
    'CRV': 'CR-V',
    // 닛산
    '알티마': '알티마', '맥시마': '맥시마', '무라노': '무라노', '패스파인더': '패스파인더',
    '센트라': '알티마', // 닛산 세단 계열 → 알티마로 대표
    // 인피니티
    'Q30': 'Q30', 'Q50': 'Q50', 'QX60': 'QX60',
    'QX50': 'QX60', 'QX80': 'QX60', // 인피니티 SUV → QX60로 대표
    // 미니
    '미니쿠퍼': '미니쿠퍼', '미니': '미니쿠퍼', 'MINI': '미니쿠퍼',

    // === 럭셔리 브랜드 ===
    // 람보르기니
    '아벤타도르': '람보르기니 아벤타도르', '우라칸': '람보르기니 우라칸', '우루스': '람보르기니 우루스',
    // 롤스로이스
    '고스트': '롤스로이스 고스트', '컬리넌': '롤스로이스 컬리넌', '팬텀': '롤스로이스 팬텀',
    // 링컨
    '네비게이터': '링컨 네비게이터', '노틸러스': '링컨 노틸러스', '에비에이터': '링컨 에비에이터',
    // 마세라티
    '기블리': '마세라티 기블리', '르반떼': '마세라티 르반떼', '콰트로포르테': '마세라티 콰트로포르테',
    // 벤틀리
    '벤테이가': '벤틀리 벤테이가', '컨티넨탈': '벤틀리 컨티넨탈 GT', '플라잉스퍼': '벤틀리 플라잉스퍼',
    // 지프
    '그랜드 체로키': '지프 그랜드 체로키', '랭글러': '지프 랭글러', '레니게이드': '지프 레니게이드', '체로키': '지프 체로키',
    // 캐딜락
    'CT6': '캐딜락 CT6', 'XT5': '캐딜락 XT5', '에스컬레이드': '캐딜락 에스컬레이드',
    'CT5': '캐딜락 CT6', 'CT4': '캐딜락 CT6', 'XT4': '캐딜락 XT5', 'XT6': '캐딜락 XT5',
    // 테슬라
    '모델3': '테슬라 모델3', '모델S': '테슬라 모델S', '모델X': '테슬라 모델X', '모델Y': '테슬라 모델Y',
    '모델 3': '테슬라 모델3', '모델 S': '테슬라 모델S', '모델 X': '테슬라 모델X', '모델 Y': '테슬라 모델Y',  // 공백 포함 버전
    'Model3': '테슬라 모델3', 'ModelS': '테슬라 모델S', 'ModelX': '테슬라 모델X', 'ModelY': '테슬라 모델Y',
    'Model 3': '테슬라 모델3', 'Model S': '테슬라 모델S', 'Model X': '테슬라 모델X', 'Model Y': '테슬라 모델Y',
    // 페라리
    '296': '페라리 296', '488': '페라리 488', 'F8': '페라리 F8', 'SF90': '페라리 SF90', '로마': '페라리 로마',
    '포르토피노': '페라리 로마', '812': '페라리 F8', // 페라리 대표 모델로 매핑
    // 포드
    'F150': '포드 F150', 'F-150': '포드 F150', '머스탱': '포드 머스탱', '브롱코': '포드 브롱코', '익스플로러': '포드 익스플로러',
    '머스탱 마하-E': '포드 머스탱', '에스케이프': '포드 익스플로러',
    // 폴스타
    '폴스타': '폴스타2', '폴스타2': '폴스타2', '폴스타4': '폴스타4',
    'Polestar': '폴스타2', 'Polestar 2': '폴스타2', 'Polestar 4': '폴스타4',
    // 푸조
    '208': '푸조 208', '3008': '푸조 3008', '5008': '푸조 5008', '508': '푸조 508',
    '2008': '푸조 208', '308': '푸조 508', // 푸조 계열 대표로 매핑
    // 피아트
    '500': '피아트 500', '500e': '피아트 500',
    
    // === 추가 대체 매핑 ===
    // 미니 쿠퍼 시리즈 (모든 변형 → 미니쿠퍼)
    '쿠퍼': '미니쿠퍼', '쿠퍼 S': '미니쿠퍼', '쿠퍼 D': '미니쿠퍼', '쿠퍼 SD': '미니쿠퍼',
    '쿠퍼 일렉트릭': '미니쿠퍼', '쿠퍼 컨버터블': '미니쿠퍼', '쿠퍼 컨트리맨': '미니쿠퍼',
    '쿠퍼 클럽맨': '미니쿠퍼', '쿠퍼 쿠페': '미니쿠퍼', '쿠퍼 로드스터': '미니쿠퍼',
    '쿠퍼 페이스맨': '미니쿠퍼',
    
    // 롤스로이스 추가
    '던': '롤스로이스 고스트', '스펙터': '롤스로이스 팬텀', '레이스': '롤스로이스 고스트',
    
    // 람보르기니 추가
    '가야르도': '람보르기니 우라칸',
    
    // 벤틀리 추가
    '뮬산': '벤틀리 플라잉스퍼',
    
    // 마세라티 추가
    '그란투리스모': '마세라티 기블리', '그란카브리오': '마세라티 기블리', '그레칼레': '마세라티 르반떼',
    
    // 지프 추가
    '컴패스': '지프 레니게이드', '글래디에이터': '지프 랭글러',
    
    // 현대/기아 누락 모델 대표 매핑
    '넥쏘': '아이오닉', '에쿠스': '그랜저', '제네시스 쿠페': 'G70',
    '벨로스터': 'K5', '아슬란': '그랜저', 'i30': '아반떼', 'i40': '쏘나타',
    
    // 페라리 추가
    '458': '페라리 488', 'F430': '페라리 488', '360': '페라리 488',
    '512': '페라리 488', 'F12': '페라리 SF90',
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
    String? extension;
    String matchType = '';
    
    // 1. 정확한 파일명 일치 확인
    if (_existingImages.containsKey(cleanModel)) {
      imageName = cleanModel;
      extension = _existingImages[cleanModel];
      matchType = 'exact';
    }
    // 2. 원본 모델명으로 확인
    else if (_existingImages.containsKey(model)) {
      imageName = model;
      extension = _existingImages[model];
      matchType = 'exact-original';
    }
    // 3. 부분 매칭
    else {
      for (final entry in _partialToImage.entries) {
        if (cleanModel.contains(entry.key) || model.contains(entry.key)) {
          // 매핑된 이미지가 실제 존재하는지 확인
          if (_existingImages.containsKey(entry.value)) {
            imageName = entry.value;
            extension = _existingImages[entry.value];
            matchType = 'partial:${entry.key}';
            break;
          }
        }
      }
    }

    // 이미지가 없으면 null 반환
    if (imageName == null || extension == null) {
      if (Environment.isDebug) {
        print('[CarImageMapper] ❌ model="$model" → clean="$cleanModel" → NO IMAGE');
      }
      return null;
    }
    
    final resultUrl = '$_baseUrl/${Uri.encodeComponent(imageName)}.$extension';
    
    // 디버그 로그 (개발 환경에서만)
    if (Environment.isDebug) {
      print('[CarImageMapper] ✅ model="$model" → clean="$cleanModel" → $matchType → $imageName.$extension');
    }
    
    return resultUrl;
  }

  /// 브랜드와 모델명으로 이미지 URL 반환
  static String? getImageUrlByBrandModel(String brand, String model) {
    // 브랜드명 + 모델명으로 먼저 시도
    final brandModel = '$brand $model';
    final brandModelUrl = getImageUrl(brandModel);
    if (brandModelUrl != null) return brandModelUrl;
    
    // 모델명만으로 시도
    return getImageUrl(model);
  }

  /// 이미지가 있는지 확인
  static bool hasImage(String model) {
    final cleanModel = model.replaceAll(RegExp(r'\s*\([^)]*\)'), '').trim();
    
    // 정확한 매칭
    if (_existingImages.containsKey(cleanModel) || _existingImages.containsKey(model)) {
      return true;
    }
    
    // 부분 매칭
    for (final entry in _partialToImage.entries) {
      if ((cleanModel.contains(entry.key) || model.contains(entry.key)) &&
          _existingImages.containsKey(entry.value)) {
        return true;
      }
    }
    
    return false;
  }

  /// 총 이미지 수 반환
  static int get totalImageCount => _existingImages.length;

  /// 이미지 없는 모델 목록 반환 (디버그용)
  /// 실제 데이터에서 많이 사용되지만 이미지가 없는 주요 모델들
  static List<String> getMissingImageModels() {
    return [
      // === 현대 ===
      '캐스퍼', '팰리세이드', '제네시스 DH', '코나', '에쿠스', '넥쏘', '베뉴', '엑센트',
      
      // === 기아 ===
      '카니발 4세대', '올 뉴 카니발', '더 뉴 카니발', '스포티지 5세대', '스포티지 4세대',
      
      // === BMW ===
      '5시리즈 (G30)', '3시리즈 (G20)', '7시리즈 (G11)', 'X4', '6시리즈 GT', '4시리즈', 'M 시리즈', 'Z4',
      
      // === 벤츠 ===
      'GLB-클래스', 'G-클래스', 'EQB', 'EQE', 'EQS', 'EQA', '스프린터',
      
      // === 아우디 ===
      'Q3', 'A5', 'A3', 'Q4 e-트론', 'R8', 'RS 시리즈',
      
      // === 테슬라 ===
      // 주의: 데이터는 "모델 3", "모델 Y"로 되어 있지만 이미지는 "테슬라 모델3", "테슬라 모델Y"로 있음
      // 부분 매칭으로 처리됨
      
      // === 미니 ===
      '쿠퍼 S', '쿠퍼 컨트리맨', '쿠퍼 클럽맨', '쿠퍼 컨버터블',
      
      // === 지프 ===
      '랭글러 (JL)', '랭글러 (JK)', '체로키(KL)', '글래디에이터', '컴패스',
      
      // === 포드 ===
      '익스플로러 6세대', '레인저', '머스탱 7세대', '익스페디션', '몬데오',
      
      // === 제네시스 ===
      'EQ900',
      
      // === KG모빌리티 ===
      'G4 렉스턴', '코란도 투리스모', '렉스턴 W',
      
      // === 쉐보레 ===
      '올란도',
      
      // === 렉서스 ===
      'CT200h', 'LS500h', 'LS460', 'IS250',
      
      // === 링컨 ===
      '에비에이터 2세대', '뉴 MKZ', '노틸러스 1세대', '컨티넨탈',
      
      // === 볼보 ===
      'S60', 'V90 크로스컨트리', 'C40 리차지', 'V40',
      
      // === 폭스바겐 ===
      '뉴 CC', '투아렉', '폴로', '시로코', '티록',
      
      // === 푸조 ===
      '3008 2세대', '5008 2세대', '2008', '308 2세대',
      
      // === 페라리 ===
      '296 GTS', '포르토피노', 'F8 스파이더', '296 GTB', '488 스파이더',
      
      // === 롤스로이스 ===
      '고스트 2세대', '던', '스펙터',
      
      // === 벤틀리 ===
      '컨티넨탈 GT 3세대', '플라잉스퍼 3세대',
      
      // === 기타 희귀 모델들 ===
      '람보르기니 가야르도', '맥라렌 570S', '애스턴마틴 밴티지',
    ];
  }
}

/// 차량 이미지 위젯
/// CarImageMapper를 사용하여 이미지를 표시하고, 없으면 placeholder를 표시
class CarImageWidget extends StatelessWidget {
  final String model;
  final String? imageUrl;
  final double? width;
  final double? height;
  final BoxFit fit;
  final Color? placeholderColor;
  final double iconSize;

  const CarImageWidget({
    super.key,
    required this.model,
    this.imageUrl,
    this.width,
    this.height,
    this.fit = BoxFit.contain,
    this.placeholderColor,
    this.iconSize = 60,
  });

  @override
  Widget build(BuildContext context) {
    final url = imageUrl ?? CarImageMapper.getImageUrl(model);
    final bgColor = placeholderColor ?? const Color(0xFF3D3D3D);

    if (url != null && url.isNotEmpty) {
      return Image.network(
        url,
        fit: fit,
        width: width,
        height: height,
        errorBuilder: (context, error, stackTrace) {
          return _buildPlaceholder(bgColor);
        },
        loadingBuilder: (context, child, loadingProgress) {
          if (loadingProgress == null) return child;
          return Container(
            width: width,
            height: height,
            color: bgColor,
            child: Center(
              child: CircularProgressIndicator(
                value: loadingProgress.expectedTotalBytes != null
                    ? loadingProgress.cumulativeBytesLoaded /
                        loadingProgress.expectedTotalBytes!
                    : null,
                color: Colors.white54,
                strokeWidth: 2,
              ),
            ),
          );
        },
      );
    }

    return _buildPlaceholder(bgColor);
  }

  Widget _buildPlaceholder(Color bgColor) {
    return Container(
      width: width,
      height: height,
      color: bgColor,
      child: Icon(
        Icons.directions_car,
        size: iconSize,
        color: Colors.white.withOpacity(0.3),
      ),
    );
  }
}
