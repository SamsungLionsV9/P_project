"""
Car Image Service - 차량 이미지 매핑
====================================
브랜드/모델별 대표 이미지 URL 관리
- 로컬 이미지 파일 사용 (235개 차량 이미지)
- 모델명 유사도 기반 이미지 검색
"""

from typing import Dict, Optional

class CarImageService:
    """차량 이미지 매핑 서비스"""
    
    # 브랜드별 로고 이미지 (Wikimedia Commons CDN)
    BRAND_LOGOS = {
        "현대": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Hyundai_Motor_Company_logo.svg/200px-Hyundai_Motor_Company_logo.svg.png",
        "기아": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Kia-logo.svg/200px-Kia-logo.svg.png",
        "제네시스": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Genesis_Logo.svg/200px-Genesis_Logo.svg.png",
        "쉐보레": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Chevrolet-logo-2011-.svg/200px-Chevrolet-logo-2011-.svg.png",
        "르노삼성": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Renault_Samsung_Motors.svg/200px-Renault_Samsung_Motors.svg.png",
        "르노코리아": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Renault_Samsung_Motors.svg/200px-Renault_Samsung_Motors.svg.png",
        "쌍용": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/SsangYong_logo.svg/200px-SsangYong_logo.svg.png",
        "KG모빌리티": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/SsangYong_logo.svg/200px-SsangYong_logo.svg.png",
        "BMW": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/BMW.svg/200px-BMW.svg.png",
        "벤츠": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Mercedes-Logo.svg/200px-Mercedes-Logo.svg.png",
        "메르세데스-벤츠": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Mercedes-Logo.svg/200px-Mercedes-Logo.svg.png",
        "아우디": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Audi-Logo_2016.svg/200px-Audi-Logo_2016.svg.png",
        "폭스바겐": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Volkswagen_logo_2019.svg/200px-Volkswagen_logo_2019.svg.png",
        "볼보": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Volvo_logo.svg/200px-Volvo_logo.svg.png",
        "렉서스": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Lexus_division_emblem.svg/200px-Lexus_division_emblem.svg.png",
        "토요타": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Toyota.svg/200px-Toyota.svg.png",
        "혼다": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Honda.svg/200px-Honda.svg.png",
        "포르쉐": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Porsche_logo.svg/200px-Porsche_logo.svg.png",
        "재규어": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Jaguar_2012_logo.svg/200px-Jaguar_2012_logo.svg.png",
        "랜드로버": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Land_Rover_logo.svg/200px-Land_Rover_logo.svg.png",
        "미니": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Mini_logo.svg/200px-Mini_logo.svg.png",
        "테슬라": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Tesla_Motors.svg/200px-Tesla_Motors.svg.png",
        "지프": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Jeep_logo.svg/200px-Jeep_logo.svg.png",
        "포드": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Ford_Motor_Company_Logo.svg/200px-Ford_Motor_Company_Logo.svg.png",
    }
    
    # 전체 차량 이미지 매핑 (235개 - 로컬 이미지 파일)
    MODEL_IMAGES = {
        # === 국산차 (PNG) ===
        # 기아
        "K3": "/car-images/K3.png",
        "K5": "/car-images/K5.png",
        "K7": "/car-images/K7.png",
        "K8": "/car-images/K8.png",
        "K9": "/car-images/K9.png",
        "EV3": "/car-images/EV3.png",
        "EV4": "/car-images/EV4.png",
        "EV5": "/car-images/EV5.png",
        "EV6": "/car-images/EV6.png",
        "EV9": "/car-images/EV9.png",
        "PV5": "/car-images/PV5.png",
        "모닝": "/car-images/모닝.png",
        "레이": "/car-images/레이.png",
        "니로": "/car-images/니로.png",
        "셀토스": "/car-images/셀토스.png",
        "쏘렌토": "/car-images/쏘렌토.png",
        "스토닉": "/car-images/스토닉.png",
        "쏘울": "/car-images/쏘울.png",
        "스팅어": "/car-images/스팅어.png",
        "포르테": "/car-images/포르테.png",
        "카렌스": "/car-images/카렌스.png",
        "프라이드": "/car-images/프라이드.png",
        "스펙트라": "/car-images/스펙트라.png",
        "엔터프라이즈": "/car-images/엔터프라이즈.png",
        "타스만": "/car-images/타스만.png",
        "카스타": "/car-images/카스타.png",
        "엘란": "/car-images/엘란.png",
        "비스토": "/car-images/비스토.png",
        "캐피탈": "/car-images/캐피탈.png",
        "그랜드 카니발": "/car-images/그랜드 카니발.png",
        "카니발 II": "/car-images/카니발 II.png",
        # 현대
        "그랜저": "/car-images/그랜저.png",
        "쏘나타": "/car-images/쏘나타.png",
        "아반떼": "/car-images/아반떼.png",
        "투싼": "/car-images/투싼.png",
        "싼타페": "/car-images/싼타페.png",
        "스타리아": "/car-images/스타리아.png",
        "스타렉스": "/car-images/스타렉스.png",
        "아이오닉": "/car-images/아이오닉.png",
        "베리타스": "/car-images/베리타스.png",
        "슈퍼살롱": "/car-images/슈퍼살롱.png",
        "뉴 다마스": "/car-images/뉴 다마스.png",
        "다마스 II": "/car-images/다마스 II.png",
        "라보": "/car-images/라보.png",
        "포텐샤": "/car-images/포텐샤.png",
        "에스페로": "/car-images/에스페로.png",
        "스테이츠맨": "/car-images/스테이츠맨.png",
        # 제네시스
        "G70": "/car-images/G70.png",
        "G80": "/car-images/G80.png",
        "G90": "/car-images/G90.png",
        "G2X": "/car-images/G2X.png",
        "GV60": "/car-images/GV60.png",
        "GV70": "/car-images/GV70.png",
        "GV80": "/car-images/GV80.png",
        # 르노코리아
        "SM3": "/car-images/SM3.png",
        "SM5": "/car-images/SM5.png",
        "SM6": "/car-images/SM6.png",
        "SM7": "/car-images/SM7.png",
        "QM3": "/car-images/QM3.png",
        "QM5": "/car-images/QM5.png",
        "QM6": "/car-images/QM6.png",
        "XM3": "/car-images/XM3.png",
        "클리오": "/car-images/클리오.png",
        "조에": "/car-images/조에.png",
        "캡처": "/car-images/캡처.png",
        "마스터": "/car-images/마스터.png",
        "그랑 콜레오스": "/car-images/그랑 콜레오스.png",
        "아르카나": "/car-images/아르카나.png",
        # 쉐보레/GM
        "스파크": "/car-images/스파크.png",
        "크루즈": "/car-images/크루즈.png",
        "말리부": "/car-images/말리부.png",
        "임팔라": "/car-images/임팔라.png",
        "트랙스": "/car-images/트랙스.png",
        "이쿼녹스": "/car-images/이쿼녹스.png",
        "트래버스": "/car-images/트래버스.png",
        "볼트": "/car-images/볼트.png",
        "캡티바": "/car-images/캡티바.png",
        "울란도": "/car-images/울란도.png",
        "토스카": "/car-images/토스카.png",
        "콜로라도": "/car-images/콜로라도.png",
        "타호": "/car-images/타호.png",
        "아카디아": "/car-images/아카디아.png",
        "카마로": "/car-images/카마로.png",
        "라세티 프리미어": "/car-images/라세티 프리미어.png",
        "젠트라": "/car-images/젠트라.png",
        "알페온": "/car-images/알페온.png",
        "마티즈 클래식": "/car-images/마티즈 클래식.png",
        "아베오 세단": "/car-images/아베오 세단.png",
        "아베오 해치백": "/car-images/아베오 해치백.png",
        "윈스톰": "/car-images/윈스톰.png",
        "크레도스": "/car-images/크레도스.png",
        "리갈": "/car-images/리갈.png",
        # 쌍용/KG
        "티볼리": "/car-images/티볼리.png",
        "토레스": "/car-images/토레스.png",
        "모하비": "/car-images/모하비.png",
        "액티언": "/car-images/액티언.png",
        "더 뉴 티볼리": "/car-images/더 뉴 티볼리.png",
        "더 뉴 토레스": "/car-images/더 뉴 토레스.png",
        "티볼리 에어": "/car-images/티볼리 에어.png",
        "코란도 C": "/car-images/코란도 C.png",
        "뷰티풀 코란도": "/car-images/뷰티풀 코란도.png",
        "더 뉴 코란도 스포츠": "/car-images/더 뉴 코란도 스포츠.png",
        "렉스턴 II": "/car-images/렉스턴 II.png",
        "더 뉴 렉스턴 스포츠": "/car-images/더 뉴 렉스턴 스포츠.png",
        "렉스턴 스포츠 칸": "/car-images/렉스턴 스포츠 칸.png",
        "뉴무쏘": "/car-images/뉴무쏘.png",
        "뉴체어맨": "/car-images/뉴체어맨.png",
        "로디우스 유로": "/car-images/로디우스 유로.png",
        "이스타나": "/car-images/이스타나.png",
        # 기타 국산
        "로체": "/car-images/로체.png",
        "티코": "/car-images/티코.png",
        "프레지오": "/car-images/프레지오.png",
        "파크타운": "/car-images/파크타운.png",
        
        # === 외제차 (PNG) ===
        # 포르쉐
        "911": "/car-images/911.png",
        "박스터": "/car-images/박스터.png",
        "카이맨": "/car-images/카이맨.png",
        "카이엔": "/car-images/카이엔.png",
        "마칸": "/car-images/마칸.png",
        "파나메라": "/car-images/파나메라.png",
        "타이칸": "/car-images/타이칸.png",
        # 메르세데스-벤츠
        "A-클래스": "/car-images/A-클래스.png",
        "C-클래스": "/car-images/C-클래스.png",
        "E-클래스": "/car-images/E-클래스.png",
        "S-클래스": "/car-images/S-클래스.png",
        "GLC": "/car-images/GLC.png",
        "GLE": "/car-images/GLE.png",
        "GLS": "/car-images/GLS.png",
        "AMG GT": "/car-images/AMG GT.png",
        # BMW
        "BMW 3시리즈": "/car-images/BMW 3시리즈.png",
        "BMW 5시리즈": "/car-images/BMW 5시리즈.png",
        "BMW 7시리즈": "/car-images/BMW 7시리즈.png",
        "X3": "/car-images/X3.png",
        "X5": "/car-images/X5.png",
        "X6": "/car-images/X6.png",
        "X7": "/car-images/X7.png",
        "i3": "/car-images/i3.png",
        "i4": "/car-images/i4.png",
        "i5": "/car-images/i5.png",
        "i7": "/car-images/i7.png",
        "iX1": "/car-images/iX1.png",
        "iX3": "/car-images/iX3.png",
        # 아우디
        "A4": "/car-images/A4.png",
        "A6": "/car-images/A6.png",
        "A7": "/car-images/A7.png",
        "A8": "/car-images/A8.png",
        "Q5": "/car-images/Q5.png",
        "Q7": "/car-images/Q7.png",
        "Q8": "/car-images/Q8.png",
        "E-트론": "/car-images/E-트론.png",
        # 렉서스
        "ES": "/car-images/ES.png",
        "LM": "/car-images/LM.png",
        "NX": "/car-images/NX.png",
        "RX": "/car-images/RX.png",
        "UX": "/car-images/UX.png",
        # 재규어
        "F-PACE": "/car-images/F-PACE.png",
        "F-TYPE": "/car-images/F-TYPE.png",
        "XE": "/car-images/XE.png",
        "XF": "/car-images/XF.png",
        "XJ": "/car-images/XJ.png",
        # 랜드로버
        "디스커버리": "/car-images/디스커버리.png",
        "디펜더": "/car-images/디펜더.png",
        "레인지로버": "/car-images/레인지로버.png",
        "벨라": "/car-images/벨라.png",
        "이보크": "/car-images/이보크.png",
        # 볼보
        "S90": "/car-images/S90.png",
        "V60": "/car-images/V60.png",
        "XC40": "/car-images/XC40.png",
        "XC60": "/car-images/XC60.png",
        "XC90": "/car-images/XC90.png",
        # 폭스바겐
        "골프": "/car-images/골프.png",
        "아테온": "/car-images/아테온.png",
        "제타": "/car-images/제타.png",
        "티구안": "/car-images/티구안.png",
        "파사트": "/car-images/파사트.png",
        "ID": "/car-images/ID.png",
        # 토요타
        "캠리": "/car-images/캠리.png",
        "프리우스": "/car-images/프리우스.png",
        "시에나": "/car-images/시에나.png",
        "알파드": "/car-images/알파드.png",
        "RAV4": "/car-images/RAV4.png",
        # 혼다
        "시빅": "/car-images/시빅.png",
        "어코드": "/car-images/어코드.png",
        "오딧세이": "/car-images/오딧세이.png",
        "CR-V": "/car-images/CR-V.png",
        "파일럿": "/car-images/파일럿.png",
        # 닛산
        "알티마": "/car-images/알티마.png",
        "맥시마": "/car-images/맥시마.png",
        "무라노": "/car-images/무라노.png",
        "패스파인더": "/car-images/패스파인더.png",
        # 인피니티
        "Q30": "/car-images/Q30.png",
        "Q50": "/car-images/Q50.png",
        "QX60": "/car-images/QX60.png",
        # 미니
        "미니쿠퍼": "/car-images/미니쿠퍼.png",
        
        # === 럭셔리 브랜드 (JPG) ===
        # 람보르기니
        "람보르기니 아벤타도르": "/car-images/람보르기니 아벤타도르.jpg",
        "람보르기니 우라칸": "/car-images/람보르기니 우라칸.jpg",
        "람보르기니 우루스": "/car-images/람보르기니 우루스.jpg",
        # 롤스로이스
        "롤스로이스 고스트": "/car-images/롤스로이스 고스트.jpg",
        "롤스로이스 컬리넌": "/car-images/롤스로이스 컬리넌.jpg",
        "롤스로이스 팬텀": "/car-images/롤스로이스 팬텀.jpg",
        # 링컨
        "링컨 네비게이터": "/car-images/링컨 네비게이터.jpg",
        "링컨 노틸러스": "/car-images/링컨 노틸러스.jpg",
        "링컨 에비에이터": "/car-images/링컨 에비에이터.jpg",
        # 마세라티
        "마세라티 기블리": "/car-images/마세라티 기블리.jpg",
        "마세라티 르반떼": "/car-images/마세라티 르반떼.jpg",
        "마세라티 콰트로포르테": "/car-images/마세라티 콰트로포르테.jpg",
        # 벤틀리
        "벤틀리 벤테이가": "/car-images/벤틀리 벤테이가.jpg",
        "벤틀리 컨티넨탈 GT": "/car-images/벤틀리 컨티넨탈 GT.jpg",
        "벤틀리 플라잉스퍼": "/car-images/벤틀리 플라잉스퍼.jpg",
        # 지프
        "지프 그랜드 체로키": "/car-images/지프 그랜드 체로키.jpg",
        "지프 랭글러": "/car-images/지프 랭글러.jpg",
        "지프 레니게이드": "/car-images/지프 레니게이드.jpg",
        "지프 체로키": "/car-images/지프 체로키.jpg",
        # 캐딜락
        "캐딜락 CT6": "/car-images/캐딜락 CT6.jpg",
        "캐딜락 XT5": "/car-images/캐딜락 XT5.jpg",
        "캐딜락 에스컬레이드": "/car-images/캐딜락 에스컬레이드.jpg",
        # 테슬라
        "테슬라 모델3": "/car-images/테슬라 모델3.jpg",
        "모델3": "/car-images/테슬라 모델3.jpg",
        "Model 3": "/car-images/테슬라 모델3.jpg",
        "Model3": "/car-images/테슬라 모델3.jpg",
        "테슬라 모델S": "/car-images/테슬라 모델S.jpg",
        "모델S": "/car-images/테슬라 모델S.jpg",
        "Model S": "/car-images/테슬라 모델S.jpg",
        "ModelS": "/car-images/테슬라 모델S.jpg",
        "테슬라 모델X": "/car-images/테슬라 모델X.jpg",
        "모델X": "/car-images/테슬라 모델X.jpg",
        "Model X": "/car-images/테슬라 모델X.jpg",
        "ModelX": "/car-images/테슬라 모델X.jpg",
        "테슬라 모델Y": "/car-images/테슬라 모델Y.png",
        "모델Y": "/car-images/테슬라 모델Y.png",
        "Model Y": "/car-images/테슬라 모델Y.png",
        "ModelY": "/car-images/테슬라 모델Y.png",
        # 페라리
        "페라리 296": "/car-images/페라리 296.jpg",
        "페라리 488": "/car-images/페라리 488.jpg",
        "페라리 F8": "/car-images/페라리 F8.jpg",
        "페라리 SF90": "/car-images/페라리 SF90.jpg",
        "페라리 로마": "/car-images/페라리 로마.jpg",
        # 포드
        "포드 F150": "/car-images/포드 F150.jpg",
        "포드 머스탱": "/car-images/포드 머스탱.jpg",
        "포드 브롱코": "/car-images/포드 브롱코.jpg",
        "포드 익스플로러": "/car-images/포드 익스플로러.jpg",
        # 폴스타
        "폴스타2": "/car-images/폴스타2.jpg",
        "폴스타4": "/car-images/폴스타4.jpg",
        # 푸조
        "푸조 208": "/car-images/푸조 208.jpg",
        "푸조 3008": "/car-images/푸조 3008.jpg",
        "푸조 5008": "/car-images/푸조 5008.jpg",
        "푸조 508": "/car-images/푸조 508.jpg",
        # 피아트
        "피아트 500": "/car-images/피아트 500.jpg",
        
        # === 대체 매핑 (시리즈 → 대표 이미지) ===
        # 테슬라 (모든 모델 → 대표 이미지)
        "모델 3": "/car-images/테슬라 모델3.jpg",
        "모델 S": "/car-images/테슬라 모델S.jpg",
        "모델 X": "/car-images/테슬라 모델X.jpg",
        "모델 Y": "/car-images/테슬라 모델Y.png",
        "사이버트럭": "/car-images/테슬라 모델X.jpg",  # 대체
        
        # 아이오닉 시리즈 → 아이오닉 대표
        "아이오닉 일렉트릭": "/car-images/아이오닉.png",
        "아이오닉 하이브리드": "/car-images/아이오닉.png",
        "아이오닉5": "/car-images/아이오닉.png",
        "아이오닉6": "/car-images/아이오닉.png",
        "아이오닉9": "/car-images/아이오닉.png",
        "더 뉴 아이오닉 일렉트릭": "/car-images/아이오닉.png",
        "더 뉴 아이오닉 하이브리드": "/car-images/아이오닉.png",
        "더 뉴 아이오닉5": "/car-images/아이오닉.png",
        
        # 쏘울 시리즈 → 쏘울 대표
        "쏘울 EV": "/car-images/쏘울.png",
        "쏘울 부스터": "/car-images/쏘울.png",
        "쏘울 부스터 EV": "/car-images/쏘울.png",
        "올 뉴 쏘울": "/car-images/쏘울.png",
        "더 뉴 쏘울": "/car-images/쏘울.png",
        
        # 미니 쿠퍼 시리즈 → 미니쿠퍼 대표
        "쿠퍼": "/car-images/미니쿠퍼.png",
        "쿠퍼 S": "/car-images/미니쿠퍼.png",
        "쿠퍼 D": "/car-images/미니쿠퍼.png",
        "쿠퍼 SD": "/car-images/미니쿠퍼.png",
        "쿠퍼 일렉트릭": "/car-images/미니쿠퍼.png",
        "쿠퍼 컨버터블": "/car-images/미니쿠퍼.png",
        "쿠퍼 컨트리맨": "/car-images/미니쿠퍼.png",
        "쿠퍼 클럽맨": "/car-images/미니쿠퍼.png",
        "쿠퍼 쿠페": "/car-images/미니쿠퍼.png",
        "쿠퍼 로드스터": "/car-images/미니쿠퍼.png",
        "쿠퍼 C 4세대": "/car-images/미니쿠퍼.png",
        "쿠퍼 S 4세대": "/car-images/미니쿠퍼.png",
        "쿠퍼 S 로드스터": "/car-images/미니쿠퍼.png",
        "쿠퍼 S 컨버터블": "/car-images/미니쿠퍼.png",
        "쿠퍼 S 컨버터블 4세대": "/car-images/미니쿠퍼.png",
        "쿠퍼 S 컨트리맨": "/car-images/미니쿠퍼.png",
        "쿠퍼 S 컨트리맨 3세대": "/car-images/미니쿠퍼.png",
        "쿠퍼 S 쿠페": "/car-images/미니쿠퍼.png",
        "쿠퍼 S 클럽맨": "/car-images/미니쿠퍼.png",
        "쿠퍼 D 컨트리맨": "/car-images/미니쿠퍼.png",
        "쿠퍼 D 클럽맨": "/car-images/미니쿠퍼.png",
        "쿠퍼 D 페이스맨": "/car-images/미니쿠퍼.png",
        "쿠퍼 SD 컨트리맨": "/car-images/미니쿠퍼.png",
        "쿠퍼 SD 클럽맨": "/car-images/미니쿠퍼.png",
        "쿠퍼 SD 페이스맨": "/car-images/미니쿠퍼.png",
        "쿠퍼 일렉트릭 4세대": "/car-images/미니쿠퍼.png",
        "쿠퍼 컨트리맨 일렉트릭 3세대": "/car-images/미니쿠퍼.png",
        
        # 람보르기니 시리즈 → 대표
        "아벤타도르": "/car-images/람보르기니 아벤타도르.jpg",
        "우라칸": "/car-images/람보르기니 우라칸.jpg",
        "우루스": "/car-images/람보르기니 우루스.jpg",
        "가야르도": "/car-images/람보르기니 우라칸.jpg",
        
        # 롤스로이스 시리즈 → 대표
        "고스트": "/car-images/롤스로이스 고스트.jpg",
        "고스트 2세대": "/car-images/롤스로이스 고스트.jpg",
        "팬텀": "/car-images/롤스로이스 팬텀.jpg",
        "컬리넌": "/car-images/롤스로이스 컬리넌.jpg",
        "던": "/car-images/롤스로이스 고스트.jpg",
        "스펙터": "/car-images/롤스로이스 고스트.jpg",
        
        # 벤틀리 시리즈 → 대표
        "벤테이가": "/car-images/벤틀리 벤테이가.jpg",
        "플라잉스퍼 1세대": "/car-images/벤틀리 플라잉스퍼.jpg",
        "플라잉스퍼 2세대": "/car-images/벤틀리 플라잉스퍼.jpg",
        "플라잉스퍼 3세대": "/car-images/벤틀리 플라잉스퍼.jpg",
        "컨티넨탈 GT 1세대": "/car-images/벤틀리 컨티넨탈 GT.jpg",
        "컨티넨탈 GT 2세대": "/car-images/벤틀리 컨티넨탈 GT.jpg",
        "컨티넨탈 GT 3세대": "/car-images/벤틀리 컨티넨탈 GT.jpg",
        "뮬산": "/car-images/벤틀리 플라잉스퍼.jpg",
        
        # 마세라티 시리즈 → 대표
        "기블리": "/car-images/마세라티 기블리.jpg",
        "르반떼": "/car-images/마세라티 르반떼.jpg",
        "콰트로포르테": "/car-images/마세라티 콰트로포르테.jpg",
        "그란투리스모": "/car-images/마세라티 기블리.jpg",
        "그란카브리오": "/car-images/마세라티 기블리.jpg",
        "그레칼레": "/car-images/마세라티 르반떼.jpg",
        
        # 페라리 시리즈 → 대표
        "로마": "/car-images/페라리 로마.jpg",
        "296 GTB": "/car-images/페라리 296.jpg",
        "296 GTS": "/car-images/페라리 296.jpg",
        "488 GTB": "/car-images/페라리 488.jpg",
        "488 스파이더": "/car-images/페라리 488.jpg",
        "488 피스타": "/car-images/페라리 488.jpg",
        "F8 스파이더": "/car-images/페라리 F8.jpg",
        "F8 트리뷰토": "/car-images/페라리 F8.jpg",
        "SF90 스트라달레": "/car-images/페라리 SF90.jpg",
        "SF90 스파이더": "/car-images/페라리 SF90.jpg",
        "812 GTS": "/car-images/페라리 SF90.jpg",
        "812 슈퍼패스트": "/car-images/페라리 SF90.jpg",
        "포르토피노": "/car-images/페라리 로마.jpg",
        "푸로산게": "/car-images/페라리 SF90.jpg",
        "GTC4 루쏘": "/car-images/페라리 488.jpg",
        "458": "/car-images/페라리 488.jpg",
        "F430": "/car-images/페라리 488.jpg",
        "360": "/car-images/페라리 488.jpg",
        "F12 베를리네타": "/car-images/페라리 SF90.jpg",
        
        # 포드/미국차 시리즈 → 대표
        "머스탱": "/car-images/포드 머스탱.jpg",
        "머스탱 7세대": "/car-images/포드 머스탱.jpg",
        "익스플로러": "/car-images/포드 익스플로러.jpg",
        "익스플로러 6세대": "/car-images/포드 익스플로러.jpg",
        "브롱코 6세대": "/car-images/포드 브롱코.jpg",
        "F150": "/car-images/포드 F150.jpg",
        
        # 지프 시리즈 → 대표
        "그랜드 체로키": "/car-images/지프 그랜드 체로키.jpg",
        "그랜드 체로키(WL)": "/car-images/지프 그랜드 체로키.jpg",
        "랭글러 (JK)": "/car-images/지프 랭글러.jpg",
        "랭글러 (JL)": "/car-images/지프 랭글러.jpg",
        "랭글러 (TJ)": "/car-images/지프 랭글러.jpg",
        "랭글러 (YJ)": "/car-images/지프 랭글러.jpg",
        "레니게이드": "/car-images/지프 레니게이드.jpg",
        "체로키(KL)": "/car-images/지프 체로키.jpg",
        "컴패스": "/car-images/지프 레니게이드.jpg",
        "컴패스 2세대": "/car-images/지프 레니게이드.jpg",
        "글래디에이터 (JT)": "/car-images/지프 랭글러.jpg",
    }
    
    # 기본 이미지 (모델을 찾지 못한 경우)
    DEFAULT_CAR_IMAGE = "https://cdn-icons-png.flaticon.com/512/3774/3774278.png"
    DEFAULT_BRAND_LOGO = "https://cdn-icons-png.flaticon.com/512/3774/3774278.png"
    
    @classmethod
    def get_model_image(cls, brand: str, model: str) -> str:
        """모델별 이미지 URL 반환"""
        # 정확한 모델명 매치
        if model in cls.MODEL_IMAGES:
            return cls.MODEL_IMAGES[model]
        
        # 부분 매칭 시도
        for key, url in cls.MODEL_IMAGES.items():
            if key in model or model in key:
                return url
        
        # 브랜드 로고 반환
        return cls.get_brand_logo(brand)
    
    @classmethod
    def get_brand_logo(cls, brand: str) -> str:
        """브랜드 로고 URL 반환"""
        return cls.BRAND_LOGOS.get(brand, cls.DEFAULT_BRAND_LOGO)
    
    @classmethod
    def get_image_with_fallback(cls, brand: str, model: str, detail_url: str = None) -> Dict:
        """이미지 URL 및 폴백 정보 반환"""
        model_image = cls.get_model_image(brand, model)
        brand_logo = cls.get_brand_logo(brand)
        
        return {
            "model_image": model_image,
            "brand_logo": brand_logo,
            "has_real_image": model in cls.MODEL_IMAGES,
            "fallback_type": "model" if model in cls.MODEL_IMAGES else "brand"
        }
    
    @classmethod
    def add_model_image(cls, model: str, image_url: str):
        """새 모델 이미지 추가 (런타임)"""
        cls.MODEL_IMAGES[model] = image_url


# 싱글톤 인스턴스
car_image_service = CarImageService()
